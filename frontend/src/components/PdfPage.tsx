import { useEffect, useRef, useState } from "react";
import { TextLayer, type PDFDocumentProxy, type RenderTask } from "pdfjs-dist";
import type { PendingAnchor, Rect, Thread } from "../types";
import { withAlpha } from "../ui";

type Props = {
  doc: PDFDocumentProxy;
  number: number;
  width: number; // PDF points
  height: number;
  scale: number;
  threads: Thread[];
  numbers: Map<string, number>;
  selectedId: string | null;
  pending: PendingAnchor;
  boxMode: boolean;
  onSelectThread: (id: string | null) => void;
  onAnchor: (a: NonNullable<PendingAnchor>) => void;
  registerRef: (n: number, el: HTMLDivElement | null) => void;
};

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

/** Merge selection client rects into one rect per visual line. */
function mergeLines(rects: Rect[]): Rect[] {
  const sorted = [...rects].sort((a, b) => a.y0 - b.y0 || a.x0 - b.x0);
  const out: Rect[] = [];
  for (const r of sorted) {
    const last = out[out.length - 1];
    const sameLine = last && Math.abs((last.y0 + last.y1) / 2 - (r.y0 + r.y1) / 2) < (r.y1 - r.y0) * 0.6;
    if (sameLine) {
      last.x0 = Math.min(last.x0, r.x0);
      last.x1 = Math.max(last.x1, r.x1);
      last.y0 = Math.min(last.y0, r.y0);
      last.y1 = Math.max(last.y1, r.y1);
    } else out.push({ ...r });
  }
  return out;
}

