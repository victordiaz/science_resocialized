import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import type { Paper } from "../types";
import { Avatar, Icon, Loader, shortDate } from "../ui";

/** "Row.116 — Does averaging…" → source tag "Row.116" + the real title. */
function splitSource(title: string): { source: string | null; title: string } {
  const m = title.match(/^(\S{2,16})\s+[—–-]\s+(.+)$/);
  if (m && /\d/.test(m[1])) return { source: m[1], title: m[2] };
  return { source: null, title };
}

function authorsText(a: string[]) {
  if (a.length === 0) return "";
  const last = (n: string) => n.trim().split(/\s+/).pop() ?? n;
  if (a.length <= 3) return a.map(last).join(", ");
  return `${last(a[0])}, ${last(a[1])} and ${a.length - 2} others`;
}

function matches(p: Paper, q: string) {
  if (!q) return true;
  const hay = [p.title, p.authors.join(" "), p.abstract ?? "", p.keywords.join(" "), p.venue ?? "", p.field ?? "", p.arxiv_id ?? ""]
    .join(" ")
    .toLowerCase();
  return q.toLowerCase().split(/\s+/).every((w) => hay.includes(w));
}

type RepLook = { label: string; tone: "live" | "good" | "warn" | "bad" | "idle" };

/** One line on where the paper's blind replication stands; after a run, what it found. */
function replicationLook(r: Paper["replication"] | undefined): RepLook | null {
  if (!r) return null;
  const verdict = (r.verdict ?? "").toLowerCase();
  switch (r.status) {
    case "none":
      return null;
    case "extracting":
      return { label: "Extracting experiment", tone: "live" };
    case "needs_you":
      return { label: "Replication needs you", tone: "warn" };
    case "ready":
      return { label: "Spec ready to replicate", tone: "idle" };
    case "running":
      return { label: "Replicating", tone: "live" };
    case "verifying":
      return { label: "Verifying replication", tone: "live" };
    case "failed":
      return { label: "Replication failed", tone: "bad" };
    default:
      if (/\b(not|failed to|did not|could not)\b.*\b(replicat|reproduc)/.test(verdict) || verdict.startsWith("not replicated"))
        return { label: "Not replicated", tone: "warn" };
      if (/\bpartial/.test(verdict)) return { label: "Partly replicated", tone: "idle" };
      if (/\b(replicated|reproduced)\b/.test(verdict)) return { label: "Replicated", tone: "good" };
      return { label: r.status === "verified" ? "Replication verified" : "Replication finished", tone: "idle" };
  }
}

const needsYou = (p: Paper) => p.replication?.status === "needs_you" || p.metadata_status === "failed";
const notReviewed = (p: Paper) => !p.last_run;

function Cover({ p }: { p: Paper }) {
  const [failed, setFailed] = useState(false);
  return (
    <a href={`#/paper/${p.id}`} className="cover-lg" aria-label={`Open ${p.title}`}>
      {failed ? <span className="cover-blank" /> : <img src={api.pageImageUrl(p.id, 1, 72)} alt="" loading="lazy" onError={() => setFailed(true)} />}
    </a>
  );
}

function RowMenu({ p, onReextract, onDelete }: { p: Paper; onReextract: () => void; onDelete: () => void }) {
  const ref = useRef<HTMLDetailsElement>(null);
  useEffect(() => {
    const close = (e: MouseEvent) => ref.current && !ref.current.contains(e.target as Node) && (ref.current.open = false);
    document.addEventListener("click", close);
    return () => document.removeEventListener("click", close);
  }, []);
  const busy = p.metadata_status === "pending" || p.metadata_status === "running";
  return (
    <details className="more" ref={ref}>
      <summary className="icon-btn ghost-icon" aria-label={`More actions for ${p.title}`}>
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <circle cx="3" cy="8" r="1.3" fill="currentColor" /><circle cx="8" cy="8" r="1.3" fill="currentColor" /><circle cx="13" cy="8" r="1.3" fill="currentColor" />
        </svg>
      </summary>
      <div className="more-menu">
        <a href={`#/paper/${p.id}`}>Open paper</a>
        <a href={`#/paper/${p.id}/run`}>Run review</a>
        <a href={`#/paper/${p.id}/replicate`}>Blind replication</a>
        <button onClick={onReextract} disabled={busy}>Re-read details</button>
        <button className="danger" onClick={onDelete}>Delete paper</button>
      </div>
    </details>
  );
}

