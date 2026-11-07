import { forwardRef, useState } from "react";
import Markdown from "./Markdown";
import { api, getUserName } from "../api";
import type { Comment, Persona, Thread } from "../types";
import { Avatar, Icon, authorKind, clock, plural } from "../ui";
import MentionInput from "./MentionInput";

type Props = {
  thread: Thread;
  number: number;
  personas: Persona[];
  selected: boolean;
  typing: { name: string; color: string }[];
  onSelect: () => void;
  onChanged: () => void;
};

function when(c: Comment) {
  if (c.round != null) return `Round ${c.round}`;
  const d = new Date(c.created_at);
  const today = new Date().toDateString() === d.toDateString();
  return today ? `Today ${clock(c.created_at)}` : d.toLocaleDateString(undefined, { day: "numeric", month: "short" });
}

function replyMeta(c: Comment, byId: Record<string, Comment>) {
  const me = getUserName().trim();
  const to = c.reply_to && byId[c.reply_to] ? ` · to ${byId[c.reply_to].author.name}` : "";
  if (c.author.type === "human") return `${me && c.author.name === me ? "You" : "Human"} · ${clock(c.created_at)}${to}`;
  if (c.round != null) return `AI · Round ${c.round}${to}`;
  return `AI · live reply · ${clock(c.created_at)}${to}`;
}

function anchorLabel(t: Thread) {
  if (!t.anchor) return "Whole paper";
  return `p.${t.anchor.page} · ${t.anchor.kind === "box" ? "box" : "quote"}`;
}

const ThreadCard = forwardRef<HTMLElement, Props>(function ThreadCard({ thread, number, personas, selected, typing, onSelect, onChanged }, ref) {
  const [draft, setDraft] = useState("");
  const [replyTo, setReplyTo] = useState<Comment | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [root, ...replies] = thread.comments;
  const byId = Object.fromEntries(thread.comments.map((c) => [c.id, c]));
  const color = root.author.color;
  const showQuote = thread.anchor?.kind !== "box" && !!thread.anchor?.quote;

  async function send() {
    if (!draft.trim() || busy) return;
    setError(null);
    setBusy(true);
    try {
      await api.reply(thread.id, draft, replyTo?.id ?? null);
      setDraft("");
      setReplyTo(null);
      onChanged();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function toggleStatus() {
    await api.setStatus(thread.id, thread.status === "open" ? "resolved" : "open");
    onChanged();
  }

  async function remove() {
    if (!confirm("Delete this thread and all its replies?")) return;
    await api.deleteThread(thread.id);
    onChanged();
  }

  return (
    <section ref={ref} className={`thread${selected ? " selected" : ""}`} style={{ ["--author" as string]: color }}>
      <button className="thread-head" onClick={onSelect} aria-expanded={selected}>
        <span className="thread-top">
          <span className="num" style={{ background: color }} aria-hidden>{number}</span>
          <span className="who">{root.author.name}</span>
          <span className="kind">{authorKind(root.author, personas)}</span>
          <span className="spacer" />
          <span className="muted small">{when(root)}</span>
        </span>
        <span className="thread-anchor">
          <span className="loc">{anchorLabel(thread)}</span>
          {showQuote && <span className="quote">“{thread.anchor!.quote}”</span>}
          {thread.status === "resolved" && <span className="kind">resolved</span>}
        </span>
        <span className="thread-body"><Markdown>{root.body}</Markdown></span>
        {!selected && (
          <span className="muted small strong">
            {replies.length === 0 ? "No replies" : plural(replies.length, "reply", "replies")}
            {typing.length > 0 && ` · ${typing.map((t) => t.name).join(", ")} replying…`}
          </span>
        )}
      </button>

      {selected && (
        <div className="thread-open">
          {replies.map((c) => (
            <div key={c.id} className="reply">
              <Avatar name={c.author.name} color={c.author.color} size={22} />
              <div className="reply-main">
                <div className="reply-head">
                  <span className="who">{c.author.name}</span>
                  <span className="muted xsmall">{replyMeta(c, byId)}</span>
                  <button className="link xsmall" onClick={() => setReplyTo(c)}>Reply</button>
                </div>
                <div className="reply-body"><Markdown>{c.body}</Markdown></div>
              </div>
            </div>
          ))}

          {typing.map((t) => (
            <div key={t.name} className="typing">
              <span className="dot" style={{ background: t.color }} aria-hidden />
              {t.name} is replying…
            </div>
          ))}

          <div className="reply-form">
            <label className="field-label" htmlFor={`reply-${thread.id}`}>
              {replyTo ? (
                <>
                  Replying to {replyTo.author.name} · <button className="link xsmall" onClick={() => setReplyTo(null)}>reply to the thread instead</button>
                </>
              ) : (
                "Reply · type @ to ask a persona"
              )}
            </label>
            <MentionInput
              id={`reply-${thread.id}`}
              value={draft}
              onChange={setDraft}
              onSubmit={send}
              personas={personas}
              rows={2}
              placeholder="Write a reply…"
            />
            {error && <p className="error">{error}</p>}
            <div className="row end">
              <button className="link danger xsmall" onClick={remove}>Delete thread</button>
              <span className="spacer" />
              <button className="btn" onClick={toggleStatus}>
                {thread.status === "open" ? <>{Icon.check}Resolve</> : "Reopen"}
              </button>
              <button className="btn dark" onClick={send} disabled={!draft.trim() || busy}>Reply</button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
});

export default ThreadCard;
