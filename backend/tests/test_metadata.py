import pytest

from app import metadata, services

from .conftest import make_pdf, resp, text, tool_use


@pytest.fixture(autouse=True)
def sync(monkeypatch):
    monkeypatch.setattr(metadata, "background", False)
    metadata.install()
    yield
    services.on_paper_created = None


def test_find_ids():
    t = "arXiv:1706.03762v7 [cs.CL] 2 Aug 2023 ... https://doi.org/10.1145/3292500.3330701."
    assert metadata.find_ids(t) == {"arxiv_id": "1706.03762v7", "doi": "10.1145/3292500.3330701"}


def _script(details):
    def script(name, messages, idx):
        assert name == "Metadata Extractor"
        if idx == 0:
            return resp(tool_use("submit_metadata", details, id_="m"))
        return resp(text("ok"))
    return script


def test_upload_extracts_metadata(fake_client):
    fake_client(_script({"title": "A Real Title", "authors": ["Ada Lovelace", "Alan Turing"], "year": 2024, "venue": "NeurIPS",
                         "keywords": ["attention", "translation"], "field": "machine learning", "doc_type": "paper"}))
    data = make_pdf([["A Real Title", "arXiv:2401.00001v2", "Ada Lovelace and Alan Turing"]])
    p = services.create_paper("report.html.pdf", data)
    assert p["metadata_status"] == "done"
    assert p["title"] == "A Real Title" and p["title_source"] == "metadata"
    assert p["authors"] == ["Ada Lovelace", "Alan Turing"] and p["year"] == 2024
    assert p["keywords"] == ["attention", "translation"] and p["field"] == "machine learning"
    assert p["arxiv_id"] == "2401.00001v2"  # from the pattern, since the model didn't give one
    listed = services.list_papers()[0]
    assert listed["authors"] == ["Ada Lovelace", "Alan Turing"] and listed["venue"] == "NeurIPS"


def test_user_title_is_kept(fake_client):
    fake_client(_script({"title": "Extracted", "year": 1999}))
    p = services.create_paper("x.pdf", make_pdf([["hello"]]), title="Mine")
    assert p["title"] == "Mine" and p["year"] == 1999
    services.update_paper(p["id"], title="Edited")
    p = metadata.extract(p["id"])
    assert p["title"] == "Edited" and p["title_source"] == "user"


def test_extraction_failure_is_recorded(fake_client):
    fake_client(lambda name, m, i: resp(text("no tool call")))
    p = services.create_paper("x.pdf", make_pdf([["hello"]]))
    assert p["metadata_status"] == "failed" and "did not submit" in p["metadata_error"]
