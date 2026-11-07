import { useEffect, useRef, useState } from "react";
import { getUserName, setUserName } from "./api";
import Library from "./pages/Library";
import PaperView from "./pages/PaperView";
import Personas from "./pages/Personas";
import RunReview from "./pages/RunReview";
import Replicate from "./pages/Replicate";
import Lab from "./pages/Lab";
import { Avatar, HUMAN_COLOR, Icon } from "./ui";

type Route =
  | { name: "library" }
  | { name: "paper"; id: string }
  | { name: "run"; id: string }
  | { name: "replicate"; id: string }
  | { name: "personas" }
  | { name: "lab" };

function parseHash(): Route {
  if (window.location.pathname.replace(/\/$/, "") === "/lab") return { name: "lab" };
  const [a, b, c] = window.location.hash.replace(/^#\/?/, "").split("/");
  if (a === "paper" && b && c === "run") return { name: "run", id: b };
  if (a === "paper" && b && c === "replicate") return { name: "replicate", id: b };
  if (a === "paper" && b) return { name: "paper", id: b };
  if (a === "personas") return { name: "personas" };
  if (a === "lab") return { name: "lab" };
  return { name: "library" };
}

function Me() {
  const [name, setName] = useState(getUserName());
  const [editing, setEditing] = useState(!getUserName());
  const ref = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (editing) ref.current?.focus();
  }, [editing]);
  const shown = name.trim() || "You";
  return (
    <div className="me">
      {editing ? (
        <label>
          <span className="sr-only">Your name</span>
          <input
            ref={ref}
            value={name}
            placeholder="Your name"
            onChange={(e) => {
              setName(e.target.value);
              setUserName(e.target.value);
            }}
            onBlur={() => name.trim() && setEditing(false)}
            onKeyDown={(e) => e.key === "Enter" && name.trim() && setEditing(false)}
          />
        </label>
      ) : (
        <button className="me-name" onClick={() => setEditing(true)} title="Change the name your comments are signed with">
          {shown}
        </button>
      )}
      <Avatar name={shown} color={HUMAN_COLOR} size={32} />
    </div>
  );
}

export default function App() {
  const [route, setRoute] = useState<Route>(parseHash);

  useEffect(() => {
    const on = () => setRoute(parseHash());
    window.addEventListener("hashchange", on);
    return () => window.removeEventListener("hashchange", on);
  }, []);

  const inPapers = route.name !== "personas" && route.name !== "lab";

  return (
    <div className="app">
      <header className="topbar">
        <a className="brand" href="#/">
          <img src="/brand/logo/mark.svg" width="28" height="28" alt="" />
          <span>Science Resocialized</span>
        </a>
        <nav aria-label="Main">
          <a href="#/" aria-current={inPapers ? "page" : undefined}>Papers</a>
          <a href="#/personas" aria-current={route.name === "personas" ? "page" : undefined}>Personas</a>
          <a href="/docs" target="_blank" rel="noreferrer">API docs</a>
        </nav>
        <div className="spacer" />
        <Me />
      </header>
      <main className="main">
        {route.name === "library" && <Library />}
        {route.name === "paper" && <PaperView key={route.id} paperId={route.id} />}
        {route.name === "run" && <RunReview key={route.id} paperId={route.id} />}
        {route.name === "replicate" && <Replicate key={route.id} paperId={route.id} />}
        {route.name === "personas" && <Personas />}
        {route.name === "lab" && <Lab />}
      </main>
    </div>
  );
}
