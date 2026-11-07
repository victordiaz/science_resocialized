"""Request bodies for the HTTP API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class RectIn(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class AnchorIn(BaseModel):
    page: int | None = Field(None, description="1-based page; omit for a whole-paper comment")
    rects: list[RectIn] | None = Field(None, description="Boxes as page fractions (0..1, origin top-left)")
    quote: str | None = Field(None, description="Exact text on the page; server computes rects if none given")


class ThreadCreate(BaseModel):
    body: str
    anchor: AnchorIn | None = None


class ReplyCreate(BaseModel):
    body: str
    reply_to: str | None = Field(None, description="Comment id being answered")


class ThreadPatch(BaseModel):
    status: str


class PaperPatch(BaseModel):
    title: str | None = None
    authors: list[str] | None = None
    year: int | None = None
    venue: str | None = None
    abstract: str | None = None
    keywords: list[str] | None = None
    field: str | None = None
    doc_type: str | None = None
    arxiv_id: str | None = None
    doi: str | None = None


class PersonaCreate(BaseModel):
    name: str
    kind: str = "builtin"
    color: str = "#1F5FD6"
    prompt: str = ""
    model: str = "claude-sonnet-5-5"
    tagline: str = ""
    enabled: bool = True


class PersonaPatch(BaseModel):
    name: str | None = None
    kind: str | None = None
    color: str | None = None
    prompt: str | None = None
    model: str | None = None
    tagline: str | None = None
    enabled: bool | None = None


class RunCreate(BaseModel):
    persona_ids: list[str]
    rounds: int = Field(1, ge=0, le=5, description="Discussion rounds after the independent pass")
    include_initial: bool = Field(True, description="False = discussion-only run on existing comments")
