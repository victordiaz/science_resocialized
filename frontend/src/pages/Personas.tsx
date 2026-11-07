import { useEffect, useState } from "react";
import { API_BASE, api } from "../api";
import type { Persona } from "../types";
import { Avatar, Icon, PALETTE, modelLabel, plural } from "../ui";

const MODELS = [
  { id: "claude-sonnet-5-5", label: "Claude Sonnet 5.5" },
  { id: "claude-opus-5-5", label: "Claude Opus 5.5" },
  { id: "claude-haiku-5-5", label: "Claude Haiku 5.5" },
  { id: "claude-fable-5-1", label: "Claude Fable 5.1" },
];

type Draft = Partial<Persona>;

const blank = (taken: string[]): Draft => ({
  name: "",
  kind: "builtin",
  color: PALETTE.find((c) => !taken.includes(c.hex))?.hex ?? PALETTE[0].hex,
  prompt: "",
  tagline: "",
  model: MODELS[0].id,
  enabled: true,
});

function usage(p: Persona) {
  if (!p.comment_count) return "No comments yet";
  return `On ${plural(p.paper_count ?? 0, "paper")} · ${plural(p.comment_count, "comment")}`;
}

export default function Personas() {
  const [list, setList] = useState<Persona[]>([]);
  const [saved, setSaved] = useState<Draft | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [key, setKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const load = () =>
    api.personas().then((ps) => {
      setList(ps);
      return ps;
    });

  const open = (p: Draft) => {
    setSaved(p);
    setDraft(p);
    setKey(null);
    setError(null);
    setNotice(null);
  };

  useEffect(() => {
    load().then((ps) => ps[0] && open(ps[0]));
  }, []);

  const dirty = JSON.stringify(saved) !== JSON.stringify(draft);
  const set = (patch: Draft) => {
    setNotice(null);
    setDraft((d) => ({ ...d, ...patch }));
  };

  async function save() {
    if (!draft) return;
    setError(null);
    try {
      const fields = { name: draft.name, kind: draft.kind, color: draft.color, prompt: draft.prompt, tagline: draft.tagline, model: draft.model, enabled: draft.enabled };
      if (draft.id) {
        const p = await api.updatePersona(draft.id, fields);
        const ps = await load();
        open(ps.find((x) => x.id === p.id) ?? p);
        setNotice("Saved");
      } else {
        const p = await api.createPersona(fields);
        const ps = await load();
        open(ps.find((x) => x.id === p.id) ?? p);
        setKey(p.api_key ?? null);
        setNotice("Created");
      }
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function remove() {
    if (!draft?.id || !confirm(`Delete ${draft.name}? Their comments stay on the papers.`)) return;
    await api.deletePersona(draft.id);
    const ps = await load();
    if (ps[0]) open(ps[0]);
    else open(blank([]));
  }

  async function regenerate() {
    if (!draft?.id || !confirm("Make a new API key? The old key stops working.")) return;
    const r = await api.regenerateKey(draft.id);
    setKey(r.api_key);
  }

  const current = list.find((p) => p.id === draft?.id);

  return (
    <div className="page-wrap wide">
      <div className="page-head">
        <div className="page-title">
          <h1>Personas</h1>
          <p>Reviewer agents. Each one runs as its own Claude agent during a review and answers when you reply to it or @mention it.</p>
        </div>
        <button className="btn dark big" onClick={() => open(blank(list.map((p) => p.color)))}>
          {Icon.plus}New persona
        </button>
      </div>

      <div className="personas-layout">
        <ul className="persona-cards" aria-label="Personas">
          {list.map((p) => (
            <li key={p.id}>
              <button aria-current={draft?.id === p.id} onClick={() => open(p)}>
                <Avatar name={p.name} color={p.color} size={36} />
                <span className="pc-text">
                  <span className="strong">{p.name}</span>
                  <span className="muted small">{p.tagline || (p.kind === "external" ? "Outside agent, posts through the API" : "No description")}</span>
                </span>
                <span className="kind">{p.kind === "external" ? "external" : modelLabel(p.model)}</span>
                {!p.enabled && <span className="kind">off</span>}
              </button>
            </li>
          ))}
          {draft && !draft.id && (
            <li>
              <button aria-current>
                <Avatar name={draft.name || "New"} color={draft.color ?? PALETTE[0].hex} size={36} />
                <span className="pc-text">
                  <span className="strong">{draft.name || "New persona"}</span>
                  <span className="muted small">Not saved yet</span>
                </span>
              </button>
            </li>
          )}
        </ul>

        {draft && (
          <section className="card persona-form" aria-label="Edit persona">
            <div className="pf-head">
              <Avatar name={draft.name || "New"} color={draft.color ?? PALETTE[0].hex} size={48} />
              <div>
                <h2>{draft.name || "New persona"}</h2>
                <span className="muted small">{current ? usage(current) : "Fill in the details and create it"}</span>
              </div>
            </div>

            <div className="grid-2">
              <label className="field">
                <span>Name</span>
                <input value={draft.name ?? ""} onChange={(e) => set({ name: e.target.value })} placeholder="Methods Skeptic" />
              </label>
              {draft.kind === "builtin" ? (
                <label className="field">
                  <span>Model</span>
                  <select value={draft.model} onChange={(e) => set({ model: e.target.value })}>
                    {!MODELS.some((m) => m.id === draft.model) && <option value={draft.model}>{draft.model}</option>}
                    {MODELS.map((m) => <option key={m.id} value={m.id}>{m.label}</option>)}
                  </select>
                </label>
              ) : (
                <div className="field">
                  <span>Model</span>
                  <p className="muted small field-note">Chosen by the outside agent.</p>
                </div>
              )}
            </div>

            <label className="field">
              <span>Focus</span>
              <input value={draft.tagline ?? ""} onChange={(e) => set({ tagline: e.target.value })} placeholder="Experimental design, confounds, ablations" />
            </label>

            <fieldset className="field">
              <legend>Color</legend>
              <div className="swatches">
                {PALETTE.map((c) => (
                  <label key={c.hex} className={`swatch${draft.color?.toLowerCase() === c.hex.toLowerCase() ? " on" : ""}`}>
                    <input type="radio" name="color" value={c.hex} checked={draft.color?.toLowerCase() === c.hex.toLowerCase()} onChange={() => set({ color: c.hex })} aria-label={c.label} />
                    <span style={{ background: c.hex }} />
                  </label>
                ))}
                <label className={`swatch custom${PALETTE.some((c) => c.hex.toLowerCase() === draft.color?.toLowerCase()) ? "" : " on"}`} title="Custom color">
                  <input type="color" value={draft.color} onChange={(e) => set({ color: e.target.value })} aria-label="Custom color" />
                </label>
              </div>
            </fieldset>

            {draft.kind === "builtin" && (
              <label className="field">
                <span className="field-row">
                  Prompt <span className="muted small normal">Sent as the agent's instructions, with the workspace tools and the paper attached</span>
                </span>
                <textarea
                  className="mono-area"
                  rows={9}
                  value={draft.prompt ?? ""}
                  onChange={(e) => set({ prompt: e.target.value })}
                  placeholder="Who this reviewer is, what they look for, and how they judge a paper."
                />
              </label>
            )}

            <fieldset className="field">
              <legend>Runs</legend>
              <label className="check small">
                <input type="radio" checked={draft.kind === "builtin"} onChange={() => set({ kind: "builtin" })} />
                In this app, with Claude and the prompt above
              </label>
              <label className="check small">
                <input type="radio" checked={draft.kind === "external"} onChange={() => set({ kind: "external" })} />
                As an outside agent that posts through the API with its own key
              </label>
              <label className="check small">
                <input type="checkbox" checked={!!draft.enabled} onChange={(e) => set({ enabled: e.target.checked })} />
                Available for reviews and replies
              </label>
            </fieldset>

            {key && (
              <div className="key-box">
                <p className="strong">Copy this API key now. It won't be shown again.</p>
                <code>{key}</code>
                <p className="muted small">An agent posts as {draft.name} by sending it as a bearer token:</p>
                <pre>{`curl -X POST ${location.origin}${API_BASE}/papers/<paper_id>/threads \\
  -H "Authorization: Bearer ${key}" -H "Content-Type: application/json" \\
  -d '{"body": "…", "anchor": {"page": 3, "quote": "exact text on the page"}}'`}</pre>
              </div>
            )}

            {error && <p className="error">{error}</p>}
            <div className="pf-actions">
              {draft.id && <button type="button" className="btn danger-outline" onClick={remove}>Delete persona</button>}
              {draft.id && <button type="button" className="btn ghost" onClick={regenerate}>New API key</button>}
              <span className="spacer" />
              {notice && !dirty && <span className="muted small">{notice}</span>}
              <button type="button" className="btn" disabled={!dirty} onClick={() => setDraft(saved)}>Discard changes</button>
              <button type="button" className="btn dark" disabled={!draft.name?.trim() || (!dirty && !!draft.id)} onClick={save}>
                {draft.id ? "Save" : "Create persona"}
              </button>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
