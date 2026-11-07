import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Markdown from "../components/Markdown";
import { api } from "../api";
import type { Attachment, Experiment, Paper, Persona, Replication, ReplicationEvent, Verification } from "../types";
import { Avatar, Icon, clock, shortDate } from "../ui";

type Tone = "live" | "idle" | "bad" | "good" | "warn";

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
  return m < 1 ? "under a minute" : m < 60 ? `${m} min` : `${Math.floor(m / 60)} h ${m % 60} min`;
}

/** File names the spec mentions (e.g. d04.txt, train.csv), so we can tell what still needs attaching. */
const FILE_RE = /(?<![\w/.-])([\w-][\w.-]*\.(?:txt|csv|tsv|json|jsonl|xlsx?|parquet|zip|tar|gz|tgz|npz|npy|h5|hdf5|pkl|pt|mat|sav|dta|rds|rdata|dat|xml|yaml|yml|py|r|ipynb))(?![\w])/gi;
function filesMentioned(spec: string): string[] {
  const out = new Set<string>();
  for (const m of spec.matchAll(FILE_RE)) {
    const name = m[1];
    if (!/^(task|report)\.md$/i.test(name) && !/^outputs?\//i.test(name)) out.add(name);
  }
  return [...out].slice(0, 20);
}

// ---------------------------------------------------------------- building blocks

/** One numbered step of the experiment: number, title, one-line status, then its content. */
function Step({ id, n, title, status, tone = "idle", children, done }: { id?: string; n: number | string; title: string; status?: React.ReactNode; tone?: Tone; done?: boolean; children?: React.ReactNode }) {
  return (
    <section id={id} className={`step-block tone-${tone}${done ? " done" : ""}`} data-outline>
      <header className="step-head">
        <span className="step-num" aria-hidden>{done ? "✓" : n}</span>
        <h3>{title}</h3>
        {status && <span className="step-status">{status}</span>}
      </header>
      {children && <div className="step-body">{children}</div>}
    </section>
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

  const shown = events.filter((e) => e.text.trim());
  return (
    <div className="activity">
      <div className="activity-head">
        <h3>Replicator log</h3>
        <span>Claude Code, blind{rep.worker ? `, on worker “${rep.worker}”` : ""}</span>
      </div>
      {shown.length === 0 ? (
        <p className="activity-empty">{rep.status === "queued" ? "Waiting for a worker to pick up the job." : "Nothing logged yet."}</p>
      ) : (
        <ol ref={box}>
          {shown.map((e) => (
            <li key={e.seq} className={`ev-${e.kind}`}>
              <span className="t">{clock(e.at, true)}</span>
              <span className="call">{e.text.trim()}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

/** First meaningful line of a report, without markdown markers, for a one-line summary. */
function firstLine(md: string | null): string {
  if (!md) return "";
  const line = md.split("\n").map((l) => l.replace(/^#+\s*|^[-*]\s+|\*\*|__|`/g, "").trim()).find((l) => l.length > 0) ?? "";
  return line.replace(/^summary:\s*/i, "");
}

function VerificationCard({ v }: { v: Verification }) {
  const name = v.persona_name ?? "Verifier";
  const color = v.persona_color ?? "#495057";
  return (
    <details className="verification" id={`ver-${v.id}`} data-outline>
      <summary className="ver-head">
        <Avatar name={name} color={color} size={26} />
        <span className="ver-title">
          <span className="strong">{name}</span>
          {v.report_md && <span className="ver-line">{firstLine(v.report_md)}</span>}
        </span>
        <span className="spacer" />
        {v.status === "done" ? (
          <span className="muted small">{v.finished_at ? clock(v.finished_at) : ""}</span>
        ) : (
          <Pill label={v.status === "failed" ? "Failed" : v.status === "pending" ? "Queued" : "Verifying"} tone={v.status === "failed" ? "bad" : v.status === "pending" ? "idle" : "live"} />
        )}
      </summary>
      {v.report_md && <div className="md ver-body"><Markdown>{v.report_md}</Markdown></div>}
      {v.error && <p className="error">{v.error}</p>}
    </details>
  );
}

// ---------------------------------------------------------------- files

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
          placeholder="Add a note: what is this file? (the replicator sees it)"
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

function FilesStep({ exp, onChanged }: { exp: Experiment; onChanged: () => void }) {
  const [over, setOver] = useState(false);
  const [progress, setProgress] = useState<{ names: string; fraction: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const input = useRef<HTMLInputElement>(null);
  const total = exp.attachments.reduce((n, a) => n + a.size, 0);
  const mentioned = useMemo(() => filesMentioned(exp.spec_md), [exp.spec_md]);
  const have = new Set(exp.attachments.map((a) => a.filename.toLowerCase()));
  const missing = mentioned.filter((m) => !have.has(m.toLowerCase()));

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

  const status = missing.length
    ? <span className="warn-text">{missing.length === 1 ? "1 file the spec mentions is missing" : `${missing.length} files the spec mentions are missing`}</span>
    : exp.attachments.length
      ? `${exp.attachments.length} ${exp.attachments.length === 1 ? "file" : "files"} in inputs/, ${bytes(total)}`
      : "Optional: datasets, archives, code";

  return (
    <Step id={`${exp.id}-files`} n={2} title="Files for the replicator" status={status} tone={missing.length ? "warn" : "idle"} done={exp.attachments.length > 0 && missing.length === 0}>
      {mentioned.length > 0 && (
        <div className="mentioned">
          <span className="small">The spec mentions:</span>
          {mentioned.map((m) => {
            const ok = have.has(m.toLowerCase());
            return (
              <span key={m} className={`need${ok ? " ok" : ""}`} title={ok ? "Attached" : "Not attached yet"}>
                <span aria-hidden>{ok ? "✓" : "○"}</span> {m}
              </span>
            );
          })}
        </div>
      )}

      {exp.attachments.length > 0 && (
        <ul className="att-list">
          {exp.attachments.map((a) => <AttachmentRow key={a.id} a={a} onChanged={onChanged} />)}
        </ul>
      )}

      <label
        className={`att-drop big${over ? " over" : ""}${missing.length ? " needed" : ""}`}
        onDragOver={(e) => (e.preventDefault(), setOver(true))}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setOver(false);
          upload(e.dataTransfer.files);
        }}
      >
        <span className="dz-icon">{Icon.upload}</span>
        {progress ? (
          <span className="att-progress">
            <strong>Uploading {progress.names}… {Math.round(progress.fraction * 100)}%</strong>
            <span className="bar"><span style={{ width: `${progress.fraction * 100}%` }} /></span>
          </span>
        ) : (
          <span className="dz-text">
            <strong>Drop files here, or click to choose</strong>
            <span>Any type and any number. They go to <code>inputs/</code> in the replicator's folder; zips stay zipped. Don't include anything with the paper's results.</span>
          </span>
        )}
        <input ref={input} type="file" multiple className="sr-only" onChange={(e) => e.target.files && upload(e.target.files)} />
      </label>
      {error && <p className="error">{error}</p>}
    </Step>
  );
}

// ---------------------------------------------------------------- replicate

function ReplicateStep({ exp, personas, onStarted }: { exp: Experiment; personas: Persona[]; onStarted: () => void }) {
  const runnable = personas.filter((p) => p.kind === "builtin" && p.enabled);
  const [picked, setPicked] = useState<string[]>(() => runnable.slice(0, 2).map((p) => p.id));
  const [budget, setBudget] = useState(3);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const latest = exp.replications[0];
  const running = latest && (latest.status === "queued" || latest.status === "running");
  const missing = filesMentioned(exp.spec_md).filter((m) => !exp.attachments.some((a) => a.filename.toLowerCase() === m.toLowerCase()));

  useEffect(() => {
    if (picked.length === 0 && runnable.length) setPicked(runnable.slice(0, 2).map((p) => p.id));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [personas]);

  async function go() {
    if (missing.length && !confirm(`The spec mentions ${missing.join(", ")}, which ${missing.length === 1 ? "isn't" : "aren't"} attached. Start anyway?`)) return;
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

  const status = running
    ? "A replication is running; see below"
    : `Claude Code gets the spec${exp.attachments.length ? ` and ${exp.attachments.length} ${exp.attachments.length === 1 ? "file" : "files"}` : ""}, nothing else`;

  return (
    <Step id={`${exp.id}-replicate`} n={3} title={latest ? "Replicate again" : "Replicate it blind"} status={status} tone={running ? "live" : "idle"}>
      {!running && (
        <>
          <div className="rep-form">
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
              <span className="legend-like">Budget</span>
              <span className="budget-input">$<input type="number" min={1} max={500} value={budget} onChange={(e) => setBudget(Math.max(1, Math.min(500, +e.target.value || 1)))} /></span>
            </label>
            <button className="btn dark big" disabled={busy} onClick={go}>
              {Icon.play}
              {exp.status === "needs_review" ? "Replicate anyway" : "Start replication"}
            </button>
          </div>
          {missing.length > 0 && <p className="warn small">Missing files: {missing.join(", ")}. Attach them in step 2 first.</p>}
          {error && <p className="error">{error}</p>}
        </>
      )}
    </Step>
  );
}

// ---------------------------------------------------------------- runs

function ReplicationBlock({ rep, n, latest, personas, tick, onChanged }: { rep: Replication; n: number; latest: boolean; personas: Persona[]; tick: number; onChanged: () => void }) {
  const [label, tone] = REP_STATUS[rep.status];
  const active = rep.status === "queued" || rep.status === "running";
  const [verifyPick, setVerifyPick] = useState<string[] | null>(null);
  const runnable = personas.filter((p) => p.kind === "builtin" && p.enabled);
  const reportHead = rep.report_md?.split("\n").find((l) => /^\*{0,2}status/i.test(l.replace(/^#+\s*/, "")))?.replace(/^#+\s*/, "").replace(/\*\*/g, "");
  const meta = [
    rep.started_at ? `${shortDate(rep.started_at)}, ${clock(rep.started_at)}` : `queued ${clock(rep.created_at)}`,
    duration(rep.started_at, rep.finished_at),
    rep.cost_usd != null ? `$${rep.cost_usd.toFixed(2)} of $${rep.budget_usd.toFixed(0)}` : `budget $${rep.budget_usd.toFixed(0)}`,
    rep.attachments.length ? `${rep.attachments.length} input ${rep.attachments.length === 1 ? "file" : "files"}` : "no input files",
  ].filter(Boolean).join(" · ");

  return (
    <details id={`run-${rep.id}`} className={`run-block${active ? " active" : ""}`} open={latest} data-outline>
      <summary className="run-summary">
        <span className="strong">Run {n}</span>
        <Pill label={rep.cancel_requested && active ? "Stopping" : label} tone={tone} />
        <span className="muted small">{meta}</span>
      </summary>
      <div className="run-body">
        {reportHead && <p className="run-verdict">{reportHead}</p>}
        {rep.error && <p className="error small">{rep.error}</p>}
        <div className="row">
          {active && !rep.cancel_requested && <button className="btn" onClick={() => api.cancelReplication(rep.id).then(onChanged)}>Stop run</button>}
          {!active && <button className="btn" onClick={() => setVerifyPick(verifyPick ? null : runnable.map((p) => p.id))}>Verify again</button>}
        </div>

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
            <button className="btn dark" disabled={verifyPick.length === 0} onClick={() => api.verify(rep.id, verifyPick).then(() => (setVerifyPick(null), onChanged()))}>
              Start verification
            </button>
          </div>
        )}

        {rep.verifications.length > 0 && (
          <div className="verifications">
            <h4>Verification reports</h4>
            {rep.verifications.map((v) => <VerificationCard key={v.id} v={v} />)}
          </div>
        )}


        {rep.report_md && <Doc title="Replicator's report" hint="REPORT.md: what it built, ran and measured" md={rep.report_md} open={latest && rep.verifications.length === 0} />}
        {active ? (
          <Log rep={rep} tick={tick} />
        ) : (
          <details className="doc">
            <summary><span className="strong">Replicator log</span><span className="muted small">every command it ran</span></summary>
            <div className="doc-body"><Log rep={rep} tick={tick} /></div>
          </details>
        )}

        {rep.files.length > 0 && (
          <details className="doc">
            <summary>
              <span className="strong">Files it produced</span>
              <span className="muted small">{rep.files.length}: code, outputs, plots</span>
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

      </div>
    </details>
  );
}

// ---------------------------------------------------------------- experiment

function ExperimentCard({ exp, personas, ticks, onChanged }: { exp: Experiment; personas: Persona[]; ticks: Record<string, number>; onChanged: () => void }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(exp.spec_md);
  const [error, setError] = useState<string | null>(null);
  const busy = exp.status === "extracting" || exp.status === "checking";

  async function act(fn: () => Promise<unknown>) {
    setError(null);
    try {
      await fn();
      onChanged();
    } catch (e) {
      setError((e as Error).message);
    }
  }

  const specStatus =
    exp.status === "extracting" ? "Reading the paper and writing the spec…"
    : exp.status === "checking" ? "Checking the spec gives nothing away…"
    : exp.status === "failed" ? "Extraction failed"
    : exp.status === "needs_review" ? <span className="warn-text">The leak check flagged it; review before replicating</span>
    : exp.leak_found === false ? "Written and checked: no leaks"
    : "Edited by hand";
  const specTone: Tone = busy ? "live" : exp.status === "failed" ? "bad" : exp.status === "needs_review" ? "warn" : "idle";

  return (
    <article className="experiment" id={exp.id}>
      <header className="exp-head">
        <h2>{exp.title || "Main experiment"}</h2>
        <span className="muted small">Extracted {shortDate(exp.created_at)}, {clock(exp.created_at)}</span>
      </header>

      <Step id={`${exp.id}-spec`} n={1} title="Experiment spec" status={specStatus} tone={specTone} done={!busy && exp.status !== "failed" && exp.status !== "needs_review" && !!exp.spec_md}>
        {exp.error && <p className="error">{exp.error}</p>}
        {exp.status === "needs_review" && (
          <div className="callout warn-box">
            {exp.leak_check_md && <div className="md"><Markdown>{exp.leak_check_md}</Markdown></div>}
            <div className="row">
              <button className="btn" onClick={() => (setDraft(exp.spec_md), setEditing(true))}>Edit the spec</button>
              <button className="btn" onClick={() => act(() => api.recheckLeaks(exp.id))}>Check again</button>
            </div>
          </div>
        )}
        {exp.spec_md && !editing && (
          <Doc title="What the replicator gets" hint="the spec" md={exp.spec_md} open={exp.replications.length === 0 && exp.status !== "needs_review"}>
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
        {exp.outcome_md && <Doc title="What the paper reports" hint="hidden from the replicator; for verifiers" md={exp.outcome_md} />}
        {exp.leak_check_md && exp.status !== "needs_review" && <Doc title="Leak check" hint={exp.leak_found ? "leak found" : exp.leak_found === false ? "clean" : ""} md={exp.leak_check_md} />}
        {error && <p className="error">{error}</p>}
      </Step>

      {!!exp.spec_md && !busy && <FilesStep exp={exp} onChanged={onChanged} />}
      {!!exp.spec_md && !busy && !editing && <ReplicateStep exp={exp} personas={personas} onStarted={onChanged} />}

      {exp.replications.length > 0 && (
        <section className="runs">
          <h3 className="runs-title">Runs</h3>
          {exp.replications.map((r, i) => (
            <ReplicationBlock key={r.id} rep={r} n={exp.replications.length - i} latest={i === 0} personas={personas} tick={ticks[r.id] ?? 0} onChanged={onChanged} />
          ))}
        </section>
      )}
    </article>
  );
}

// ---------------------------------------------------------------- outline sidebar

function missingFiles(exp: Experiment) {
  return filesMentioned(exp.spec_md).filter((m) => !exp.attachments.some((a) => a.filename.toLowerCase() === m.toLowerCase()));
}

function goTo(id: string) {
  const el = document.getElementById(id);
  if (!el) return;
  // Open it and every folded section around it.
  for (let d: HTMLElement | null = el; d; d = d.parentElement?.closest("details") ?? null) {
    if (d instanceof HTMLDetailsElement) d.open = true;
  }
  el.scrollIntoView({ behavior: "smooth", block: "start" });
}

type OutlineItem = { id: string; label: string; sub?: string; mark: "done" | "warn" | "live" | "bad" | "todo"; depth: 0 | 1 | 2 };

function outlineFor(exp: Experiment): OutlineItem[] {
  const busy = exp.status === "extracting" || exp.status === "checking";
  const missing = missingFiles(exp);
  const latest = exp.replications[0];
  const items: OutlineItem[] = [
    { id: exp.id, label: exp.title || "Main experiment", mark: "todo", depth: 0 },
    {
      id: `${exp.id}-spec`,
      label: "1  Experiment spec",
      sub: busy ? (exp.status === "extracting" ? "Extracting…" : "Checking leaks…") : exp.status === "needs_review" ? "Leak flagged" : exp.status === "failed" ? "Failed" : "Ready",
      mark: busy ? "live" : exp.status === "needs_review" ? "warn" : exp.status === "failed" ? "bad" : "done",
      depth: 1,
    },
  ];
  if (exp.spec_md && !busy) {
    items.push({
      id: `${exp.id}-files`,
      label: "2  Files",
      sub: missing.length ? `${missing.length} missing` : exp.attachments.length ? `${exp.attachments.length} attached` : "None",
      mark: missing.length ? "warn" : exp.attachments.length ? "done" : "todo",
      depth: 1,
    });
    const running = latest && (latest.status === "queued" || latest.status === "running");
    items.push({ id: `${exp.id}-replicate`, label: "3  Replicate", sub: running ? "Running" : latest ? `${exp.replications.length} ${exp.replications.length === 1 ? "run" : "runs"}` : "Not started", mark: running ? "live" : latest ? "done" : "todo", depth: 1 });
  }
  exp.replications.forEach((r, i) => {
    const n = exp.replications.length - i;
    const verdict = r.report_md?.split("\n").find((l) => /^\*{0,2}status/i.test(l.replace(/^#+\s*/, "")))?.replace(/^#+\s*|\*\*/g, "").replace(/^status:\s*/i, "");
    items.push({
      id: `run-${r.id}`,
      label: `Run ${n}`,
      sub: verdict ? verdict.split(",")[0] : REP_STATUS[r.status][0],
      mark: r.status === "running" || r.status === "queued" ? "live" : r.status === "failed" ? "bad" : r.status === "done" ? "done" : "todo",
      depth: 1,
    });
    for (const v of r.verifications) {
      items.push({ id: `ver-${v.id}`, label: v.persona_name ?? "Verifier", sub: v.status === "done" ? "Report" : v.status, mark: v.status === "done" ? "done" : v.status === "failed" ? "bad" : "live", depth: 2 });
    }
  });
  return items;
}

const MARK: Record<OutlineItem["mark"], string> = { done: "✓", warn: "!", live: "●", bad: "×", todo: "○" };

function Outline({ experiments }: { experiments: Experiment[] }) {
  const [current, setCurrent] = useState<string | null>(null);

  useEffect(() => {
    const els = [...document.querySelectorAll<HTMLElement>("[data-outline]")];
    if (!els.length) return;
    const io = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setCurrent(visible[0].target.id);
      },
      { rootMargin: "-80px 0px -60% 0px" }
    );
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, [experiments]);

  return (
    <nav className="outline" aria-label="On this page">
      <div className="outline-title">On this page</div>
      {experiments.map((exp) => (
        <ul key={exp.id}>
          {outlineFor(exp).map((it, i) => (
            <li key={it.id + i} className={`d${it.depth}${current === it.id && it.depth > 0 ? " current" : ""}`}>
              <button onClick={() => goTo(it.id)}>
                {it.depth > 0 && <span className={`o-mark m-${it.mark}`} aria-hidden>{MARK[it.mark]}</span>}
                <span className="o-label">{it.label}</span>
                {it.sub && <span className="o-sub">{it.sub}</span>}
              </button>
            </li>
          ))}
        </ul>
      ))}
    </nav>
  );
}

// ---------------------------------------------------------------- page

function HowItWorks() {
  return (
    <ol className="how-strip">
      <li><strong>Extract.</strong> An agent writes the experiment spec and, separately, what the paper reports. A second agent checks the spec gives nothing away.</li>
      <li><strong>Attach files.</strong> Add any datasets or code the replicator needs.</li>
      <li><strong>Replicate.</strong> Claude Code gets only the spec and files, writes and runs the code, and reports what it measured. No web search.</li>
      <li><strong>Verify.</strong> The personas you pick compare the run with the paper.</li>
    </ol>
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
  const none = experiments !== null && experiments.length === 0;

  async function extract() {
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

  const extractButton = (
    <button className={`btn big ${none ? "dark" : ""}`} disabled={starting || busy} onClick={extract}>
      {Icon.play}
      {busy ? "Extracting…" : starting ? "Starting…" : none ? "Extract the experiment" : "Extract again"}
    </button>
  );

  return (
    <div className="page-wrap replicate-page">
      <div className="page-head">
        <div className="page-title">
          <div className="crumbs">
            <a href="#/">Papers</a> / <a href={`#/paper/${paperId}`}>{paper?.title ?? "Paper"}</a>
          </div>
          <h1>Blind replication</h1>
          <p>Have Claude Code replicate the paper's main experiment without seeing its results, then let personas check the run against the paper.</p>
        </div>
        {!none && extractButton}
      </div>

      {!configured && <p className="warn">No Anthropic API key found. Set ANTHROPIC_API_KEY in backend/.env and restart the server.</p>}
      {error && <p className="error">{error}</p>}

      {none && (
        <div className="card empty-run start-card">
          <h2>Start by extracting the main experiment</h2>
          <HowItWorks />
          <div>{extractButton}</div>
          <p className="muted xsmall">Extraction uses the Claude API and takes a minute or two. Nothing runs code until you start a replication.</p>
        </div>
      )}

      {experiments && experiments.length > 0 && (
        <div className="replicate-layout">
          <Outline experiments={experiments} />
          <div className="replicate-main">
            {experiments.map((e) => (
              <ExperimentCard key={e.id} exp={e} personas={personas} ticks={ticks} onChanged={load} />
            ))}
          </div>
        </div>
      )}

      {!none && experiments && (
        <details className="how-details">
          <summary className="muted small">How blind replication works</summary>
          <HowItWorks />
        </details>
      )}
    </div>
  );
}
