import json
import threading

from app import services
from app.agents import live, runner

from .conftest import resp, text, tool_use


def _first_user_text(messages):
    c = messages[0]["content"]
    return c if isinstance(c, str) else json.dumps(c)


def test_round0_visibility(paper, personas, fake_client):
    a, b = personas
    # Pre-existing: a human comment, an old comment by B, an old comment by A.
    services.create_thread(paper["id"], services.human_author("Ana"), "human note", None)
    services.create_thread(paper["id"], services.persona_author(b), "old stats note", None)
    services.create_thread(paper["id"], services.persona_author(a), "old skeptic note", None)

    seen = {}

    def script(name, messages, idx):
        if idx == 0:
            return resp(tool_use("list_threads", {}, id_=f"lt-{name}"))
        if idx == 1:
            seen[name] = messages[-1]["content"][0]["content"][0]["text"]
            return resp(text("done"))

    fake_client(script)
    run = runner.start_run(paper["id"], [a["id"], b["id"]], rounds=0, background=False)
    assert run["status"] == "completed"
    assert "human note" in seen["Skeptic"] and "old skeptic note" in seen["Skeptic"]
    assert "old stats note" not in seen["Skeptic"]
    assert "old stats note" in seen["Stats"] and "old skeptic note" not in seen["Stats"]


def test_round_snapshot(paper, personas, fake_client):
    """In round 1, personas see everything from round 0 but not each other's round-1 replies."""
    a, b = personas
    barrier = threading.Barrier(2, timeout=5)
    round1_views = {}

    def script(name, messages, idx):
        first = _first_user_text(messages)
        if "Discussion round" not in first:  # round 0
            if idx == 0:
                return resp(tool_use("create_comment", {"body": f"{name} r0 comment", "page": 2, "quote": "BLEU of 28.4"}, id_=f"c-{name}"))
            return resp(text("ok"))
        # round 1: reply, wait for the other, then list
        n = sum(1 for m in messages if m["role"] == "assistant")
        if n == 0:
            round1_views[name] = first
            t = services.list_threads(paper["id"])[0]
            return resp(tool_use("reply", {"thread_id": t["id"], "body": f"{name} r1 reply"}, id_=f"r-{name}"))
        if n == 1:
            barrier.wait()
            return resp(tool_use("list_threads", {}, id_=f"l-{name}"))
        round1_views[name + "_after"] = messages[-1]["content"][0]["content"][0]["text"]
        return resp(text("done"))

    fake_client(script)
    run = runner.start_run(paper["id"], [a["id"], b["id"]], rounds=1, background=False)
    assert run["status"] == "completed", run
    assert "Skeptic r0 comment" in round1_views["Stats"] and "Stats r0 comment" in round1_views["Skeptic"]
    # Own reply is newer than the snapshot too, so neither sees round-1 replies.
    assert "Stats r1 reply" not in round1_views["Skeptic_after"]
    assert "Skeptic r1 reply" not in round1_views["Stats_after"]
    assert {t["round"] for t in run["tasks"]} == {0, 1}
    assert all(t["status"] == "done" for t in run["tasks"])


def test_run_without_key_fails_cleanly(paper, personas, monkeypatch):
    def boom():
        raise RuntimeError("no credentials")

    monkeypatch.setattr(runner, "client_factory", boom)
    run = runner.start_run(paper["id"], [personas[0]["id"]], rounds=0, background=False)
    assert run["status"] == "failed"
    assert "no credentials" in run["error"]
    assert all(t["status"] == "failed" for t in run["tasks"])


def test_tool_error_is_returned_to_agent(paper, personas, fake_client):
    results = {}

    def script(name, messages, idx):
        if idx == 0:
            return resp(tool_use("create_comment", {"body": "x", "page": 1, "quote": "purple elephant"}, id_="bad"))
        results["r"] = messages[-1]["content"][0]
        return resp(text("ok"))

    fake_client(script)
    runner.start_run(paper["id"], [personas[0]["id"]], rounds=0, background=False)
    assert results["r"]["is_error"] is True and "quote not found" in results["r"]["content"]


