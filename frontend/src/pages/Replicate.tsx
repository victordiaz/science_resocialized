import { useCallback, useEffect, useRef, useState } from "react";
import Markdown from "../components/Markdown";
import { api } from "../api";
import type { Attachment, Experiment, Paper, Persona, Replication, ReplicationEvent, Verification } from "../types";
import { Avatar, Icon, clock, modelLabel, shortDate } from "../ui";

type Tone = "live" | "idle" | "bad" | "good" | "warn";

const EXP_STATUS: Record<Experiment["status"], [string, Tone]> = {
  extracting: ["Extracting the experiment", "live"],
  checking: ["Checking for leaks", "live"],
  ready: ["Ready", "idle"],
  needs_review: ["Needs your review", "warn"],
  failed: ["Failed", "bad"],
};

const REP_STATUS: Record<Replication["status"], [string, Tone]> = {
  queued: ["Waiting for a worker", "idle"],
  running: ["Replicating", "live"],
  done: ["Finished", "good"],
  failed: ["Failed", "bad"],
  cancelled: ["Stopped", "idle"],
};

function Pill({ label, tone }: { label: string; tone: Tone }) {
  return (
    <span className={`pill ${tone}`}>
      {tone === "live" && <span className="dot" aria-hidden />}
      {label}
    </span>
  );
}

function bytes(n: number) {
  return n < 1024 ? `${n} B` : n < 1024 * 1024 ? `${(n / 1024).toFixed(0)} KB` : `${(n / 1024 / 1024).toFixed(1)} MB`;
}

function duration(from: string | null, to: string | null) {
  if (!from) return null;
  const ms = (to ? new Date(to) : new Date()).getTime() - new Date(from).getTime();
  const m = Math.floor(ms / 60000);
  return m < 60 ? `${m} min` : `${Math.floor(m / 60)} h ${m % 60} min`;
}

/** Pipeline stages for one experiment: extract → leak check → replicate → verify. */
function Stages({ exp }: { exp: Experiment }) {
  const rep = exp.replications[0];
  const vs = rep?.verifications ?? [];
  const stage = (name: string, state: "done" | "live" | "todo" | "bad" | "warn", sub: string) => ({ name, state, sub });
  const s = [
    stage(
      "Extract",
      exp.status === "extracting" ? "live" : exp.status === "failed" && !exp.spec_md ? "bad" : "done",
      exp.status === "extracting" ? "Reading the paper" : exp.spec_md ? "Spec written" : "Failed",
    ),
    stage(
      "Leak check",
      exp.status === "extracting" ? "todo" : exp.status === "checking" ? "live" : exp.leak_found ? "warn" : exp.spec_md ? "done" : "todo",
      exp.status === "checking" ? "Comparing spec and outcome" : exp.leak_found ? "Leak found" : exp.leak_found === false ? "Clean" : exp.spec_md ? "Edited by hand" : "",
    ),
    stage(
      "Replicate",
      !rep ? "todo" : rep.status === "running" || rep.status === "queued" ? "live" : rep.status === "done" ? "done" : "bad",
      !rep ? "Not started" : REP_STATUS[rep.status][0],
    ),
    stage(
      "Verify",
      vs.length === 0 ? "todo" : vs.some((v) => v.status === "running" || v.status === "pending") ? "live" : vs.every((v) => v.status === "done") ? "done" : "bad",
      vs.length === 0 ? (rep?.status === "done" ? "No verifiers picked" : "After the run") : `${vs.filter((v) => v.status === "done").length} of ${vs.length} reports`,
    ),
  ];
  return (
    <ol className="stages pipeline" aria-label="Pipeline" style={{ gridTemplateColumns: "repeat(4, minmax(0, 1fr))" }}>
      {s.map((x) => (
        <li key={x.name} aria-current={x.state === "live" ? "step" : undefined}>
          <span className={`track st-${x.state}`}><span /></span>
          <span className={`stage-name${x.state === "todo" ? " muted" : ""}`}>{x.name}</span>
          <span className="muted small">{x.sub}</span>
        </li>
      ))}
    </ol>
  );
}

