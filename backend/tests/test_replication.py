import base64
import importlib.util
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import services
from app.config import settings
from app.main import app
from app.replication import service

from .conftest import resp, text, tool_use

TOKEN = "test-worker-token"


@pytest.fixture(autouse=True)
def sync(monkeypatch):
    monkeypatch.setattr(service, "background", False)
    monkeypatch.setattr(settings, "worker_token", TOKEN)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


SPEC = "Train Method A on dataset D and report accuracy in the table below."
OUTCOME = "The paper reports 91.2% accuracy (Table 2, p.6)."


def extractor_and_checker(leak: bool):
    def script(name, messages, idx):
        if name == "Experiment Extractor":
            if idx == 0:
                return resp(tool_use("read_full_text", {}, id_="r"))
            if idx == 1:
                return resp(tool_use("submit_experiment", {"title": "Method A on D", "spec_markdown": SPEC, "outcome_markdown": OUTCOME}, id_="s"))
            return resp(text("done"))
        if name == "Leak Checker":
            if idx == 0:
                return resp(tool_use("submit_leak_check", {"leaks_found": leak, "notes": "leaks the score" if leak else "clean"}, id_="l"))
            return resp(text("ok"))
        # verifiers
        if idx == 0:
            return resp(tool_use("read_replication_file", {"path": "REPORT.md"}, id_="v1"))
        if idx == 1:
            seen = messages[-1]["content"][0]["content"][0]["text"]
            return resp(tool_use("submit_report", {"report_markdown": f"{name} checked. Saw: {seen[:40]}"}, id_="v2"))
        return resp(text("done"))

    return script


def test_extraction_stops_before_replication(paper, personas, fake_client):
    fake_client(extractor_and_checker(leak=False))
    exp = service.start_extraction(paper["id"])
    exp = service.get_experiment(exp["id"])
    assert exp["status"] == "ready" and exp["spec_md"] == SPEC and exp["outcome_md"] == OUTCOME
    assert exp["leak_found"] is False
    assert service.list_for_paper(paper["id"])[0]["replications"] == []  # waits for a person
    rep = service.queue_replication(exp["id"], [personas[0]["id"]], budget_usd=3)
    assert rep["status"] == "queued" and rep["spec_md"] == SPEC and rep["budget_usd"] == 3
    assert rep["verifier_ids"] == [personas[0]["id"]]


def test_leak_pauses_for_review(paper, personas, fake_client):
    fake_client(extractor_and_checker(leak=True))
    exp = service.start_extraction(paper["id"])
    exp = service.get_experiment(exp["id"])
    assert exp["status"] == "needs_review" and exp["leak_check_md"] == "leaks the score"
    assert service.list_for_paper(paper["id"])[0]["replications"] == []
    # a person edits the spec, then starts it
    exp = service.update_spec(exp["id"], spec_md="Fixed spec")
    assert exp["status"] == "ready" and exp["leak_found"] is None
    rep = service.queue_replication(exp["id"])
    assert rep["spec_md"] == "Fixed spec"


def test_extractor_must_submit(paper, fake_client):
    fake_client(lambda name, m, i: resp(text("I won't submit")))
    exp = service.start_extraction(paper["id"])
    exp = service.get_experiment(exp["id"])
    assert exp["status"] == "failed" and "without submitting" in exp["error"]


def test_worker_protocol_and_verification(client, paper, personas, fake_client):
    fake_client(extractor_and_checker(leak=False))
    a, b = personas
    exp = client.post(f"/api/papers/{paper['id']}/experiments").json()
    assert client.post(f"/api/experiments/{exp['id']}/replications", json={"verifier_ids": [a["id"], b["id"]]}).status_code == 201
    h = {"X-Worker-Token": TOKEN}

    assert client.post("/api/worker/claim", json={"worker": "w1"}).status_code == 401
    job = client.post("/api/worker/claim", json={"worker": "w1"}, headers=h).json()["job"]
    assert SPEC in job["task_md"] and OUTCOME not in json.dumps(job)  # blind
    assert "Do not try to find the original paper" in job["system_append"]
    assert client.post("/api/worker/claim", json={"worker": "w2"}, headers=h).json()["job"] is None

    rid = job["replication_id"]
    r = client.post(f"/api/worker/replications/{rid}/events", json={"events": [{"kind": "tool", "text": "Bash: python train.py"}], "workdir": "/tmp/x"}, headers=h)
    assert r.json() == {"cancel": False}
    rep = client.get(f"/api/replications/{rid}?events_after=0").json()
    assert rep["status"] == "running" and rep["worker"] == "w1"
    assert [e["text"] for e in rep["events"]][-1] == "Bash: python train.py"

    files = [
        {"path": "REPORT.md", "content_b64": base64.b64encode(b"# Report\nMeasured 88.0% accuracy.").decode()},
        {"path": "outputs/results.json", "content_b64": base64.b64encode(b'{"acc": 0.88}').decode()},
        {"path": "../escape.txt", "content_b64": base64.b64encode(b"nope").decode()},
    ]
    r = client.post(f"/api/worker/replications/{rid}/complete", json={"status": "done", "cost_usd": 1.25, "files": files[:2]}, headers=h)
    assert r.status_code == 200, r.text
    bad = client.post(f"/api/worker/replications/{rid}/complete", json={"status": "done", "files": files[2:]}, headers=h)
    assert bad.status_code == 400

    rep = client.get(f"/api/replications/{rid}").json()
    assert rep["status"] == "done" and rep["cost_usd"] == 1.25
    assert rep["report_md"].startswith("# Report")
    assert {f["path"] for f in rep["files"]} == {"REPORT.md", "outputs/results.json"}
    assert client.get(f"/api/replications/{rid}/files/outputs/results.json").json() == {"acc": 0.88}
    # verifiers ran automatically, one per persona, and read the report
    vs = rep["verifications"]
    assert sorted(v["persona_name"] for v in vs) == ["Skeptic", "Stats"]
    assert all(v["status"] == "done" and "Measured 88.0%" in v["report_md"] for v in vs)
    # reviewers can read it
    digest = service.summary_for_agents(paper["id"])
    assert "Measured 88.0% accuracy" in digest and "Verification by Skeptic" in digest


