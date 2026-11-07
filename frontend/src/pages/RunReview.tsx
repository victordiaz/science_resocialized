import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../api";
import type { Paper, Persona, Run, RunTask } from "../types";
import { Avatar, Icon, clock, lighten, modelLabel, plural, runLabel, shortDate } from "../ui";

const ROUND_OPTIONS = [0, 1, 2, 3];

function roundsHelp(rounds: number, discussionOnly: boolean) {
  if (discussionOnly)
    return `Personas skip the solo review and discuss the comments already on the paper, ${rounds === 1 ? "once" : rounds + " times over"}.`;
  if (rounds === 0) return "Each persona reviews the paper on its own. Nobody sees anyone else’s comments.";
  return `Each persona first reviews on its own, then reads the others’ comments and replies${rounds === 1 ? " once." : ", " + rounds + " times over."}`;
}

const STATE: Record<RunTask["status"], { label: string; tone: "live" | "idle" | "bad" }> = {
  pending: { label: "Queued", tone: "idle" },
  running: { label: "Working", tone: "live" },
  done: { label: "Done", tone: "idle" },
  failed: { label: "Failed", tone: "bad" },
  cancelled: { label: "Stopped", tone: "idle" },
};

function liveLabel(activity: string | null): string {
  if (!activity) return "Working";
  if (activity.startsWith("Replying")) return "Replying";
  if (activity.startsWith("Writing")) return "Commenting";
  if (activity.startsWith("Looking")) return "Looking";
  return "Reading";
}