export default function PdfPage(p: Props) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  const [drag, setDrag] = useState<{ x: number; y: number; x2: number; y2: number } | null>(null);
  const cssW = p.width * p.scale;
  const cssH = p.height * p.scale;

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => e.isIntersecting && setVisible(true), { rootMargin: "800px 0px" });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  useEffect(() => {
    if (!visible) return;
    let cancelled = false;
    let task: RenderTask | null = null;
    let textLayer: TextLayer | null = null;
    (async () => {
      const page = await p.doc.getPage(p.number);
      if (cancelled) return;
      const viewport = page.getViewport({ scale: p.scale });
      const canvas = canvasRef.current!;
      const dpr = window.devicePixelRatio || 1;
      canvas.width = Math.floor(viewport.width * dpr);
      canvas.height = Math.floor(viewport.height * dpr);
      const ctx = canvas.getContext("2d")!;
      task = page.render({ canvasContext: ctx, viewport, transform: dpr !== 1 ? [dpr, 0, 0, dpr, 0, 0] : undefined });
      try {
        await task.promise;
      } catch {
        return; // cancelled
      }
      if (cancelled || !textRef.current) return;
      textRef.current.replaceChildren();
      textLayer = new TextLayer({ textContentSource: page.streamTextContent(), container: textRef.current, viewport });
      await textLayer.render().catch(() => undefined);
    })();
    return () => {
      cancelled = true;
      task?.cancel();
      textLayer?.cancel();
    };
  }, [visible, p.doc, p.number, p.scale]);

  function toNorm(clientX: number, clientY: number) {
    const b = wrapRef.current!.getBoundingClientRect();
    return { x: clamp01((clientX - b.left) / b.width), y: clamp01((clientY - b.top) / b.height) };
  }

  function onMouseUp(e: React.MouseEvent) {
    if (p.boxMode) return;
    const sel = window.getSelection();
    if (sel && !sel.isCollapsed && sel.rangeCount && textRef.current?.contains(sel.anchorNode)) {
      const b = wrapRef.current!.getBoundingClientRect();
      const rects: Rect[] = Array.from(sel.getRangeAt(0).getClientRects())
        .filter((r) => r.width > 1 && r.height > 1 && r.bottom > b.top && r.top < b.bottom)
        .map((r) => ({
          x0: clamp01((r.left - b.left) / b.width),
          y0: clamp01((r.top - b.top) / b.height),
          x1: clamp01((r.right - b.left) / b.width),
          y1: clamp01((r.bottom - b.top) / b.height),
        }));
      const quote = sel.toString().replace(/\s+/g, " ").trim();
      if (rects.length && quote) {
        p.onAnchor({ page: p.number, rects: mergeLines(rects), quote });
        return;
      }
    }
    // Plain click: select the thread under the pointer, if any.
    const { x, y } = toNorm(e.clientX, e.clientY);
    const hit = p.threads.find((t) => t.anchor?.rects.some((r) => x >= r.x0 && x <= r.x1 && y >= r.y0 && y <= r.y1));
    if (hit) p.onSelectThread(hit.id);
  }

  function onBoxDown(e: React.PointerEvent) {
    const { x, y } = toNorm(e.clientX, e.clientY);
    (e.target as Element).setPointerCapture(e.pointerId);
    setDrag({ x, y, x2: x, y2: y });
  }
  function onBoxMove(e: React.PointerEvent) {
    if (!drag) return;
    const { x, y } = toNorm(e.clientX, e.clientY);
    setDrag({ ...drag, x2: x, y2: y });
  }
  function onBoxUp() {
    if (!drag) return;
    const r = { x0: Math.min(drag.x, drag.x2), y0: Math.min(drag.y, drag.y2), x1: Math.max(drag.x, drag.x2), y1: Math.max(drag.y, drag.y2) };
    setDrag(null);
    if (r.x1 - r.x0 > 0.01 && r.y1 - r.y0 > 0.005) p.onAnchor({ page: p.number, rects: [r], quote: null });
  }

  const pct = (r: Rect) => ({
    left: `${r.x0 * 100}%`,
    top: `${r.y0 * 100}%`,
    width: `${(r.x1 - r.x0) * 100}%`,
    height: `${(r.y1 - r.y0) * 100}%`,
  });

  return (
    <div
      ref={(el) => {
        (wrapRef as React.MutableRefObject<HTMLDivElement | null>).current = el;
        p.registerRef(p.number, el);
      }}
      className="pdf-page"
      style={{ width: cssW, height: cssH, ["--scale-factor" as string]: p.scale, ["--total-scale-factor" as string]: p.scale }}
      onMouseUp={onMouseUp}
      data-page={p.number}
    >
      <canvas ref={canvasRef} style={{ width: cssW, height: cssH }} />
      <div className="marks" aria-hidden>
        {p.threads.map((t) => {
          const color = t.comments[0]?.author.color ?? "#888";
          const sel = t.id === p.selectedId;
          const box = t.anchor!.kind === "box";
          const cls = `mark ${box ? "box" : "text"}${sel ? " selected" : ""}${t.status === "resolved" ? " resolved" : ""}`;
          const style = box
            ? { borderColor: color, background: withAlpha(color, sel ? 0.12 : 0.05) }
            : { borderColor: color, background: withAlpha(color, sel ? 0.25 : 0.1) };
          return t.anchor!.rects.map((r, i) => <div key={t.id + i} className={cls} style={{ ...pct(r), ...style }} />);
        })}
        {p.pending?.page === p.number && p.pending.rects.map((r, i) => <div key={"p" + i} className="mark pending" style={pct(r)} />)}
      </div>
      <div ref={textRef} className="textLayer" />
      <div className="badges">
        {p.threads.map((t) => {
          const rects = t.anchor!.rects;
          const box = t.anchor!.kind === "box";
          const r = box ? rects[0] : rects.reduce((lo, x) => (x.y1 > lo.y1 + 0.002 || (Math.abs(x.y1 - lo.y1) <= 0.002 && x.x1 > lo.x1) ? x : lo));
          const pos = box ? { left: `${r.x0 * 100}%`, top: `${r.y0 * 100}%` } : { left: `${r.x1 * 100}%`, top: `${r.y0 * 100}%` };
          const n = p.numbers.get(t.id);
          return (
            <button
              key={t.id}
              className={`badge${t.id === p.selectedId ? " selected" : ""}${box ? " at-corner" : ""}`}
              style={{ ...pos, background: t.comments[0]?.author.color }}
              onMouseUp={(e) => e.stopPropagation()}
              onClick={() => p.onSelectThread(t.id)}
              aria-label={`Open thread ${n}`}
            >
              {n}
            </button>
          );
        })}
      </div>
      {p.boxMode && (
        <div className="box-layer" onPointerDown={onBoxDown} onPointerMove={onBoxMove} onPointerUp={onBoxUp}>
          {drag && (
            <div
              className="mark pending"
              style={pct({ x0: Math.min(drag.x, drag.x2), y0: Math.min(drag.y, drag.y2), x1: Math.max(drag.x, drag.x2), y1: Math.max(drag.y, drag.y2) })}
            />
          )}
        </div>
      )}
      <span className="page-num">{p.number}</span>
    </div>
  );
}
