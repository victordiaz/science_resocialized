import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/** Markdown with GitHub extensions (tables, task lists, strikethrough, autolinks). Links open in a new tab. */
export default function Markdown({ children }: { children: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{ a: ({ node: _node, ...props }) => <a {...props} target="_blank" rel="noreferrer" /> }}
    >
      {children}
    </ReactMarkdown>
  );
}
