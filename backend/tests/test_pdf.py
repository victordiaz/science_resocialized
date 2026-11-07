from app import pdf

from .conftest import make_pdf


def _words(tmp_path, lines):
    p = tmp_path / "x.pdf"
    p.write_bytes(make_pdf([lines]))
    return pdf.extract_pages(p)[0]["words"]


def test_extract_pages_normalized(tmp_path):
    p = tmp_path / "x.pdf"
    p.write_bytes(make_pdf([["Hello world"], ["Second page"]]))
    pages = pdf.extract_pages(p)
    assert [pg["number"] for pg in pages] == [1, 2]
    assert pages[0]["width"] == 600 and pages[0]["height"] == 800
    assert [w["text"] for w in pages[0]["words"]] == ["Hello", "world"]
    for w in pages[0]["words"]:
        assert 0 <= w["x0"] < w["x1"] <= 1 and 0 <= w["y0"] < w["y1"] <= 1
    # first word starts at x=72 of 600
    assert abs(pages[0]["words"][0]["x0"] - 72 / 600) < 0.01


def _w(texts):
    return [{"text": t, "x0": i * 0.1, "y0": 0.1, "x1": i * 0.1 + 0.08, "y1": 0.12, "block": 0, "line": 0} for i, t in enumerate(texts)]


def test_find_quote_normalizes():
    words = _w(["The", "\ufb01nal", "model,", "trained", "carefully."])  # \ufb01 = "fi" ligature
    assert pdf.find_quote(words, "the FINAL model trained") is not None
    assert pdf.find_quote(words, "final   model,  trained carefully") is not None
    assert pdf.find_quote(words, "not on the page") is None
    assert pdf.find_quote(words, "  ") is None


def test_find_quote_handles_line_end_hyphenation(tmp_path):
    words = _words(tmp_path, ["We propose the Trans-", "former architecture."])
    rects = pdf.find_quote(words, "the Transformer architecture")
    assert rects is not None and len(rects) == 2


def test_find_quote_multiline_returns_rect_per_line(tmp_path):
    words = _words(tmp_path, ["alpha beta gamma", "delta epsilon zeta"])
    rects = pdf.find_quote(words, "gamma delta epsilon")
    assert len(rects) == 2
    assert rects[0]["y1"] <= rects[1]["y0"] + 0.001


def test_anchor_rects_clamped():
    out = pdf.clamp_rects([{"x0": 1.4, "y0": 0.5, "x1": 0.2, "y1": -0.3}, {"x0": 0.3, "y0": 0.3, "x1": 0.3, "y1": 0.4}])
    assert out == [{"x0": 0.2, "y0": 0.0, "x1": 1.0, "y1": 0.5}]


def test_text_in_rects(tmp_path):
    words = _words(tmp_path, ["alpha beta", "gamma delta"])
    rects = pdf.find_quote(words, "gamma delta")
    assert pdf.text_in_rects(words, rects) == "gamma delta"


def test_render_png_region(tmp_path):
    p = tmp_path / "x.pdf"
    p.write_bytes(make_pdf([["Hello"]]))
    full = pdf.render_png(p, 1, dpi=72)
    part = pdf.render_png(p, 1, dpi=72, region={"x0": 0, "y0": 0, "x1": 0.5, "y1": 0.5})
    assert full.startswith(b"\x89PNG") and part.startswith(b"\x89PNG")
    assert len(part) < len(full)