function RunCard({ run, onStop }: { run: Run; onStop: () => void }) {
  const active = run.status === "running" || run.status === "queued";
  const rounds = [...new Set(run.tasks.map((t) => t.round))].sort((a, b) => a - b);
  const personaIds = [...new Set(run.tasks.map((t) => t.persona_id))];
  const statusText = { queued: "Starting", running: "Running", completed: "Finished", failed: "Failed", cancelled: "Stopped" }[run.status];

  return (
    <div className="card run-card">
      <div className="run-head">
        <h2>Run {run.number}</h2>
        <span className={`pill ${active ? "live" : run.status === "failed" ? "bad" : "idle"}`}>
          {active && <span className="dot" aria-hidden />}
          {statusText}
        </span>
        <span className="muted small">
          Started {clock(run.created_at)}{new Date(run.created_at).toDateString() !== new Date().toDateString() ? `, ${shortDate(run.created_at)}` : ""} ·{" "}
          {runLabel({ persona_count: personaIds.length, rounds: run.rounds, include_initial: run.include_initial })}
        </span>
        <span className="spacer" />
        {active && <button className="btn" onClick={onStop}>Stop run</button>}
      </div>
      {run.error && <p className="error small">{run.error}</p>}

      <ol className="stages" aria-label="Run stages" style={{ gridTemplateColumns: `repeat(${rounds.length}, minmax(0, 1fr))` }}>
        {rounds.map((r) => {
          const ts = run.tasks.filter((t) => t.round === r);
          const finished = ts.filter((t) => t.status === "done" || t.status === "failed" || t.status === "cancelled").length;
          const running = ts.some((t) => t.status === "running");
          const allDone = finished === ts.length;
          const made = ts.reduce((n, t) => n + t.comment_count, 0);
          const replied = ts.reduce((n, t) => n + t.reply_count, 0);
          const failed = ts.filter((t) => t.status === "failed").length;
          let sub = "Queued";
          if (allDone)
            sub = ts.every((t) => t.status === "cancelled")
              ? "Stopped"
              : `Done · ${r === 0 ? plural(made, "comment") : plural(replied, "reply", "replies")}${failed ? ` · ${failed} failed` : ""}`;
          else if (running) sub = r === 0 ? "Reading the paper" : "Reading each other’s comments";
          return (
            <li key={r} aria-current={running ? "step" : undefined}>
              <span className="track"><span style={{ width: `${(finished / ts.length) * 100}%`, background: allDone ? "var(--ink)" : "var(--accent)" }} /></span>
              <span className={`stage-name${!running && !allDone ? " muted" : ""}`}>{r === 0 ? "Solo review" : `Discussion ${r}`}</span>
              <span className="muted small">{sub}</span>
            </li>
          );
        })}
      </ol>

      <div className="lanes">
        {personaIds.map((pid) => {
          const ts = run.tasks.filter((t) => t.persona_id === pid);
          const current =
            ts.find((t) => t.status === "running") ?? ts.find((t) => t.round === run.current_round) ?? ts[ts.length - 1];
          const comments = ts.reduce((n, t) => n + t.comment_count, 0);
          const replies = ts.reduce((n, t) => n + t.reply_count, 0);
          const failed = ts.find((t) => t.status === "failed");
          let state = STATE[current.status];
          if (current.status === "running") state = { label: liveLabel(current.activity), tone: "live" };
          if (current.status === "done" && active) state = { label: "Waiting", tone: "idle" };
          let doing = current.activity ?? (current.status === "pending" ? `Waiting for ${current.round === 0 ? "the solo review" : `discussion ${current.round}`}` : "");
          if (failed) doing = failed.error ?? "Failed";
          return (
            <div key={pid} className="lane">
              <Avatar name={ts[0].persona_name} color={ts[0].persona_color} size={32} />
              <div className="lane-main">
                <span className="strong">{ts[0].persona_name}</span>
                <span className={`small${failed ? " error-text" : ""}`}>{doing}</span>
              </div>
              <span className="muted small nowrap num">{plural(comments, "comment")} · {plural(replies, "reply", "replies")}</span>
              <span className={`pill ${failed ? "bad" : state.tone}`}>{failed ? "Failed" : state.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Activity({ run }: { run: Run }) {
  const events = run.events ?? [];
  return (
    <div className="activity">
      <div className="activity-head">
        <h3>API activity</h3>
        <span>what the agents are calling, live</span>
      </div>
      {events.length === 0 ? (
        <p className="activity-empty">{run.status === "running" || run.status === "queued" ? "No calls yet." : "No calls recorded for this run."}</p>
      ) : (
        <ol>
          {events.map((e) => (
            <li key={e.seq}>
              <span className="t">{clock(e.at, true)}</span>
              <span className="who" style={{ color: lighten(e.persona_color ?? "#888") }}>{e.persona_name}</span>
              <span className="call">{e.call}</span>
              <span className={e.code < 300 ? "ok" : "fail"}>{e.code}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

export default function RunReview({ paperId }: { paperId: string }) {
  const [paper, setPaper] = useState<Paper | null>(null);
  const [personas, setPersonas] = useState<Persona[] | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [viewing, setViewing] = useState<string | null>(null);
  const [viewed, setViewed] = useState<Run | null>(null);
  const [picked, setPicked] = useState<Set<string>>(new Set());
  const [rounds, setRounds] = useState(1);
  const [discussionOnly, setDiscussionOnly] = useState(false);
  const [configured, setConfigured] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  const loadRuns = useCallback(() => api.runs(paperId).then(setRuns).catch(() => undefined), [paperId]);

  useEffect(() => {
    api.paper(paperId).then(setPaper).catch((e) => setError(e.message));
    api.personas().then((ps) => {
      setPersonas(ps);
      setPicked(new Set(ps.filter((p) => p.kind === "builtin" && p.enabled).map((p) => p.id)));
    });
    api.status().then((s) => setConfigured(s.anthropic_configured)).catch(() => undefined);
    loadRuns();
  }, [paperId, loadRuns]);

  // Live progress.
  useEffect(() => {
    const es = new EventSource(api.eventsUrl(paperId));
    let t: number | undefined;
    es.onmessage = (m) => {
      const ev = JSON.parse(m.data);
      if (ev.type === "run.updated") {
        clearTimeout(t);
        t = window.setTimeout(loadRuns, 150);
      }
    };
    return () => {
      es.close();
      clearTimeout(t);
    };
  }, [paperId, loadRuns]);

  // An earlier run picked from the history list: fetch it with its activity log.
  useEffect(() => {
    if (!viewing || viewing === runs[0]?.id) return setViewed(null);
    api.run(viewing).then(setViewed).catch(() => setViewed(null));
  }, [viewing, runs]);

  const runnable = useMemo(() => (personas ?? []).filter((p) => p.kind === "builtin" && p.enabled), [personas]);
  const active = runs.find((r) => r.status === "running" || r.status === "queued");
  const shown = viewed ?? runs[0];
  const hasComments = (paper?.thread_count ?? 0) > 0;

  async function start() {
    setError(null);
    setStarting(true);
    try {
      await api.startRun(paperId, [...picked], discussionOnly ? Math.max(1, rounds) : rounds, !discussionOnly);
      setViewing(null);
      await loadRuns();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setStarting(false);
    }
  }

  const toggle = (id: string) => {
    const next = new Set(picked);
    next.has(id) ? next.delete(id) : next.add(id);
    setPicked(next);
  };

  return (
    <div className="page-wrap wide">
      <div className="page-title">
        <div className="crumbs">
          <a href="#/">Papers</a> / <a href={`#/paper/${paperId}`}>{paper?.title ?? "Paper"}</a>
        </div>
        <h1>Run review</h1>
      </div>

      <div className="run-layout">
        <section className="card setup" aria-label="Set up a run">
          <fieldset>
            <legend>Reviewers · one agent each, in parallel</legend>
            {personas && runnable.length === 0 && <p className="muted small">No personas are enabled.</p>}
            {runnable.map((p) => (
              <label key={p.id} className="pick">
                <input type="checkbox" checked={picked.has(p.id)} onChange={() => toggle(p.id)} />
                <Avatar name={p.name} color={p.color} size={26} />
                <span className="grow strong-ish">{p.name}</span>
                <span className="mono muted">{modelLabel(p.model)}</span>
              </label>
            ))}
            <a href="#/personas" className="muted small">Manage personas</a>
          </fieldset>

          <fieldset>
            <legend>Discussion rounds</legend>
            <div className="radio-seg" role="radiogroup" aria-label="Discussion rounds">
              {ROUND_OPTIONS.map((n) => (
                <button
                  key={n}
                  role="radio"
                  aria-checked={rounds === n}
                  disabled={discussionOnly && n === 0}
                  onClick={() => setRounds(n)}
                >
                  {n}
                </button>
              ))}
            </div>
            <p className="help">{roundsHelp(discussionOnly ? Math.max(1, rounds) : rounds, discussionOnly)}</p>
            <label className="check small">
              <input
                type="checkbox"
                checked={discussionOnly}
                disabled={!hasComments}
                onChange={(e) => {
                  setDiscussionOnly(e.target.checked);
                  if (e.target.checked && rounds === 0) setRounds(1);
                }}
              />
              Skip the solo review and discuss existing comments
            </label>
          </fieldset>

          <div className="setup-go">
            {!configured && <p className="warn">No Anthropic API key found. Set ANTHROPIC_API_KEY in backend/.env and restart the server.</p>}
            {error && <p className="error">{error}</p>}
            <button className="btn dark big full" disabled={!!active || starting || picked.size === 0} onClick={start}>
              {Icon.play}
              {active ? "A review is running" : starting ? "Starting…" : "Start review"}
            </button>
            <span className="muted xsmall center-text">Agents use the same HTTP API as everyone else. Outside a run they only answer people, never each other.</span>
          </div>
        </section>

        <section className="run-side" aria-label="Current run">
          {shown ? (
            <>
              <RunCard run={shown} onStop={() => api.cancelRun(shown.id).then(loadRuns)} />
              <Activity run={shown} />
              {runs.length > 1 && (
                <div className="card history">
                  <h3>Earlier runs</h3>
                  <ul>
                    {runs.map((r) => (
                      <li key={r.id}>
                        <button aria-current={shown.id === r.id} onClick={() => setViewing(r.id)}>
                          <span className="strong">Run {r.number}</span>
                          <span className="muted small">{runLabel({ persona_count: r.persona_ids.length, rounds: r.rounds, include_initial: r.include_initial })}</span>
                          <span className="spacer" />
                          <span className="muted small">{shortDate(r.created_at)}, {clock(r.created_at)} · {r.status}</span>
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          ) : (
            <div className="card empty-run">
              <h2>No runs yet</h2>
              <p className="muted">Pick reviewers and start a run. You'll see each persona's progress and every API call here as it happens.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
