import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { GlobalWorkerOptions, getDocument, type PDFDocumentProxy } from "pdfjs-dist";
import workerUrl from "pdfjs-dist/build/pdf.worker.min.mjs?url";
import { api } from "../api";
import PdfPage from "../components/PdfPage";
import ThreadCard from "../components/ThreadCard";
import MentionInput from "../components/MentionInput";
import type { Paper, PendingAnchor, Persona, Run, Thread } from "../types";
import { AvatarStack, HUMAN_COLOR, Icon, Loader, plural, shortDate } from "../ui";

GlobalWorkerOptions.workerSrc = workerUrl;

function authorList(a: string[], max = 4) {
  if (a.length <= max) return a.join(", ");
  return `${a.slice(0, max - 1).join(", ")} and ${a.length - (max - 1)} others`;
}

function bylineText(p: Paper) {
  const where = [p.venue, p.year].filter(Boolean).join(" ");
  return [authorList(p.authors), where].filter(Boolean).join(" · ");
}

type Typing = Record<string, { name: string; color: string }[]>;
type Scope = "page" | "all";

const authorKey = (a: { type: string; id: string | null }) => (a.type === "human" ? "humans" : (a.id as string));

export default function PaperView({ paperId }: { paperId: string }) {
  const [paper, setPaper] = useState<Paper | null>(null);
  const [doc, setDoc] = useState<PDFDocumentProxy | null>(null);
  const [threads, setThreads] = useState<Thread[]>([]);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [pending, setPending] = useState<PendingAnchor>(null);
  const [general, setGeneral] = useState(false);
  const [draft, setDraft] = useState("");
  const [tool, setTool] = useState<"text" | "box">("text");
  const [scale, setScale] = useState(1);
  const [page, setPage] = useState(1);
  const [scope, setScope] = useState<Scope>("page");
  const [authorFilter, setAuthorFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<"open" | "resolved">("open");
  const [typing, setTyping] = useState<Typing>({});

  const pageEls = useRef<Map<number, HTMLDivElement>>(new Map());
  const cardEls = useRef<Map<string, HTMLElement>>(new Map());
  const scrollerRef = useRef<HTMLDivElement>(null);
  const fitted = useRef(false);

  const loadPaper = useCallback(() => api.paper(paperId).then(setPaper).catch((e) => setError(e.message)), [paperId]);
  const loadThreads = useCallback(() => api.threads(paperId).then(setThreads).catch((e) => setError(e.message)), [paperId]);
  const loadRuns = useCallback(() => api.runs(paperId).then(setRuns).catch(() => undefined), [paperId]);

  useEffect(() => {
    loadPaper();
    api.personas().then(setPersonas);
    loadThreads();
    loadRuns();
    let cancelled = false;
    const task = getDocument(api.paperFileUrl(paperId));
    task.promise.then(setDoc).catch((e) => !cancelled && setError(`Could not load PDF: ${e.message}`));
    return () => {
      cancelled = true;
      task.destroy();
    };
  }, [paperId, loadPaper, loadThreads, loadRuns]);

  // Fit the page width to the reading column once.
  useEffect(() => {
    const w = paper?.pages?.[0]?.width;
    const desk = scrollerRef.current;
    if (!w || !desk || fitted.current) return;
    fitted.current = true;
    setScale(Math.max(0.6, Math.min(1.6, +((desk.clientWidth - 64) / w).toFixed(2))));
  }, [paper]);

  // Live updates.
  useEffect(() => {
    const es = new EventSource(api.eventsUrl(paperId));
    let t: number | undefined;
    const refreshThreads = () => {
      clearTimeout(t);
      t = window.setTimeout(() => {
        loadThreads();
        loadPaper();
      }, 150);
    };
    es.onmessage = (m) => {
      const ev = JSON.parse(m.data);
      if (ev.type.startsWith("thread.") || ev.type.startsWith("comment.")) refreshThreads();
      else if (ev.type === "paper.updated") loadPaper();
      else if (ev.type === "run.updated") loadRuns();
      else if (ev.type === "live.started" || ev.type === "live.finished") {
        setTyping((cur) => {
          const list = (cur[ev.thread_id] ?? []).filter((x) => x.name !== ev.persona_name);
          if (ev.type === "live.started") list.push({ name: ev.persona_name, color: ev.persona_color });
          return { ...cur, [ev.thread_id]: list };
        });
        if (ev.error) setError(`${ev.persona_name} could not reply: ${ev.error}`);
      }
    };
    return () => {
      es.close();
      clearTimeout(t);
    };
  }, [paperId, loadThreads, loadRuns, loadPaper]);

  // Track the page in view.
  useEffect(() => {
    const desk = scrollerRef.current;
    if (!desk) return;
    let raf = 0;
    const onScroll = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const line = desk.scrollTop + desk.clientHeight / 3;
        let current = 1;
        for (const [n, el] of pageEls.current) if (el.offsetTop <= line && n > current) current = n;
        setPage(current);
      });
    };
    desk.addEventListener("scroll", onScroll, { passive: true });
    return () => desk.removeEventListener("scroll", onScroll);
  }, [doc, paper]);

  // Stable numbers: reading order over all threads.
  const numbers = useMemo(() => new Map(threads.map((t, i) => [t.id, i + 1])), [threads]);

  const runningRun = runs.find((r) => r.status === "running" || r.status === "queued");

  const authors = useMemo(() => {
    const m = new Map<string, { key: string; name: string; color: string }>();
    for (const t of threads)
      for (const c of t.comments) {
        const key = authorKey(c.author);
        if (!m.has(key)) m.set(key, { key, name: c.author.type === "human" ? "Humans" : c.author.name, color: c.author.type === "human" ? HUMAN_COLOR : c.author.color });
      }
    return [...m.values()].sort((a, b) => (a.key === "humans" ? 1 : b.key === "humans" ? -1 : 0));
  }, [threads]);

  const inScope = useMemo(
    () =>
      threads.filter((t) => {
        if (scope === "page" && t.anchor && t.anchor.page !== page) return false;
        if (authorFilter !== "all" && !t.comments.some((c) => authorKey(c.author) === authorFilter)) return false;
        return true;
      }),
    [threads, scope, page, authorFilter]
  );
  const openCount = inScope.filter((t) => t.status === "open").length;
  const resolvedCount = inScope.length - openCount;
  const visibleThreads = inScope.filter((t) => t.status === statusFilter);

  const pageCounts = useMemo(() => {
    const m = new Map<number, number>();
    for (const t of threads) if (t.anchor && t.status === "open") m.set(t.anchor.page, (m.get(t.anchor.page) ?? 0) + 1);
    return m;
  }, [threads]);

  // Marks on the PDF follow the author filter and show both open and resolved threads.
  const byPage = useMemo(() => {
    const m = new Map<number, Thread[]>();
    for (const t of threads) {
      if (!t.anchor || !t.anchor.rects.length) continue;
      if (authorFilter !== "all" && !t.comments.some((c) => authorKey(c.author) === authorFilter)) continue;
      m.set(t.anchor.page, [...(m.get(t.anchor.page) ?? []), t]);
    }
    return m;
  }, [threads, authorFilter]);

  function goToPage(n: number, y = 0) {
    const el = pageEls.current.get(n);
    const desk = scrollerRef.current;
    if (!el || !desk) return;
    desk.scrollTo({ top: el.offsetTop + y * el.offsetHeight - (y ? desk.clientHeight / 3 : 16), behavior: "smooth" });
  }

  function selectFromPage(id: string | null) {
    setSelected(id);
    const t = threads.find((x) => x.id === id);
    if (t && t.status !== statusFilter) setStatusFilter(t.status);
    if (id) requestAnimationFrame(() => cardEls.current.get(id)?.scrollIntoView({ behavior: "smooth", block: "nearest" }));
  }

  function selectFromSidebar(t: Thread) {
    const next = selected === t.id ? null : t.id;
    setSelected(next);
    if (next && t.anchor) goToPage(t.anchor.page, t.anchor.rects[0]?.y0 ?? 0);
  }

  async function postNew() {
    if (!draft.trim()) return;
    setError(null);
    try {
      const anchor = pending ? { page: pending.page, rects: pending.rects, quote: pending.quote } : null;
      const t = await api.createThread(paperId, draft, anchor);
      setDraft("");
      setPending(null);
      setGeneral(false);
      setStatusFilter("open");
      window.getSelection()?.removeAllRanges();
      await loadThreads();
      setSelected(t.id);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  if (!paper) return <div className="center muted">{error ?? <><Loader size={32} label="Loading" /> Loading paper…</>}</div>;

  const reviewers = (paper.participants ?? []).filter((a) => a.type === "persona");
  const lastRun = paper.last_run;
  const meta = [
    plural(paper.page_count, "page"),
    `uploaded ${shortDate(paper.created_at)}`,
    lastRun
      ? `last review run ${lastRun.rounds === 0 ? "solo" : plural(lastRun.rounds, "round")}, ${shortDate(lastRun.created_at)}`
      : "not reviewed yet",
  ].join(" · ");

  return (
    <div className="workspace">
      <div className="paper-header">
        <div className="paper-heading">
          <div className="crumbs"><a href="#/">Papers</a> / Paper</div>
          <h1 title={paper.abstract ?? undefined}>{paper.title}</h1>
          {(paper.authors.length > 0 || paper.venue || paper.year) && (
            <div className="byline small">{bylineText(paper)}</div>
          )}
          <div className="muted small">{meta}</div>
        </div>
        <div className="paper-actions">
          <AvatarStack authors={reviewers} label="Personas on this paper" />
          <a className="btn big" href={`#/paper/${paperId}/replicate`}>Replicate</a>
          <a className="btn dark big" href={`#/paper/${paperId}/run`}>
            {Icon.play}
            {runningRun ? "Review running" : "Run review"}
          </a>
        </div>
      </div>

      <div className="workspace-body">
        <aside className="rail" aria-label="Pages">
          {paper.pages!.map((pg) => {
            const count = pageCounts.get(pg.number) ?? 0;
            return (
              <button key={pg.number} className={`rail-page${pg.number === page ? " current" : ""}`} onClick={() => goToPage(pg.number)} aria-label={`Page ${pg.number}, ${plural(count, "open thread")}`}>
                <span className="rail-thumb" style={{ aspectRatio: `${pg.width} / ${pg.height}` }}>
                  <img src={api.pageImageUrl(paperId, pg.number)} alt="" loading="lazy" />
                  {count > 0 && <span className="rail-count">{count}</span>}
                </span>
                <span className="rail-num">{pg.number}</span>
              </button>
            );
          })}
        </aside>

        <section className="reader">
          <div className="toolbar" role="toolbar" aria-label="Page tools">
            <div className="segmented">
              <button aria-pressed={tool === "text"} onClick={() => setTool("text")}>{Icon.text}Highlight text</button>
              <button aria-pressed={tool === "box"} onClick={() => setTool("box")}>{Icon.box}Draw box</button>
            </div>
            <span className="muted small">{tool === "text" ? "Select words on the page to start a thread" : "Drag a box over a figure, table or equation"}</span>
            <span className="spacer" />
            <div className="pager">
              <button className="icon-btn" aria-label="Previous page" disabled={page <= 1} onClick={() => goToPage(page - 1)}>{Icon.prev}</button>
              <span className="pager-label">Page {page} / {paper.page_count}</span>
              <button className="icon-btn" aria-label="Next page" disabled={page >= paper.page_count} onClick={() => goToPage(page + 1)}>{Icon.next}</button>
              <span className="zoom">
                <button aria-label="Zoom out" onClick={() => setScale((s) => Math.max(0.5, +(s - 0.1).toFixed(2)))}>−</button>
                <span>{Math.round(scale * 100)}%</span>
                <button aria-label="Zoom in" onClick={() => setScale((s) => Math.min(3, +(s + 0.1).toFixed(2)))}>+</button>
              </span>
            </div>
          </div>

          <div className={`desk${tool === "box" ? " box-mode" : ""}`} ref={scrollerRef}>
            {!doc && <div className="center muted">Rendering PDF…</div>}
            {doc &&
              paper.pages!.map((pg) => (
                <PdfPage
                  key={pg.number}
                  doc={doc}
                  number={pg.number}
                  width={pg.width}
                  height={pg.height}
                  scale={scale}
                  threads={byPage.get(pg.number) ?? []}
                  numbers={numbers}
                  selectedId={selected}
                  pending={pending}
                  boxMode={tool === "box"}
                  onSelectThread={selectFromPage}
                  onAnchor={(a) => {
                    setPending(a);
                    setGeneral(false);
                    setSelected(null);
                  }}
                  registerRef={(n, el) => (el ? pageEls.current.set(n, el) : pageEls.current.delete(n))}
                />
              ))}
          </div>
        </section>

        <aside className="threads-panel" aria-label="Comment threads">
          <div className="threads-head">
            <div className="threads-title">
              <h2>Threads</h2>
              <button className="link small muted-link" onClick={() => setScope(scope === "page" ? "all" : "page")} title="Switch between this page and the whole paper">
                {scope === "page" ? `page ${page}` : "all pages"}
              </button>
              <span className="spacer" />
              <div className="tabs" role="tablist" aria-label="Thread status">
                <button role="tab" aria-selected={statusFilter === "open"} onClick={() => setStatusFilter("open")}>Open {openCount}</button>
                <button role="tab" aria-selected={statusFilter === "resolved"} onClick={() => setStatusFilter("resolved")}>Resolved {resolvedCount}</button>
              </div>
            </div>
            {authors.length > 0 && (
              <div className="chips" aria-label="Filter by author">
                <button className={`chip-btn${authorFilter === "all" ? " on" : ""}`} onClick={() => setAuthorFilter("all")}>All</button>
                {authors.map((a) => (
                  <button key={a.key} className={`chip-btn${authorFilter === a.key ? " on" : ""}`} onClick={() => setAuthorFilter(authorFilter === a.key ? "all" : a.key)}>
                    <span className="dot" style={{ background: a.color }} aria-hidden />
                    {a.name}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="threads-list">
            {error && (
              <p className="error" onClick={() => setError(null)}>
                {error}
              </p>
            )}

            {pending || general ? (
              <section className="thread composer selected">
                <div className="thread-anchor">
                  <span className="loc">{pending ? `p.${pending.page} · ${pending.quote ? "quote" : "box"}` : "Whole paper"}</span>
                  {pending?.quote && <span className="quote">“{pending.quote}”</span>}
                </div>
                <label className="field-label" htmlFor="new-comment">New thread · type @ to ask a persona</label>
                <MentionInput id="new-comment" value={draft} onChange={setDraft} onSubmit={postNew} personas={personas} autoFocus placeholder="Write a comment…" />
                <div className="row end">
                  <button className="btn" onClick={() => (setPending(null), setGeneral(false), setDraft(""))}>Cancel</button>
                  <button className="btn dark" onClick={postNew} disabled={!draft.trim()}>Comment</button>
                </div>
              </section>
            ) : (
              <button className="link small whole" onClick={() => setGeneral(true)}>Comment on the whole paper</button>
            )}

            {visibleThreads.length === 0 && (
              <p className="empty">
                {threads.length === 0
                  ? "No comments yet. Run a review to get the personas started, or select text to comment."
                  : statusFilter === "resolved"
                    ? "No resolved threads here."
                    : scope === "page"
                      ? `No open threads on page ${page}.`
                      : "No open threads match this filter."}
              </p>
            )}

            {visibleThreads.map((t) => (
              <ThreadCard
                key={t.id}
                ref={(el) => (el ? cardEls.current.set(t.id, el) : cardEls.current.delete(t.id))}
                thread={t}
                number={numbers.get(t.id) ?? 0}
                personas={personas}
                selected={t.id === selected}
                typing={typing[t.id] ?? []}
                onSelect={() => selectFromSidebar(t)}
                onChanged={() => (loadThreads(), loadPaper())}
              />
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}