function Doc({ title, md, hint, open = false, children }: { title: string; md: string; hint?: string; open?: boolean; children?: React.ReactNode }) {
  return (
    <details className="doc" open={open}>
      <summary>
        <span className="strong">{title}</span>
        {hint && <span className="muted small">{hint}</span>}
      </summary>
      <div className="doc-body md">
        <Markdown>{md}</Markdown>
        {children}
      </div>
    </details>
  );
}

function Log({ rep, tick }: { rep: Replication; tick: number }) {
  const [events, setEvents] = useState<ReplicationEvent[]>([]);
  const last = useRef(0);
  const box = useRef<HTMLOListElement>(null);

  useEffect(() => {
    let stop = false;
    (async () => {
      for (let i = 0; i < 20 && !stop; i++) {
        const r = await api.replication(rep.id, last.current).catch(() => null);
        const evs = r?.events ?? [];
        if (!evs.length || stop) break;
        last.current = evs[evs.length - 1].seq;
        setEvents((cur) => [...cur, ...evs].slice(-800));
        if (evs.length < 500) break;
      }
    })();
    return () => {
      stop = true;
    };
  }, [rep.id, tick, rep.status]);

  useEffect(() => {
    const el = box.current;
    if (el && el.scrollHeight - el.scrollTop - el.clientHeight < 80) el.scrollTop = el.scrollHeight;
  }, [events]);

  return (
    <div className="activity">
      <div className="activity-head">
        <h3>Replicator log</h3>
        <span>Claude Code, blind{rep.worker ? `, on worker “${rep.worker}”` : ""}</span>
      </div>
      {events.length === 0 ? (
        <p className="activity-empty">{rep.status === "queued" ? "Waiting for a worker to pick up the job." : "Nothing logged yet."}</p>
      ) : (
        <ol ref={box}>
          {events.map((e) => (
            <li key={e.seq} className={`ev-${e.kind}`}>
              <span className="t">{clock(e.at, true)}</span>
              <span className="call">{e.text}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function VerificationCard({ v }: { v: Verification }) {
  const name = v.persona_name ?? "Verifier";
  const color = v.persona_color ?? "#495057";
  return (
    <section className="card verification">
      <div className="ver-head">
        <Avatar name={name} color={color} size={28} />
        <span className="strong">{name}</span>
        <span className="spacer" />
        {v.status === "done" ? (
          <span className="muted small">{v.finished_at ? clock(v.finished_at) : ""}</span>
        ) : (
          <Pill label={v.status === "failed" ? "Failed" : v.status === "pending" ? "Queued" : "Verifying"} tone={v.status === "failed" ? "bad" : v.status === "pending" ? "idle" : "live"} />
        )}
      </div>
      {v.report_md && <div className="md ver-body"><Markdown>{v.report_md}</Markdown></div>}
      {v.error && <p className="error">{v.error}</p>}
    </section>
  );
}

function ReplicationBlock({ rep, n, personas, tick, onChanged }: { rep: Replication; n: number; personas: Persona[]; tick: number; onChanged: () => void }) {
  const [label, tone] = REP_STATUS[rep.status];
  const active = rep.status === "queued" || rep.status === "running";
  const [verifyPick, setVerifyPick] = useState<string[] | null>(null);
  const runnable = personas.filter((p) => p.kind === "builtin" && p.enabled);
  const meta = [
    rep.started_at ? `started ${clock(rep.started_at)}` : `queued ${clock(rep.created_at)}`,
    duration(rep.started_at, rep.finished_at),
    rep.cost_usd != null ? `$${rep.cost_usd.toFixed(2)} of $${rep.budget_usd.toFixed(0)}` : `budget $${rep.budget_usd.toFixed(0)}`,
    rep.attachments.length ? `${rep.attachments.length} input ${rep.attachments.length === 1 ? "file" : "files"}` : null,
  ].filter(Boolean).join(" · ");

  return (
    <div className="rep">
      <div className="run-head">
        <h3>Replication {n}</h3>
        <Pill label={rep.cancel_requested && active ? "Stopping" : label} tone={tone} />
        <span className="muted small">{meta}</span>
        <span className="spacer" />
        {active && !rep.cancel_requested && <button className="btn" onClick={() => api.cancelReplication(rep.id).then(onChanged)}>Stop</button>}
        {!active && <button className="btn ghost" onClick={() => setVerifyPick(verifyPick ? null : runnable.map((p) => p.id))}>Verify again</button>}
      </div>
      {rep.error && <p className="error small">{rep.error}</p>}

      {verifyPick && (
        <div className="verify-pick">
          {runnable.map((p) => (
            <label key={p.id} className="check small">
              <input
                type="checkbox"
                checked={verifyPick.includes(p.id)}
                onChange={() => setVerifyPick(verifyPick.includes(p.id) ? verifyPick.filter((x) => x !== p.id) : [...verifyPick, p.id])}
              />
              <span className="dot" style={{ background: p.color }} /> {p.name}
            </label>
          ))}
          <button
            className="btn dark"
            disabled={verifyPick.length === 0}
            onClick={() => api.verify(rep.id, verifyPick).then(() => (setVerifyPick(null), onChanged()))}
          >
            Start verification
          </button>
        </div>
      )}

      <Log rep={rep} tick={tick} />

      {rep.report_md && <Doc title="Replicator's report" hint="REPORT.md" md={rep.report_md} open />}

      {rep.files.length > 0 && (
        <details className="doc">
          <summary>
            <span className="strong">Files</span>
            <span className="muted small">{rep.files.length} uploaded: code, outputs, plots</span>
          </summary>
          <ul className="files">
            {rep.files.map((f) => (
              <li key={f.path}>
                <a href={api.replicationFileUrl(rep.id, f.path)} target="_blank" rel="noreferrer" className="mono-link">{f.path}</a>
                <span className="muted xsmall">{bytes(f.size)}</span>
              </li>
            ))}
          </ul>
        </details>
      )}

      {rep.verifications.length > 0 && (
        <div className="verifications">
          <h3>Verification</h3>
          {rep.verifications.map((v) => <VerificationCard key={v.id} v={v} />)}
        </div>
      )}
    </div>
  );
}

function AttachmentRow({ a, onChanged }: { a: Attachment; onChanged: () => void }) {
  const [note, setNote] = useState(a.note);
  useEffect(() => setNote(a.note), [a.note]);
  return (
    <li className="att">
      <span className="att-icon" aria-hidden>{(a.filename.split(".").pop() ?? "").slice(0, 4).toUpperCase() || "FILE"}</span>
      <span className="att-main">
        <span className="att-name">
          <a href={api.attachmentUrl(a.id)} className="mono-link" download>{a.filename}</a>
          <span className="muted xsmall">{bytes(a.size)}</span>
        </span>
        <input
          className="att-note"
          value={note}
          placeholder="What is this? (shown to the replicator)"
          aria-label={`Note for ${a.filename}`}
          onChange={(e) => setNote(e.target.value)}
          onBlur={() => note !== a.note && api.updateAttachment(a.id, note).then(onChanged)}
          onKeyDown={(e) => e.key === "Enter" && (e.target as HTMLInputElement).blur()}
        />
      </span>
      <button className="btn ghost" aria-label={`Remove ${a.filename}`} onClick={() => confirm(`Remove ${a.filename}?`) && api.deleteAttachment(a.id).then(onChanged)}>
        Remove
      </button>
    </li>
  );
}

/** Files a person provides for the replicator (datasets, archives, code). They land in ./inputs/. */
function Attachments({ exp, onChanged }: { exp: Experiment; onChanged: () => void }) {
  const [over, setOver] = useState(false);
  const [progress, setProgress] = useState<{ names: string; fraction: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const input = useRef<HTMLInputElement>(null);
  const total = exp.attachments.reduce((n, a) => n + a.size, 0);

  async function upload(list: FileList | File[]) {
    const files = [...list];
    if (!files.length) return;
    setError(null);
    setProgress({ names: files.length === 1 ? files[0].name : `${files.length} files`, fraction: 0 });
    try {
      await api.uploadAttachments(exp.id, files, (fraction) => setProgress((p) => p && { ...p, fraction }));
      onChanged();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setProgress(null);
      if (input.current) input.current.value = "";
    }
  }

  return (
    <section className="attachments" aria-label="Files for the replicator">
      <div className="att-head">
        <span className="strong">Files for the replicator</span>
        <span className="muted small">
          {exp.attachments.length ? `${exp.attachments.length} in inputs/, ${bytes(total)}` : "Datasets, archives, code: any type, any number"}
        </span>
      </div>
      {exp.attachments.length > 0 && (
        <ul className="att-list">
          {exp.attachments.map((a) => <AttachmentRow key={a.id} a={a} onChanged={onChanged} />)}
        </ul>
      )}
      <label
        className={`att-drop${over ? " over" : ""}`}
        onDragOver={(e) => (e.preventDefault(), setOver(true))}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setOver(false);
          upload(e.dataTransfer.files);
        }}
      >
        {progress ? (
          <span className="att-progress">
            <span className="small">Uploading {progress.names}… {Math.round(progress.fraction * 100)}%</span>
            <span className="bar"><span style={{ width: `${progress.fraction * 100}%` }} /></span>
          </span>
        ) : (
          <span className="small">
            <strong>Drop files here</strong> or <span className="link">choose files</span>. Zips stay zipped; the replicator unpacks them.
            Don't include anything with the paper's results.
          </span>
        )}
        <input ref={input} type="file" multiple className="sr-only" onChange={(e) => e.target.files && upload(e.target.files)} />
      </label>
      {error && <p className="error">{error}</p>}
    </section>
  );
}

/** Step 2: pick verifiers and a budget, then queue the blind replication. */
function StartReplication({ exp, personas, anyway, onStarted }: { exp: Experiment; personas: Persona[]; anyway: boolean; onStarted: () => void }) {
  const runnable = personas.filter((p) => p.kind === "builtin" && p.enabled);
  const [picked, setPicked] = useState<string[]>(() => runnable.slice(0, 2).map((p) => p.id));
  const [budget, setBudget] = useState(3);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function go() {
    setError(null);
    setBusy(true);
    try {
      await api.replicate(exp.id, { verifier_ids: picked, budget_usd: budget });
      onStarted();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="start-rep">
      <div className="start-rep-head">
        <span className="step">2</span>
        <span className="strong">{exp.replications.length ? "Replicate again" : "Replicate it blind"}</span>
        <span className="muted small">
          Claude Code gets only the spec above{exp.attachments.length ? ` and the ${exp.attachments.length === 1 ? "file" : `${exp.attachments.length} files`} in inputs/` : ""}
        </span>
      </div>
      <div className="start-rep-body">
        <fieldset>
          <legend>Verifiers, after the run</legend>
          <div className="chips">
            {runnable.map((p) => (
              <label key={p.id} className={`chip-btn${picked.includes(p.id) ? " on" : ""}`}>
                <input
                  type="checkbox"
                  className="sr-only"
                  checked={picked.includes(p.id)}
                  onChange={() => setPicked(picked.includes(p.id) ? picked.filter((x) => x !== p.id) : [...picked, p.id])}
                />
                <span className="dot" style={{ background: p.color }} aria-hidden />
                {p.name}
              </label>
            ))}
          </div>
        </fieldset>
        <label className="budget">
          <span className="strong small">Budget</span>
          $<input type="number" min={1} max={500} value={budget} onChange={(e) => setBudget(Math.max(1, Math.min(500, +e.target.value || 1)))} />
        </label>
        <span className="spacer" />
        <button className="btn dark big" disabled={busy} onClick={go}>
          {Icon.play}
          {anyway ? "Replicate anyway" : "Start replication"}
        </button>
      </div>
      {error && <p className="error">{error}</p>}
    </div>
  );
}

function ExperimentCard({ exp, personas, ticks, onChanged }: { exp: Experiment; personas: Persona[]; ticks: Record<string, number>; onChanged: () => void }) {
  const [label, tone] = EXP_STATUS[exp.status];
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(exp.spec_md);
  const [error, setError] = useState<string | null>(null);
  const busy = exp.status === "extracting" || exp.status === "checking";
  const latest = exp.replications[0];
  const canReplicate = !!exp.spec_md && !busy && !(latest && (latest.status === "queued" || latest.status === "running"));

  async function act(fn: () => Promise<unknown>) {
    setError(null);
    try {
      await fn();
      onChanged();
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <article className="card experiment">
      <div className="run-head">
        <h2>{exp.title || "Main experiment"}</h2>
        <Pill label={label} tone={tone} />
        <span className="muted small">{shortDate(exp.created_at)}, {clock(exp.created_at)}</span>
      </div>
      <Stages exp={exp} />
      {exp.error && <p className="error">{exp.error}</p>}

      {exp.status === "needs_review" && (
        <div className="callout warn-box">
          <p className="strong">The leak check flagged the spec before it went to the replicator.</p>
          {exp.leak_check_md && <div className="md"><Markdown>{exp.leak_check_md}</Markdown></div>}
          <div className="row">
            <button className="btn" onClick={() => (setDraft(exp.spec_md), setEditing(true))}>Edit the spec</button>
            <button className="btn" onClick={() => act(() => api.recheckLeaks(exp.id))}>Check again</button>
          </div>
        </div>
      )}

      {exp.spec_md && !editing && (
        <Doc title="Experiment spec" hint="what the replicator gets" md={exp.spec_md} open={exp.status === "needs_review" || exp.replications.length === 0}>
          {!busy && (
            <div className="row">
              <button className="btn" onClick={() => (setDraft(exp.spec_md), setEditing(true))}>Edit spec</button>
            </div>
          )}
        </Doc>
      )}
      {editing && (
        <div className="spec-edit">
          <label className="field-label" htmlFor={`spec-${exp.id}`}>Experiment spec (markdown). Keep results and anything that identifies the paper out of it.</label>
          <textarea id={`spec-${exp.id}`} className="mono-area" rows={18} value={draft} onChange={(e) => setDraft(e.target.value)} />
          <div className="row end">
            <button className="btn" onClick={() => setEditing(false)}>Cancel</button>
            <button className="btn dark" onClick={() => act(async () => (await api.updateExperiment(exp.id, { spec_md: draft }), setEditing(false)))}>Save spec</button>
          </div>
        </div>
      )}
      {exp.outcome_md && <Doc title="Paper's reported outcome" hint="hidden from the replicator, given to verifiers" md={exp.outcome_md} />}
      {exp.leak_check_md && exp.status !== "needs_review" && <Doc title="Leak check" hint={exp.leak_found ? "leak found" : exp.leak_found === false ? "clean" : ""} md={exp.leak_check_md} />}

      {error && <p className="error">{error}</p>}
      {!!exp.spec_md && !busy && !editing && <Attachments exp={exp} onChanged={onChanged} />}

      {canReplicate && !editing && (
        <StartReplication exp={exp} personas={personas} anyway={exp.status === "needs_review"} onStarted={onChanged} />
      )}

      {exp.replications.map((r, i) => (
        <ReplicationBlock key={r.id} rep={r} n={exp.replications.length - i} personas={personas} tick={ticks[r.id] ?? 0} onChanged={onChanged} />
      ))}
    </article>
  );
}

export default function Replicate({ paperId }: { paperId: string }) {
  const [paper, setPaper] = useState<Paper | null>(null);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [experiments, setExperiments] = useState<Experiment[] | null>(null);
  const [configured, setConfigured] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [ticks, setTicks] = useState<Record<string, number>>({});

  const load = useCallback(() => api.experiments(paperId).then(setExperiments).catch((e) => setError(e.message)), [paperId]);

  useEffect(() => {
    api.paper(paperId).then(setPaper).catch((e) => setError(e.message));
    api.personas().then(setPersonas);
    api.status().then((s) => setConfigured(s.anthropic_configured)).catch(() => undefined);
    load();
  }, [paperId, load]);

  useEffect(() => {
    const es = new EventSource(api.eventsUrl(paperId));
    let t: number | undefined;
    es.onmessage = (m) => {
      const ev = JSON.parse(m.data);
      if (ev.type === "replication.updated") {
        clearTimeout(t);
        t = window.setTimeout(load, 200);
      } else if (ev.type === "replication.events") {
        setTicks((cur) => ({ ...cur, [ev.replication_id]: (cur[ev.replication_id] ?? 0) + 1 }));
      }
    };
    return () => {
      es.close();
      clearTimeout(t);
    };
  }, [paperId, load]);

  const busy = (experiments ?? []).some((e) => e.status === "extracting" || e.status === "checking");

  async function start() {
    setError(null);
    setStarting(true);
    try {
      await api.startExtraction(paperId);
      await load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setStarting(false);
    }
  }

  return (
    <div className="page-wrap wide">
      <div className="page-title">
        <div className="crumbs">
          <a href="#/">Papers</a> / <a href={`#/paper/${paperId}`}>{paper?.title ?? "Paper"}</a>
        </div>
        <h1>Blind replication</h1>
        <p>Pull out the paper's main experiment, have Claude Code replicate it without seeing the results, then let personas check the replication against the paper.</p>
      </div>

      <div className="run-layout">
        <section className="card setup" aria-label="Start a replication">
          <ol className="how">
            <li><strong>Extract.</strong> An agent writes the experiment spec and, separately, the results the paper reports. A second agent checks the spec gives nothing away. Then it stops so you can read or edit the spec.</li>
            <li><strong>Replicate.</strong> When you start it, Claude Code gets only the spec, writes and runs the code in its own folder, and writes a report. No web search; told not to look the paper up. It runs code on the worker machine with permissions bypassed.</li>
            <li><strong>Verify.</strong> When the run finishes, each persona you picked compares it with the paper and writes a report.</li>
          </ol>

          <div className="setup-go">
            {!configured && <p className="warn">No Anthropic API key found. Set ANTHROPIC_API_KEY in backend/.env and restart the server.</p>}
            {error && <p className="error">{error}</p>}
            <button className="btn dark big full" disabled={starting || busy} onClick={start}>
              {Icon.play}
              {busy ? "Extracting…" : starting ? "Starting…" : "Extract experiment"}
            </button>
            <span className="muted xsmall center-text">Step 1 only. Nothing runs until you start the replication on the experiment.</span>
          </div>
        </section>

        <section className="run-side" aria-label="Experiments">
          {experiments && experiments.length === 0 && (
            <div className="card empty-run">
              <h2>No experiment extracted yet</h2>
              <p className="muted">Extract the experiment on the left. It takes a minute or two; you start the replication afterwards.</p>
            </div>
          )}
          {(experiments ?? []).map((e) => (
            <ExperimentCard key={e.id} exp={e} personas={personas} ticks={ticks} onChanged={load} />
          ))}
        </section>
      </div>
    </div>
  );
}
