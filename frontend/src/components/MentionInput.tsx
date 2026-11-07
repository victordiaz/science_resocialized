import { useRef, useState } from "react";
import type { Persona } from "../types";

type Props = {
  id?: string;
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  personas: Persona[];
  placeholder?: string;
  autoFocus?: boolean;
  rows?: number;
};

/** Textarea with @persona autocomplete. Cmd/Ctrl+Enter submits. */
export default function MentionInput({ id, value, onChange, onSubmit, personas, placeholder, autoFocus, rows = 3 }: Props) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const [query, setQuery] = useState<{ start: number; text: string } | null>(null);
  const [active, setActive] = useState(0);

  const matches = query
    ? personas.filter((p) => p.kind === "builtin" && p.enabled && p.name.toLowerCase().includes(query.text.toLowerCase())).slice(0, 6)
    : [];

  function update(v: string, caret: number) {
    onChange(v);
    const before = v.slice(0, caret);
    const m = before.match(/(^|\s)@([\w-]*)$/);
    if (m) {
      setQuery({ start: caret - m[2].length - 1, text: m[2] });
      setActive(0);
    } else setQuery(null);
  }

  function pick(p: Persona) {
    if (!query) return;
    const caret = ref.current?.selectionStart ?? value.length;
    const next = value.slice(0, query.start) + "@" + p.name + " " + value.slice(caret);
    onChange(next);
    setQuery(null);
    requestAnimationFrame(() => {
      const pos = query.start + p.name.length + 2;
      ref.current?.focus();
      ref.current?.setSelectionRange(pos, pos);
    });
  }

  return (
    <div className="mention">
      <textarea
        ref={ref}
        id={id}
        rows={rows}
        value={value}
        autoFocus={autoFocus}
        placeholder={placeholder}
        onChange={(e) => update(e.target.value, e.target.selectionStart)}
        onKeyDown={(e) => {
          if (matches.length) {
            if (e.key === "ArrowDown") return e.preventDefault(), setActive((active + 1) % matches.length);
            if (e.key === "ArrowUp") return e.preventDefault(), setActive((active - 1 + matches.length) % matches.length);
            if (e.key === "Enter" || e.key === "Tab") return e.preventDefault(), pick(matches[active]);
            if (e.key === "Escape") return setQuery(null);
          }
          if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
            e.preventDefault();
            onSubmit();
          }
        }}
      />
      {matches.length > 0 && (
        <ul className="mention-menu" role="listbox">
          {matches.map((p, i) => (
            <li
              key={p.id}
              role="option"
              aria-selected={i === active}
              onMouseDown={(e) => {
                e.preventDefault();
                pick(p);
              }}
            >
              <span className="dot" style={{ background: p.color }} />
              {p.name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