def test_cancel_running_job(client, paper, fake_client):
    fake_client(extractor_and_checker(leak=False))
    exp = service.start_extraction(paper["id"])
    service.queue_replication(exp["id"])
    h = {"X-Worker-Token": TOKEN}
    rid = client.post("/api/worker/claim", json={}, headers=h).json()["job"]["replication_id"]
    client.post(f"/api/replications/{rid}/cancel")
    assert client.post(f"/api/worker/replications/{rid}/events", json={"events": []}, headers=h).json() == {"cancel": True}
    client.post(f"/api/worker/replications/{rid}/complete", json={"status": "done", "files": []}, headers=h)
    assert client.get(f"/api/replications/{rid}").json()["status"] == "cancelled"


def test_external_persona_cannot_verify(paper, fake_client):
    fake_client(extractor_and_checker(leak=False))
    exp = service.start_extraction(paper["id"])
    ext = services.create_persona("Outside", kind="external")
    with pytest.raises(ValueError):
        service.queue_replication(exp["id"], [ext["id"]])


# ---------------------------------------------------------------- the standalone worker

def _load_worker():
    path = Path(__file__).resolve().parents[2] / "worker" / "replicate_worker.py"
    spec = importlib.util.spec_from_file_location("replicate_worker", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_worker_summarizes_stream_json():
    w = _load_worker()
    assert w.summarize({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": "python train.py"}}]}}) == [
        {"kind": "tool", "text": "Bash: python train.py"}
    ]
    out = w.summarize({"type": "result", "subtype": "success", "total_cost_usd": 1.5, "duration_ms": 120000, "num_turns": 7})
    assert out == [{"kind": "result", "text": "Claude Code success, $1.50, 2.0 min, 7 turns"}]


def test_worker_collects_report_outputs_and_code(tmp_path):
    w = _load_worker()
    (tmp_path / "REPORT.md").write_text("r")
    (tmp_path / "outputs").mkdir()
    (tmp_path / "outputs" / "plot.png").write_bytes(b"\x89PNG")
    (tmp_path / "train.py").write_text("print(1)")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "x.py").write_text("skip")
    (tmp_path / "model.bin").write_bytes(b"\x00" * 10)
    paths = [f["path"] for f in w.collect_files(tmp_path)]
    assert paths == ["REPORT.md", "outputs/plot.png", "train.py"]


# ---------------------------------------------------------------- attachments

def _ready_experiment(paper, fake_client):
    fake_client(extractor_and_checker(leak=False))
    return service.start_extraction(paper["id"])


def test_attachments_flow(client, paper, personas, fake_client):
    exp = _ready_experiment(paper, fake_client)
    r = client.post(
        f"/api/experiments/{exp['id']}/attachments",
        files=[("files", ("train.csv", b"x,y\n1,2\n", "text/csv")), ("files", ("../../evil name.zip", b"PK\x03\x04", "application/zip"))],
        data={"note": "training data"},
    )
    assert r.status_code == 201, r.text
    a, b = r.json()
    assert (a["filename"], a["size"], a["note"]) == ("train.csv", 8, "training data")
    assert b["filename"] == "evil name.zip"  # path parts stripped
    dup = client.post(f"/api/experiments/{exp['id']}/attachments", files=[("files", ("train.csv", b"other", "text/csv"))]).json()[0]
    assert dup["filename"] == "train (2).csv"
    client.patch(f"/api/attachments/{b['id']}", json={"note": "archive of extras"})
    assert client.get(f"/api/attachments/{a['id']}/download").content == b"x,y\n1,2\n"

    rep = client.post(f"/api/experiments/{exp['id']}/replications", json={"verifier_ids": [personas[0]["id"]]}).json()
    assert len(rep["attachment_ids"]) == 3
    h = {"X-Worker-Token": TOKEN}
    job = client.post("/api/worker/claim", json={}, headers=h).json()["job"]
    assert "## Provided files" in job["task_md"] and "`inputs/train.csv` (8 bytes): training data" in job["task_md"]
    assert "archive of extras" in job["task_md"]
    url = job["attachments"][0]["url"]
    assert client.get(url).status_code == 401
    assert client.get(url, headers=h).content == b"x,y\n1,2\n"

    # deleting a file later doesn't break the record of a run that used it
    client.delete(f"/api/attachments/{dup['id']}")
    assert len(client.get(f"/api/replications/{rep['id']}").json()["attachments"]) == 2
    assert len(client.get(f"/api/experiments/{exp['id']}/attachments").json()) == 2


def test_attachment_size_limit(client, paper, fake_client, monkeypatch):
    exp = _ready_experiment(paper, fake_client)
    monkeypatch.setattr(settings, "attachment_max_mb", 1)
    r = client.post(f"/api/experiments/{exp['id']}/attachments", files=[("files", ("big.bin", b"0" * (1024 * 1024 + 1), "application/octet-stream"))])
    assert r.status_code == 400 and "larger than 1 MB" in r.json()["detail"]
    assert client.get(f"/api/experiments/{exp['id']}/attachments").json() == []


def test_verifier_can_read_provided_files(paper, personas, fake_client):
    import io

    exp = _ready_experiment(paper, fake_client)
    service.save_attachment(exp["id"], "notes.txt", io.BytesIO(b"use column y"), "text/plain")
    seen = {}

    def script(name, messages, idx):
        if idx == 0:
            return resp(tool_use("read_replication_file", {"path": "inputs/notes.txt"}, id_="a"))
        if idx == 1:
            seen["text"] = messages[-1]["content"][0]["content"][0]["text"]
            seen["task"] = messages[0]["content"]
            return resp(tool_use("submit_report", {"report_markdown": "ok"}, id_="b"))
        return resp(text("done"))

    rep = service.queue_replication(exp["id"])
    service.claim_job("w")
    fake_client(script)
    service.complete_job(rep["id"], "done", "# r", None, None, [])
    service.start_verifications(rep["id"], [personas[0]["id"]])
    assert seen["text"] == "use column y"
    assert "`inputs/notes.txt`" in seen["task"]


def test_worker_fetches_and_reuses_inputs(tmp_path):
    import hashlib

    w = _load_worker()
    data = b"a,b\n1,2\n"
    calls = []

    class FakeApi:
        def download(self, path, dest):
            calls.append(path)
            dest.write_bytes(data)

    job = {"attachments": [{"id": "att_1", "filename": "d.csv", "size": len(data), "sha256": hashlib.sha256(data).hexdigest(), "url": "/api/worker/attachments/att_1"}]}
    notes = []
    w.fetch_attachments(FakeApi(), job, tmp_path, notes.append)
    assert (tmp_path / "inputs" / "d.csv").read_bytes() == data and calls == ["/api/worker/attachments/att_1"]
    w.fetch_attachments(FakeApi(), job, tmp_path, notes.append)  # re-run: reused, not downloaded
    assert calls == ["/api/worker/attachments/att_1"] and "already here" in notes[-1]
    job["attachments"][0]["sha256"] = "0" * 64
    (tmp_path / "inputs" / "d.csv").unlink()
    with pytest.raises(RuntimeError, match="checksum"):
        w.fetch_attachments(FakeApi(), job, tmp_path, notes.append)
    # provided files are never uploaded back
    (tmp_path / "REPORT.md").write_text("r")
    (tmp_path / "inputs" / "x.csv").write_text("1")
    assert [f["path"] for f in w.collect_files(tmp_path)] == ["REPORT.md"]


def test_papers_list_replication_status(client, paper, personas, fake_client):
    assert services.list_papers()[0]["replication"]["status"] == "none"
    exp = _ready_experiment(paper, fake_client)
    assert services.list_papers()[0]["replication"]["status"] == "ready"
    rep = service.queue_replication(exp["id"], [personas[0]["id"]])
    assert services.list_papers()[0]["replication"]["status"] == "running"
    service.claim_job("w")
    report = "# R\n\n## Status: REPLICATED, matches within 1 point\n"
    files = [{"path": "REPORT.md", "content_b64": base64.b64encode(report.encode()).decode()}]
    service.complete_job(rep["id"], "done", report, 0.5, None, files)
    s = services.list_papers()[0]["replication"]
    assert s["status"] == "verified" and s["verdict"] == "REPLICATED, matches within 1 point" and s["runs"] == 1
