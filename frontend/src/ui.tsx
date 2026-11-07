/** Small shared presentation helpers. */
import type { Author, Persona } from "./types";

export function initials(name: string): string {
  const words = name.replace(/[^\p{L}\p{N}\s-]/gu, " ").split(/[\s-]+/).filter(Boolean);
  if (words.length === 0) return "?";
  if (words.length === 1) return words[0][0].toUpperCase();
  return (words[0][0] + words[1][0]).toUpperCase();
}

export function Avatar({ name, color, size = 30, ring = false, title }: { name: string; color: string; size?: number; ring?: boolean; title?: string }) {
  return (
    <span
      className={`avatar${ring ? " ring" : ""}`}
      title={title ?? name}
      aria-hidden={title ? undefined : true}
      style={{ width: size, height: size, background: color, fontSize: Math.max(9, Math.round(size * 0.36)) }}
    >
      {initials(name)}
    </span>
  );
}

export function AvatarStack({ authors, size = 30, label }: { authors?: Pick<Author, "name" | "color">[]; size?: number; label?: string }) {
  if (!authors || authors.length === 0) return null;
  return (
    <span className="avatar-stack" aria-label={label ?? authors.map((a) => a.name).join(", ")}>
      {authors.map((a, i) => (
        <Avatar key={a.name + i} name={a.name} color={a.color} size={size} ring title={a.name} />
      ))}
    </span>
  );
}

const MODEL_NAMES: Record<string, string> = {
  "claude-sonnet-5-5": "Sonnet 5.5",
  "claude-opus-5-5": "Opus 5.5",
  "claude-haiku-5-5": "Haiku 5.5",
  "claude-fable-5-1": "Fable 5.1",
};

export function modelLabel(model: string | undefined): string {
  if (!model) return "";
  if (MODEL_NAMES[model]) return MODEL_NAMES[model];
  const m = model.match(/^claude-([a-z]+)-(\d+)(?:-(\d+))?/);
  if (!m) return model;
  return `${m[1][0].toUpperCase()}${m[1].slice(1)} ${m[2]}${m[3] ? "." + m[3] : ""}`;
}

export function authorKind(a: Author, personas: Persona[]): string {
  if (a.type === "human") return "Human";
  const p = personas.find((x) => x.id === a.id);
  if (!p) return "AI";
  return p.kind === "external" ? "AI · external" : `AI · ${modelLabel(p.model)}`;
}

export function shortDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short" });
}

export function clock(iso: string, seconds = false): string {
  return new Date(iso).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit", ...(seconds ? { second: "2-digit" } : {}) });
}

export function plural(n: number, one: string, many = one + "s"): string {
  return `${n} ${n === 1 ? one : many}`;
}

export function runLabel(r: { persona_count: number; rounds: number; include_initial: boolean }): string {
  const who = plural(r.persona_count, "persona");
  if (!r.include_initial) return `${who} · discussion only, ${plural(r.rounds, "round")}`;
  if (r.rounds === 0) return `${who} · solo`;
  return `${who} · ${plural(r.rounds, "round")}`;
}

export const HUMAN_COLOR = "#495057";

export const PALETTE = [
  { hex: "#1F5FD6", label: "Blue" },
  { hex: "#0B7285", label: "Teal" },
  { hex: "#B4410B", label: "Orange" },
  { hex: "#6741D9", label: "Purple" },
  { hex: "#A61E4D", label: "Raspberry" },
  { hex: "#2B8A3E", label: "Green" },
];

export function withAlpha(hex: string, a: number): string {
  const m = hex.replace("#", "");
  const full = m.length === 3 ? m.split("").map((c) => c + c).join("") : m;
  const n = parseInt(full, 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
}

/** Lighten a color toward white, for persona colors shown on a dark background. */
export function lighten(hex: string, amount = 0.45): string {
  const m = hex.replace("#", "");
  const n = parseInt(m.length === 3 ? m.split("").map((c) => c + c).join("") : m, 16);
  const mix = (c: number) => Math.round(c + (255 - c) * amount);
  return `rgb(${mix((n >> 16) & 255)}, ${mix((n >> 8) & 255)}, ${mix(n & 255)})`;
}

export const Icon = {
  play: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M3 2l9 5-9 5V2z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    </svg>
  ),
  plus: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M7 2v10M2 7h10" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  ),
  text: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M2 3h10M7 3v9M5 12h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  ),
  box: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <rect x="2" y="3" width="10" height="8" rx="1" stroke="currentColor" strokeWidth="1.5" strokeDasharray="2 1.5" />
    </svg>
  ),
  prev: (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
      <path d="M7.5 2.5L4 6l3.5 3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  ),
  next: (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
      <path d="M4.5 2.5L8 6 4.5 9.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  ),
  check: (
    <svg width="13" height="13" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M2.5 7.5l3 3 6-7" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  upload: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 16V4M7 9l5-5 5 5M4 16v3a1 1 0 001 1h14a1 1 0 001-1v-3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  logo: (
    <svg width="26" height="26" viewBox="0 0 26 26" fill="none" aria-hidden="true">
      <rect x="3" y="2" width="16" height="21" rx="2" stroke="#1B1C1F" strokeWidth="2" />
      <rect x="9" y="9" width="14" height="10" rx="2" fill="#1F5FD6" />
      <rect x="7" y="6" width="8" height="2" rx="1" fill="#1B1C1F" />
    </svg>
  ),
};