type Filter = "all" | "needs" | "unreviewed";

export default function Library() {
  const [papers, setPapers] = useState<Paper[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("all");
  const [field, setField] = useState("");
  const [dragging, setDragging] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);

  const load = () => api.papers().then(setPapers).catch((e) => setError(e.message));
  useEffect(() => {
    load();
  }, []);

  // While details are read or a replication is in progress, refresh every few seconds.
  const live = (papers ?? []).some(
    (p) => p.metadata_status === "pending" || p.metadata_status === "running" || ["extracting", "running", "verifying"].includes(p.replication?.status)
  );
  useEffect(() => {
    if (!live) return;
    const t = window.setInterval(load, 3000);
    return () => window.clearInterval(t);
  }, [live]);

  async function upload(f: File) {
    if (f.type && f.type !== "application/pdf") {
      setError(`${f.name} is not a PDF.`);
      return;
    }
    setUploading(f.name);
    setError(null);
    try {
      await api.uploadPaper(f);
      await load();
    } catch (e) {
      setError(`Could not upload ${f.name}: ${(e as Error).message}`);
    } finally {
      setUploading(null);
      if (fileInput.current) fileInput.current.value = "";
    }
  }

  // Drop a PDF anywhere on the page.
  useEffect(() => {
    let depth = 0;
    const hasFiles = (e: DragEvent) => [...(e.dataTransfer?.types ?? [])].includes("Files");
    const enter = (e: DragEvent) => hasFiles(e) && (depth++, setDragging(true));
    const leave = (e: DragEvent) => hasFiles(e) && --depth <= 0 && (depth = 0, setDragging(false));
    const over = (e: DragEvent) => hasFiles(e) && e.preventDefault();
    const drop = (e: DragEvent) => {
      if (!hasFiles(e)) return;
      e.preventDefault();
      depth = 0;
      setDragging(false);
      const f = e.dataTransfer?.files[0];
      if (f) upload(f);
    };
    window.addEventListener("dragenter", enter);
    window.addEventListener("dragleave", leave);
    window.addEventListener("dragover", over);
    window.addEventListener("drop", drop);
    return () => {
      window.removeEventListener("dragenter", enter);
      window.removeEventListener("dragleave", leave);
      window.removeEventListener("dragover", over);
      window.removeEventListener("drop", drop);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function remove(p: Paper) {
    if (!confirm(`Delete "${p.title}" and all its comments?`)) return;
    await api.deletePaper(p.id);
    load();
  }

  const all = papers ?? [];
  const counts = { all: all.length, needs: all.filter(needsYou).length, unreviewed: all.filter(notReviewed).length };
  const shown = all.filter(
    (p) =>
      matches(p, query.trim()) &&
      (!field || p.field === field) &&
      (filter === "all" || (filter === "needs" ? needsYou(p) : notReviewed(p)))
  );

  const chip = (id: Filter, label: string, n: number) => (
    <button className={`fchip${filter === id ? " on" : ""}`} aria-pressed={filter === id} onClick={() => setFilter(id)}>
      {label} {n}
    </button>
  );

  return (
    <div className="page-wrap papers-list">
      {dragging && (
        <div className="drop-overlay" aria-hidden>
          <div>
            <span className="dz-icon">{Icon.upload}</span>
            <strong>Drop the PDF to upload it</strong>
          </div>
        </div>
      )}

      <div className="pl-head">
        <h1>Papers</h1>
        <label className="sr-only" htmlFor="search">Search papers</label>
        <input id="search" className="search" type="search" placeholder="Search titles, authors, tags" value={query} onChange={(e) => setQuery(e.target.value)} />
        <label className="btn dark big upload-btn">
          {Icon.upload}
          Upload PDF
          <input ref={fileInput} type="file" accept="application/pdf" className="sr-only" onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} />
        </label>
      </div>

      <div className="pl-filters">
        {chip("all", "All", counts.all)}
        {chip("needs", "Needs you", counts.needs)}
        {chip("unreviewed", "Not reviewed", counts.unreviewed)}
        {field && (
          <button className="fchip on" onClick={() => setField("")} aria-label={`Remove field filter ${field}`}>
            {field} ×
          </button>
        )}
        <span className="spacer" />
        <span className="muted small">Drop a PDF anywhere on this page to upload</span>
      </div>

      {error && <p className="error">{error}</p>}

      <ul className="pl-list" aria-label="Papers">
        {uploading && (
          <li className="pl-row">
            <span className="cover-lg cover-uploading" aria-hidden><Loader size={32} /></span>
            <div className="pl-upload">
              <div className="pl-upload-head">
                <span className="strong-ish">{uploading}</span>
                <span className="muted small">Extracting words and positions</span>
              </div>
              <div className="bar indeterminate" role="progressbar" aria-label="Upload progress"><span /></div>
            </div>
          </li>
        )}
        {papers && shown.length === 0 && !uploading && (
          <li className="pl-empty">{all.length === 0 ? <><Loader kind="gather" size={48} /> No papers yet. Upload a PDF, or drop one anywhere on this page.</> : "No papers match."}</li>
        )}
        {shown.map((p) => {
          const { source, title } = splitSource(p.title);
          const reading = p.metadata_status === "pending" || p.metadata_status === "running";
          const meta = [authorsText(p.authors), [p.venue, p.year].filter(Boolean).join(" "), `${p.page_count} ${p.page_count === 1 ? "page" : "pages"}`, `uploaded ${shortDate(p.created_at)}`]
            .filter(Boolean)
            .join(" · ");
          const who = p.participants ?? [];
          const rep = replicationLook(p.replication);
          const threads = p.open_count > 0 ? `${p.open_count} open` : p.resolved_count > 0 ? "All resolved" : "No threads";
          return (
            <li key={p.id} className="pl-row">
              <Cover p={p} />
              <div className="pl-main">
                <div className="pl-kicker">
                  {p.field ? (
                    <button className="pl-field" onClick={() => setField(field === p.field ? "" : p.field!)} title="Show only this field">{p.field}</button>
                  ) : (
                    <span>{reading ? "Reading details…" : "Paper"}</span>
                  )}
                  {source && <span className="pl-source">{source}</span>}
                </div>
                <a href={`#/paper/${p.id}`} className="pl-title" title={p.abstract ?? undefined}>{title}</a>
                <div className="pl-meta">{meta}</div>
                <div className="pl-status">
                  <a href={`#/paper/${p.id}`} className={`pl-threads${p.open_count > 0 ? " has" : ""}`}>
                    <svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                      <path d="M2.5 3.5h11v7h-6l-3 2.5v-2.5h-2z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
                    </svg>
                    {threads}
                  </a>
                  {p.last_run ? (
                    <a href={`#/paper/${p.id}/run`} className="pl-reviewed">
                      <span className="pl-who" aria-label={who.map((w) => w.name).join(", ")}>
                        {who.slice(0, 3).map((w, i) => <Avatar key={w.name + i} name={w.name} color={w.color} size={22} title={w.name} />)}
                        {who.length > 3 && <span className="pl-who-more">+{who.length - 3}</span>}
                      </span>
                      Reviewed {shortDate(p.last_run.created_at)}
                    </a>
                  ) : (
                    <a href={`#/paper/${p.id}/run`} className="pl-action">Run first review</a>
                  )}
                  {rep ? (
                    <a href={`#/paper/${p.id}/replicate`} className={`pl-rep t-${rep.tone}`} title={p.replication.verdict ?? undefined}>
                      <span className="pl-dot" aria-hidden />
                      {rep.label}
                    </a>
                  ) : (
                    <a href={`#/paper/${p.id}/replicate`} className="pl-replicate">Replicate</a>
                  )}
                </div>
              </div>
              <RowMenu p={p} onReextract={() => api.extractMetadata(p.id).then(load)} onDelete={() => remove(p)} />
            </li>
          );
        })}
      </ul>
    </div>
  );
}
