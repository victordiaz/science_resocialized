import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import type { Paper } from "../types";
import { AvatarStack, Icon, clock, runLabel, shortDate } from "../ui";

function Thumb() {
  return (
    <span className="mini-page" aria-hidden>
      <span style={{ background: "#C9C7BF" }} />
      <span />
      <span />
      <span className="block" />
    </span>
  );
}

function authorsShort(a: string[]) {
  if (a.length === 0) return "";
  if (a.length <= 3) return a.join(", ");
  return `${a[0]}, ${a[1]} and ${a.length - 2} others`;
}

function matches(p: Paper, q: string) {
  if (!q) return true;
  const hay = [p.title, p.authors.join(" "), p.abstract ?? "", p.keywords.join(" "), p.venue ?? "", p.field ?? "", p.arxiv_id ?? ""]
    .join(" ")
    .toLowerCase();
  return q.toLowerCase().split(/\s+/).every((w) => hay.includes(w));
}

export default function Library() {
  const [papers, setPapers] = useState<Paper[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [field, setField] = useState("");
  const [year, setYear] = useState("");
  const [keyword, setKeyword] = useState("");
  const [dragOver, setDragOver] = useState(false);

  const load = () => api.papers().then(setPapers).catch((e) => setError(e.message));
  useEffect(() => {
    load();
  }, []);

  // While details are being extracted, refresh every 2 seconds.
  const extracting = (papers ?? []).some((p) => p.metadata_status === "pending" || p.metadata_status === "running");
  useEffect(() => {
    if (!extracting) return;
    const t = window.setInterval(load, 2000);
    return () => window.clearInterval(t);
  }, [extracting]);

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
    }
  }

  async function remove(p: Paper) {
    if (!confirm(`Delete "${p.title}" and all its comments?`)) return;
    await api.deletePaper(p.id);
    load();
  }

  async function reextract(p: Paper) {
    await api.extractMetadata(p.id);
    load();
  }

  const all = papers ?? [];
  const fields = useMemo(() => [...new Set(all.map((p) => p.field).filter(Boolean) as string[])].sort(), [all]);
  const years = useMemo(() => [...new Set(all.map((p) => p.year).filter(Boolean) as number[])].sort((a, b) => b - a), [all]);
  const shown = all.filter(
    (p) =>
      matches(p, query.trim()) &&
      (!field || p.field === field) &&
      (!year || String(p.year) === year) &&
      (!keyword || p.keywords.includes(keyword))
  );
  const filtered = !!(query || field || year || keyword);

  return (
    <div className="page-wrap">
      <div className="page-head">
        <div className="page-title">
          <h1>Papers</h1>
          <p>Upload a PDF, then let your personas and colleagues review it together.</p>
        </div>
        <label className="sr-only" htmlFor="search">Search papers</label>
        <input id="search" className="search" type="search" placeholder="Search titles, authors, abstracts" value={query} onChange={(e) => setQuery(e.target.value)} />
      </div>

      <div className="upload-row">
        <label
          htmlFor="upload"
          className={`dropzone${dragOver ? " over" : ""}`}
          onDragOver={(e) => (e.preventDefault(), setDragOver(true))}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            const f = e.dataTransfer.files[0];
            if (f) upload(f);
          }}
        >
          <span className="dz-icon">{Icon.upload}</span>
          <span className="dz-text">
            <strong>Drop a PDF here, or choose a file</strong>
            <span>We extract each page's words and positions, then read the first pages for the title, authors, venue, year, abstract and keywords.</span>
          </span>
          <input id="upload" type="file" accept="application/pdf" className="sr-only" onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} />
        </label>
        {uploading && (
          <div className="card processing">
            <div><strong>Processing</strong> <span className="muted small">1 file</span></div>
            <div className="small">{uploading}</div>
            <div className="bar indeterminate" role="progressbar" aria-label="Extracting pages"><span /></div>
            <div className="muted small">Extracting words and positions</div>
          </div>
        )}
      </div>

      {error && <p className="error">{error}</p>}

      {(fields.length > 0 || years.length > 0 || keyword) && (
        <div className="filters" aria-label="Filter papers">
          {fields.length > 0 && (
            <label>
              <span className="sr-only">Field</span>
              <select value={field} onChange={(e) => setField(e.target.value)}>
                <option value="">All fields</option>
                {fields.map((f) => <option key={f} value={f}>{f}</option>)}
              </select>
            </label>
          )}
          {years.length > 0 && (
            <label>
              <span className="sr-only">Year</span>
              <select value={year} onChange={(e) => setYear(e.target.value)}>
                <option value="">Any year</option>
                {years.map((y) => <option key={y} value={y}>{y}</option>)}
              </select>
            </label>
          )}
          {keyword && (
            <button className="chip-btn on" onClick={() => setKeyword("")} aria-label={`Remove keyword filter ${keyword}`}>
              {keyword} ×
            </button>
          )}
          {filtered && (
            <button className="link small" onClick={() => (setQuery(""), setField(""), setYear(""), setKeyword(""))}>Clear filters</button>
          )}
          <span className="spacer" />
          <span className="muted small">{shown.length} of {all.length} papers</span>
        </div>
      )}

      <section className="card table-card" aria-label="All papers">
        <table className="papers">
          <thead>
            <tr>
              <th scope="col">Paper</th>
              <th scope="col">Pages</th>
              <th scope="col">Threads</th>
              <th scope="col">Reviewers</th>
              <th scope="col">Last review run</th>
              <th scope="col"><span className="sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody>
            {papers && shown.length === 0 && (
              <tr>
                <td colSpan={6} className="empty-cell">
                  {all.length === 0 ? "No papers yet. Upload a PDF to start a review." : "No papers match these filters."}
                </td>
              </tr>
            )}
            {shown.map((p) => {
              const busy = p.metadata_status === "pending" || p.metadata_status === "running";
              const where = [p.venue, p.year].filter(Boolean).join(" ");
              return (
                <tr key={p.id}>
                  <td className="paper-col">
                    <a href={`#/paper/${p.id}`} className="paper-cell" title={p.abstract ?? undefined}>
                      <Thumb />
                      <span>
                        <span className="paper-title">{p.title}</span>
                        {(p.authors.length > 0 || where) && (
                          <span className="paper-byline small">{[authorsShort(p.authors), where].filter(Boolean).join(" · ")}</span>
                        )}
                        <span className="muted xsmall">
                          {busy ? "Reading details…" : `Uploaded ${shortDate(p.created_at)}`}
                          {p.metadata_status === "failed" && " · details could not be read"}
                        </span>
                      </span>
                    </a>
                    {(p.field || p.keywords.length > 0) && (
                      <span className="tags">
                        {p.field && (
                          <button className={`tag field${field === p.field ? " on" : ""}`} onClick={() => setField(field === p.field ? "" : p.field!)}>
                            {p.field}
                          </button>
                        )}
                        {p.keywords.slice(0, 5).map((k) => (
                          <button key={k} className={`tag${keyword === k ? " on" : ""}`} onClick={() => setKeyword(keyword === k ? "" : k)}>
                            {k}
                          </button>
                        ))}
                      </span>
                    )}
                  </td>
                  <td className="num">{p.page_count}</td>
                  <td>
                    <span className="counts">
                      <span className="chip strong">{p.open_count} open</span>
                      <span className="muted small">{p.resolved_count} resolved</span>
                    </span>
                  </td>
                  <td><AvatarStack authors={p.participants} size={26} /></td>
                  <td>
                    {p.last_run ? (
                      <span className="stack">
                        <span className="small">{runLabel(p.last_run)}</span>
                        <span className="muted small">{shortDate(p.last_run.created_at)}, {clock(p.last_run.created_at)}</span>
                      </span>
                    ) : (
                      <span className="small">Not reviewed yet</span>
                    )}
                  </td>
                  <td className="actions">
                    <a className="btn" href={`#/paper/${p.id}/run`}>Run review</a>
                    <a className="btn" href={`#/paper/${p.id}/replicate`}>Replicate</a>
                    <details className="more">
                      <summary className="btn ghost" aria-label={`More actions for ${p.title}`}>…</summary>
                      <div className="more-menu">
                        <button onClick={() => reextract(p)} disabled={busy}>Re-read details</button>
                        <button className="danger" onClick={() => remove(p)}>Delete paper</button>
                      </div>
                    </details>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </section>
    </div>
  );
}
