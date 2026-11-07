"""Paper metadata extraction: title, authors, year, venue, abstract, keywords, field, ids.

Runs in the background after upload (and on request). A regex pass finds arXiv ids and
DOIs; Claude reads the first pages for the rest. A title a person set is kept.
"""
from __future__ import annotations

import logging
import re
import threading

from . import services
from .agents import runner
from .agents.tools import AgentContext, ToolError
from .config import settings
from .events import bus
from .services import Visibility

log = logging.getLogger("paper_review.metadata")

background = True  # False in tests

ARXIV_RE = re.compile(r"arXiv:\s*(\d{4}\.\d{4,5})(v\d+)?", re.I)
DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>]+[^\s\"<>.,;)\]])")
FIRST_PAGES_CHARS = 14000

DOC_TYPES = ["paper", "preprint", "thesis", "report", "book chapter", "slides", "other"]

SYSTEM = """# Persona: Metadata Extractor
You read the first pages of an uploaded document (usually a research paper) and record its
bibliographic details. Use only what the document shows; leave a field out rather than guess.
The PDF's own metadata and file name may be wrong (e.g. "report.html", "Microsoft Word - draft").
Title: the real title, in its original capitalization. Authors: full names in order, without
affiliations or footnote marks. Venue: the short common name of the journal, conference or
workshop if stated, without year or edition (e.g. "NeurIPS", "ACL", "Nature", "ICML Workshop on
X"; else omit; "arXiv" for arXiv-only preprints). Year: of publication or of this version.
Abstract: copied verbatim if present (else a 2-3 sentence neutral summary, marked as such by
starting with "Summary:"). Keywords: 3-8 topical keywords, lowercase. Field: one broad research
area, e.g. "machine learning", "natural language processing", "computer vision", "biology",
"physics", "economics". Call submit_metadata once."""

SUBMIT = {
    "name": "submit_metadata",
    "description": "Record the document's details. Omit any field the document doesn't show.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "authors": {"type": "array", "items": {"type": "string"}},
            "year": {"type": "integer"},
            "venue": {"type": "string"},
            "abstract": {"type": "string"},
            "keywords": {"type": "array", "items": {"type": "string"}},
            "field": {"type": "string"},
            "doc_type": {"type": "string", "enum": DOC_TYPES},
            "arxiv_id": {"type": "string"},
            "doi": {"type": "string"},
        },
        "required": ["title"],
        "additionalProperties": False,
    },
}


def find_ids(text: str) -> dict:
    out = {}
    m = ARXIV_RE.search(text)
    if m:
        out["arxiv_id"] = m.group(1) + (m.group(2) or "")
    m = DOI_RE.search(text)
    if m:
        out["doi"] = m.group(1)
    return out


def _first_pages(paper_id: str, paper: dict) -> str:
    chunks, total = [], 0
    for pg in paper["pages"][:3]:
        t = services.page_data(paper_id, pg["number"])["text"].strip()
        chunks.append(f"=== Page {pg['number']} ===\n{t}")
        total += len(t)
        if total > FIRST_PAGES_CHARS:
            break
    return "\n\n".join(chunks)[:FIRST_PAGES_CHARS]


def extract(paper_id: str) -> dict:
    """Extract and store metadata for one paper. Returns the updated paper."""
    paper = services.get_paper(paper_id)
    services.set_metadata_status(paper_id, "running")
    bus.publish(paper_id, {"type": "paper.updated", "paper_id": paper_id})
    try:
        text = _first_pages(paper_id, paper)
        ids = find_ids(text)
        got: dict = {}

        def executor(ctx, name, inp):
            if name != "submit_metadata":
                raise ToolError(f"unknown tool {name}")
            if not isinstance(inp.get("title"), str) or not inp["title"].strip():
                raise ToolError("`title` is required")
            got.update(inp)
            return [{"type": "text", "text": "Saved."}]

        persona = {"id": "system:metadata", "name": "Metadata Extractor", "color": "#495057", "model": settings.pipeline_model}
        ctx = AgentContext(paper_id=paper_id, persona=persona, visibility=Visibility())
        msg = (
            f"File name: {paper['filename']}\nTitle from the PDF's metadata: {paper['title']}\n"
            f"Pages: {paper['page_count']}\nIdentifiers found by pattern: {ids or 'none'}\n\n{text}"
        )
        runner.agent_loop(runner.client_factory(), ctx, msg, max_steps=3, system=SYSTEM, tools=[SUBMIT], executor=executor)
        if not got:
            raise RuntimeError("the extractor did not submit any details")
        fields = {**got, **{k: v for k, v in ids.items() if not got.get(k)}}
        if fields.get("year") and not (1500 < int(fields["year"]) < 2200):
            fields.pop("year")
        if paper["title_source"] == "user":
            fields.pop("title", None)
        services.update_paper(paper_id, source="metadata", **fields)
        services.set_metadata_status(paper_id, "done")
    except Exception as e:
        log.exception("metadata extraction for %s failed", paper_id)
        services.set_metadata_status(paper_id, "failed", runner._err_text(e))
    bus.publish(paper_id, {"type": "paper.updated", "paper_id": paper_id})
    return services.get_paper(paper_id)


def start(paper_id: str) -> None:
    services.set_metadata_status(paper_id, "pending")
    if background:
        threading.Thread(target=extract, args=(paper_id,), daemon=True).start()
    else:
        extract(paper_id)


def install() -> None:
    services.on_paper_created = start


def resume_unfinished() -> None:
    """After a restart, redo extractions that never finished."""
    for p in services.list_papers():
        if p["metadata_status"] in ("pending", "running"):
            start(p["id"])
