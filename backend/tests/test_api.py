import pytest
from fastapi.testclient import TestClient

from app import services
from app.main import app

from .conftest import make_pdf


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def uploaded(client):
    data = make_pdf([["The quick brown fox", "jumps over the lazy dog."], ["Page two text."]])
    r = client.post("/api/papers", files={"file": ("p.pdf", data, "application/pdf")})
    assert r.status_code == 201, r.text
    return r.json()


def test_upload_and_meta(client, uploaded):
    assert uploaded["page_count"] == 2
    assert len(uploaded["pages"]) == 2
    r = client.get("/api/papers")
    assert [p["id"] for p in r.json()] == [uploaded["id"]]


def test_upload_rejects_non_pdf(client):
    r = client.post("/api/papers", files={"file": ("x.pdf", b"hello", "application/pdf")})
    assert r.status_code == 400


def test_page_text_and_image(client, uploaded):
    r = client.get(f"/api/papers/{uploaded['id']}/pages/1/text?layout=true")
    body = r.json()
    assert "quick brown fox" in body["text"]
    assert body["words"][0]["text"] == "The"
    assert len(body["lines"]) == 2
    img = client.get(f"/api/papers/{uploaded['id']}/pages/1/image?dpi=50")
    assert img.headers["content-type"] == "image/png"
    assert client.get(f"/api/papers/{uploaded['id']}/pages/9/image").status_code == 404
    full = client.get(f"/api/papers/{uploaded['id']}/text").text
    assert "=== Page 2 ===" in full


def test_create_thread_by_quote_and_rects(client, uploaded):
    pid = uploaded["id"]
    r = client.post(f"/api/papers/{pid}/threads", json={"body": "hi", "anchor": {"page": 1, "quote": "brown fox jumps"}})
    assert r.status_code == 201, r.text
    t = r.json()
    assert t["anchor"]["page"] == 1 and len(t["anchor"]["rects"]) == 2
    assert t["comments"][0]["author"]["type"] == "human"

    r = client.post(
        f"/api/papers/{pid}/threads",
        json={"body": "box", "anchor": {"page": 1, "rects": [{"x0": 0, "y0": 0, "x1": 1, "y1": 0.2}]}},
    )
    t2 = r.json()
    assert "quick" in t2["anchor"]["quote"]

    r = client.post(f"/api/papers/{pid}/threads", json={"body": "general"})
    assert r.json()["anchor"] is None


def test_create_thread_quote_not_found_422(client, uploaded):
    r = client.post(
        f"/api/papers/{uploaded['id']}/threads", json={"body": "x", "anchor": {"page": 1, "quote": "purple elephant"}}
    )
    assert r.status_code == 422
    assert "quote not found" in r.json()["detail"]


def test_reply_with_persona_key(client, uploaded):
    persona = services.create_persona("Ext", kind="external", color="#123456")
    pid = uploaded["id"]
    t = client.post(f"/api/papers/{pid}/threads", json={"body": "root"}, headers={"X-User-Name": "Ana"}).json()
    assert t["comments"][0]["author"]["name"] == "Ana"
    r = client.post(
        f"/api/threads/{t['id']}/replies",
        json={"body": "agent says", "reply_to": t["comments"][0]["id"]},
        headers={"Authorization": f"Bearer {persona['api_key']}"},
    )
    assert r.status_code == 201
    assert r.json()["author"] == {"type": "persona", "id": persona["id"], "name": "Ext", "color": "#123456"}
    bad = client.post(f"/api/threads/{t['id']}/replies", json={"body": "x"}, headers={"Authorization": "Bearer nope"})
    assert bad.status_code == 401


def test_thread_status_patch(client, uploaded):
    t = client.post(f"/api/papers/{uploaded['id']}/threads", json={"body": "root"}).json()
    r = client.patch(f"/api/threads/{t['id']}", json={"status": "resolved"})
    assert r.json()["status"] == "resolved"
    assert client.patch(f"/api/threads/{t['id']}", json={"status": "weird"}).status_code == 400
    assert client.get(f"/api/papers/{uploaded['id']}/threads?status=open").json() == []


