import os
import threading
from types import SimpleNamespace

import pymupdf as fitz
import pytest

os.environ["PAPER_REVIEW_SEED"] = "0"
os.environ["LOCAL_WORKER"] = "0"

from app import db, services  # noqa: E402
from app.agents import live, runner  # noqa: E402
from app.config import settings  # noqa: E402


def _no_real_claude():
    raise RuntimeError("tests must not call the real Anthropic API (use the fake_client fixture)")


@pytest.fixture(autouse=True)
def tmp_data(tmp_path, monkeypatch):
    from app import metadata

    monkeypatch.setattr(settings, "data_dir", tmp_path / "data")
    monkeypatch.setattr(settings, "seed", False)
    monkeypatch.setattr(live, "background", False)
    monkeypatch.setattr(metadata, "background", False)
    monkeypatch.setattr(runner, "client_factory", _no_real_claude)
    db.init_db()
    live.install()
    yield
    services.on_human_comment = None
    services.on_paper_created = None


def make_pdf(pages: list[list[str]]) -> bytes:
    """Each page is a list of text lines, drawn top-down."""
    doc = fitz.open()
    for lines in pages:
        page = doc.new_page(width=600, height=800)
        y = 72
        for line in lines:
            page.insert_text((72, y), line, fontsize=11)
            y += 18
    data = doc.tobytes()
    doc.close()
    return data


@pytest.fixture
def paper():
    data = make_pdf(
        [
            ["Attention mechanisms are powerful tools", "for sequence transduction in practice.", "We propose the Trans-", "former architecture."],
            ["Results show BLEU of 28.4 on WMT 2014.", "Training took 3.5 days on eight GPUs."],
        ]
    )
    return services.create_paper("test.pdf", data, title="Test Paper")


@pytest.fixture
def personas():
    a = services.create_persona("Skeptic", color="#f00", prompt="be skeptical")
    b = services.create_persona("Stats", color="#00f", prompt="check stats")
    return a, b


# ---------------------------------------------------------------- fake Claude

def tool_use(name, inp, id_=None):
    return SimpleNamespace(type="tool_use", id=id_ or f"tu_{name}_{threading.get_ident()}_{id(inp)}", name=name, input=inp)


def text(t):
    return SimpleNamespace(type="text", text=t)


def resp(*blocks, stop=None):
    has_tool = any(b.type == "tool_use" for b in blocks)
    return SimpleNamespace(content=list(blocks), stop_reason=stop or ("tool_use" if has_tool else "end_turn"))


class FakeClient:
    """script(persona_name, messages, call_index) -> response. Records every call."""

    def __init__(self, script):
        self.script = script
        self.calls = []
        self._lock = threading.Lock()
        self.messages = SimpleNamespace(create=self._create)
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        persona_name = kwargs["system"].split("# Persona: ", 1)[1].split("\n", 1)[0]
        with self._lock:
            idx = sum(1 for c in self.calls if c["persona"] == persona_name)
            self.calls.append({"persona": persona_name, "kwargs": kwargs})
        return self.script(persona_name, kwargs["messages"], idx)


@pytest.fixture
def fake_client(monkeypatch):
    holder = {}

    def install(script):
        client = FakeClient(script)
        monkeypatch.setattr(runner, "client_factory", lambda: client)
        holder["client"] = client
        return client

    return install
