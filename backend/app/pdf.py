"""PDF processing with PyMuPDF.

All coordinates leaving this module are normalized to the page: 0..1, top-left origin.
"""
from __future__ import annotations

import unicodedata
from pathlib import Path
from typing import TypedDict

import pymupdf as fitz


class Rect(TypedDict):
    x0: float
    y0: float
    x1: float
    y1: float


class Word(TypedDict):
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    block: int
    line: int


class PageInfo(TypedDict):
    number: int
    width: float
    height: float
    text: str
    words: list[Word]


def _r(v: float) -> float:
    return round(min(1.0, max(0.0, v)), 5)


def extract_pages(path: str | Path) -> list[PageInfo]:
    pages: list[PageInfo] = []
    with fitz.open(path) as doc:
        for i, page in enumerate(doc):
            rect = page.rect
            w, h = rect.width, rect.height
            words: list[Word] = []
            for x0, y0, x1, y1, text, block, line, _wn in page.get_text("words", sort=True):
                words.append(
                    Word(
                        text=text,
                        x0=_r((x0 - rect.x0) / w),
                        y0=_r((y0 - rect.y0) / h),
                        x1=_r((x1 - rect.x0) / w),
                        y1=_r((y1 - rect.y0) / h),
                        block=int(block),
                        line=int(line),
                    )
                )
            pages.append(PageInfo(number=i + 1, width=w, height=h, text=page.get_text("text", sort=True), words=words))
    return pages


def pdf_title(path: str | Path, fallback: str) -> str:
    with fitz.open(path) as doc:
        title = (doc.metadata or {}).get("title") or ""
    return title.strip() or fallback


def render_png(path: str | Path, page: int, dpi: int = 110, region: Rect | None = None) -> bytes:
    """Render a 1-based page (optionally only a normalized region of it) to PNG."""
    with fitz.open(path) as doc:
        if page < 1 or page > doc.page_count:
            raise ValueError(f"page {page} out of range 1..{doc.page_count}")
        p = doc[page - 1]
        clip = None
        if region is not None:
            r = clamp_rects([region])[0]
            pr = p.rect
            clip = fitz.Rect(
                pr.x0 + r["x0"] * pr.width,
                pr.y0 + r["y0"] * pr.height,
                pr.x0 + r["x1"] * pr.width,
                pr.y0 + r["y1"] * pr.height,
            )
        pix = p.get_pixmap(dpi=dpi, clip=clip)
        return pix.tobytes("png")


def clamp_rects(rects: list[dict]) -> list[Rect]:
    """Clamp to 0..1, fix inverted corners, drop degenerate rects."""
    out: list[Rect] = []
    for r in rects:
        x0, x1 = sorted((float(r["x0"]), float(r["x1"])))
        y0, y1 = sorted((float(r["y0"]), float(r["y1"])))
        c = Rect(x0=_r(x0), y0=_r(y0), x1=_r(x1), y1=_r(y1))
        if c["x1"] - c["x0"] > 0.0005 and c["y1"] - c["y0"] > 0.0005:
            out.append(c)
    return out


def _norm_chars(s: str) -> str:
    """Lowercase alphanumerics only, after NFKC (expands ligatures like ﬁ)."""
    s = unicodedata.normalize("NFKC", s).lower()
    return "".join(ch for ch in s if ch.isalnum())


def _words_to_rects(words: list[Word], indices: list[int]) -> list[Rect]:
    """One rect per (block, line) group covering the given words."""
    groups: dict[tuple[int, int], Rect] = {}
    order: list[tuple[int, int]] = []
    for i in indices:
        w = words[i]
        key = (w["block"], w["line"])
        if key not in groups:
            groups[key] = Rect(x0=w["x0"], y0=w["y0"], x1=w["x1"], y1=w["y1"])
            order.append(key)
        else:
            g = groups[key]
            g["x0"], g["y0"] = min(g["x0"], w["x0"]), min(g["y0"], w["y0"])
            g["x1"], g["y1"] = max(g["x1"], w["x1"]), max(g["y1"], w["y1"])
    return [groups[k] for k in order]


def find_quote(words: list[Word], quote: str) -> list[Rect] | None:
    """Locate quote among page words, tolerant of case, whitespace, punctuation,
    ligatures and line-end hyphenation. Returns rects (one per line) or None."""
    target = _norm_chars(quote)
    if not target:
        return None
    stream: list[str] = []
    owner: list[int] = []
    for i, w in enumerate(words):
        for ch in _norm_chars(w["text"]):
            stream.append(ch)
            owner.append(i)
    hay = "".join(stream)
    pos = hay.find(target)
    if pos < 0:
        return None
    indices = sorted(set(owner[pos : pos + len(target)]))
    return _words_to_rects(words, indices)


def text_in_rects(words: list[Word], rects: list[Rect]) -> str:
    """Words whose center falls inside any rect, in reading order."""
    picked = []
    for w in words:
        cx, cy = (w["x0"] + w["x1"]) / 2, (w["y0"] + w["y1"]) / 2
        if any(r["x0"] <= cx <= r["x1"] and r["y0"] <= cy <= r["y1"] for r in rects):
            picked.append(w["text"])
    return " ".join(picked)


def page_lines(words: list[Word]) -> list[dict]:
    """Group words into lines with a bbox each — compact layout view for agents."""
    lines: dict[tuple[int, int], dict] = {}
    for w in words:
        key = (w["block"], w["line"])
        ln = lines.get(key)
        if ln is None:
            lines[key] = {"text": w["text"], "x0": w["x0"], "y0": w["y0"], "x1": w["x1"], "y1": w["y1"]}
        else:
            ln["text"] += " " + w["text"]
            ln["x0"], ln["y0"] = min(ln["x0"], w["x0"]), min(ln["y0"], w["y0"])
            ln["x1"], ln["y1"] = max(ln["x1"], w["x1"]), max(ln["y1"], w["y1"])
    return list(lines.values())