def test_delete_persona_keeps_comments(client, uploaded):
    persona = services.create_persona("Gone", kind="external", color="#abcdef")
    r = client.post(
        f"/api/papers/{uploaded['id']}/threads",
        json={"body": "by persona"},
        headers={"Authorization": f"Bearer {persona['api_key']}"},
    )
    tid = r.json()["id"]
    assert client.delete(f"/api/personas/{persona['id']}").status_code == 204
    assert persona["id"] not in [p["id"] for p in client.get("/api/personas").json()]
    c = client.get(f"/api/threads/{tid}").json()["comments"][0]
    assert c["author"]["name"] == "Gone" and c["author"]["color"] == "#abcdef"
    # revoked key
    r = client.post(f"/api/threads/{tid}/replies", json={"body": "x"}, headers={"Authorization": f"Bearer {persona['api_key']}"})
    assert r.status_code == 401


def test_persona_crud(client):
    r = client.post("/api/personas", json={"name": "New", "prompt": "p"})
    p = r.json()
    assert p["api_key"].startswith("prk_") and p["model"] == "claude-sonnet-5-5"
    r = client.patch(f"/api/personas/{p['id']}", json={"prompt": "changed", "enabled": False})
    assert r.json()["prompt"] == "changed" and r.json()["enabled"] is False
    assert "api_key" not in client.get(f"/api/personas/{p['id']}").json()


def test_anchor_kind_and_paper_stats(client, uploaded):
    pid = uploaded["id"]
    box = client.post(f"/api/papers/{pid}/threads", json={"body": "b", "anchor": {"page": 1, "rects": [{"x0": 0, "y0": 0, "x1": 1, "y1": 0.2}]}}).json()
    sel = client.post(
        f"/api/papers/{pid}/threads",
        json={"body": "s", "anchor": {"page": 1, "rects": [{"x0": 0, "y0": 0, "x1": 1, "y1": 0.2}], "quote": "quick brown"}},
    ).json()
    quote = client.post(f"/api/papers/{pid}/threads", json={"body": "q", "anchor": {"page": 1, "quote": "lazy dog"}}).json()
    assert (box["anchor"]["kind"], sel["anchor"]["kind"], quote["anchor"]["kind"]) == ("box", "text", "text")
    client.patch(f"/api/threads/{box['id']}", json={"status": "resolved"})
    p = client.get("/api/papers").json()[0]
    assert (p["open_count"], p["resolved_count"], p["thread_count"]) == (2, 1, 3)
    assert [a["type"] for a in p["participants"]] == ["human"]
    assert p["last_run"] is None


def test_persona_tagline_and_usage(client, uploaded):
    persona = client.post("/api/personas", json={"name": "T", "kind": "external", "tagline": "checks things"}).json()
    client.post(f"/api/papers/{uploaded['id']}/threads", json={"body": "x"}, headers={"Authorization": f"Bearer {persona['api_key']}"})
    got = next(p for p in client.get("/api/personas").json() if p["id"] == persona["id"])
    assert got["tagline"] == "checks things"
    assert (got["comment_count"], got["paper_count"]) == (1, 1)


def test_comments_follow_persona_color_and_name(client, uploaded):
    persona = client.post("/api/personas", json={"name": "Old", "kind": "external", "color": "#111111"}).json()
    t = client.post(f"/api/papers/{uploaded['id']}/threads", json={"body": "x"}, headers={"Authorization": f"Bearer {persona['api_key']}"}).json()
    client.patch(f"/api/personas/{persona['id']}", json={"name": "New", "color": "#222222"})
    author = client.get(f"/api/threads/{t['id']}").json()["comments"][0]["author"]
    assert (author["name"], author["color"]) == ("New", "#222222")
    assert client.get("/api/papers").json()[0]["participants"][0]["color"] == "#222222"
    client.delete(f"/api/personas/{persona['id']}")
    author = client.get(f"/api/threads/{t['id']}").json()["comments"][0]["author"]
    assert (author["name"], author["color"]) == ("Old", "#111111")  # deleted: as written