def test_cancel_run(paper, personas, fake_client):
    started = threading.Event()
    release = threading.Event()

    def script(name, messages, idx):
        started.set()
        release.wait(5)
        return resp(tool_use("read_full_text", {}, id_=f"x{idx}"))

    fake_client(script)
    run = runner.start_run(paper["id"], [personas[0]["id"]], rounds=2, background=True)
    assert started.wait(5)
    runner.cancel_run(run["id"])
    release.set()
    for _ in range(100):
        r = runner.get_run(run["id"])
        if r["status"] not in ("queued", "running"):
            break
        threading.Event().wait(0.05)
    assert r["status"] == "cancelled"
    assert all(t["status"] in ("cancelled",) for t in r["tasks"])


def test_live_reply_targets(paper, personas, fake_client):
    a, b = personas
    ext = services.create_persona("Outside", kind="external")
    calls = []

    def script(name, messages, idx):
        calls.append(name)
        return resp(text(f"{name} answers"))

    fake_client(script)
    human = services.human_author("Ana")
    t = services.create_thread(paper["id"], services.persona_author(a), "persona root", None)
    assert calls == []  # agent comments never trigger agents

    services.add_reply(t["id"], human, "why?")
    assert calls == ["Skeptic"]
    thread = services.get_thread(t["id"])
    assert thread["comments"][-1]["author"]["name"] == "Skeptic"
    assert thread["comments"][-1]["body"] == "Skeptic answers"

    calls.clear()
    services.add_reply(t["id"], human, "what do you think @stats?")
    assert sorted(calls) == ["Skeptic", "Stats"]

    calls.clear()
    services.create_thread(paper["id"], human, "plain human note", None)
    services.create_thread(paper["id"], human, "hey @Outside and @nobody", None)
    assert calls == []

    calls.clear()
    t2 = services.create_thread(paper["id"], services.persona_author(ext), "external root", None)
    services.add_reply(t2["id"], human, "reply to external")
    assert calls == []


def test_live_reply_to_specific_comment(paper, personas, fake_client):
    a, b = personas
    calls = []
    fake_client(lambda name, m, i: (calls.append(name), resp(text("ans")))[1])
    t = services.create_thread(paper["id"], services.persona_author(a), "root", None)
    bc = services.add_reply(t["id"], services.persona_author(b), "stats reply")
    services.add_reply(t["id"], services.human_author("Ana"), "to stats", reply_to=bc["id"])
    assert calls == ["Stats"]
    assert live.slug("Methods Skeptic") == "methods-skeptic"


def test_model_call_uses_fallback_for_default_model(paper, personas, fake_client):
    client = fake_client(lambda name, m, i: resp(text("x")))
    runner.start_run(paper["id"], [personas[0]["id"]], rounds=0, background=False)
    kw = client.calls[0]["kwargs"]
    assert kw["model"] == "claude-sonnet-5-5"
    assert kw["fallbacks"] == "default" and kw["betas"] == ["server-side-fallback-2026-07-01"]


def test_run_records_activity_and_counts(paper, personas, fake_client):
    def script(name, messages, idx):
        if idx == 0:
            return resp(tool_use("create_comment", {"body": "c", "page": 2, "quote": "BLEU of 28.4"}, id_="c1"))
        if idx == 1:
            t = services.list_threads(paper["id"])[0]
            return resp(tool_use("reply", {"thread_id": t["id"], "body": "r"}, id_="r1"))
        if idx == 2:
            return resp(tool_use("view_page", {"page": 9}, id_="v1"))
        return resp(text("done"))

    fake_client(script)
    run = runner.start_run(paper["id"], [personas[0]["id"]], rounds=0, background=False)
    task = run["tasks"][0]
    assert (task["comment_count"], task["reply_count"], task["activity"]) == (1, 1, "Finished this round")
    calls = [(e["call"].split()[0], e["code"]) for e in reversed(run["events"])]
    assert calls == [("POST", 201), ("POST", 201), ("GET", 422)]
    assert run["number"] == 1
