import type { Paper, Persona, Run, Thread, Comment, Rect, Experiment, Replication, Verification, Attachment } from "./types";

export const API_BASE: string = (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api";

const NAME_KEY = "referee.userName";
export const getUserName = () => localStorage.getItem(NAME_KEY) || "";
export const setUserName = (n: string) => localStorage.setItem(NAME_KEY, n);

async function req<T>(method: string, path: string, body?: unknown, raw?: BodyInit): Promise<T> {
  const headers: Record<string, string> = {};
  const name = getUserName();
  if (name) headers["X-User-Name"] = name;
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const res = await fetch(API_BASE + path, {
    method,
    headers,
    body: raw ?? (body !== undefined ? JSON.stringify(body) : undefined),
  });
  if (!res.ok) {
    let msg = `${res.status} ${res.statusText}`;
    try {
      const j = await res.json();
      if (j.detail) msg = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
    } catch {
      /* not json */
    }
    throw new Error(msg);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  status: () => req<{ anthropic_configured: boolean }>("GET", "/status"),

  papers: () => req<Paper[]>("GET", "/papers"),
  paper: (id: string) => req<Paper>("GET", `/papers/${id}`),
  uploadPaper: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return req<Paper>("POST", "/papers", undefined, fd);
  },
  deletePaper: (id: string) => req<void>("DELETE", `/papers/${id}`),
  updatePaper: (id: string, patch: Partial<Pick<Paper, "title" | "authors" | "year" | "venue" | "abstract" | "keywords" | "field">>) =>
    req<Paper>("PATCH", `/papers/${id}`, patch),
  extractMetadata: (id: string) => req<Paper>("POST", `/papers/${id}/metadata`),
  paperFileUrl: (id: string) => `${API_BASE}/papers/${id}/file`,
  pageImageUrl: (id: string, n: number, dpi = 36) => `${API_BASE}/papers/${id}/pages/${n}/image?dpi=${dpi}`,

  threads: (paperId: string) => req<Thread[]>("GET", `/papers/${paperId}/threads`),
  createThread: (paperId: string, body: string, anchor: { page: number; rects?: Rect[]; quote?: string | null } | null) =>
    req<Thread>("POST", `/papers/${paperId}/threads`, { body, anchor }),
  reply: (threadId: string, body: string, replyTo: string | null) =>
    req<Comment>("POST", `/threads/${threadId}/replies`, { body, reply_to: replyTo }),
  setStatus: (threadId: string, status: "open" | "resolved") => req<Thread>("PATCH", `/threads/${threadId}`, { status }),
  deleteThread: (threadId: string) => req<void>("DELETE", `/threads/${threadId}`),

  personas: () => req<Persona[]>("GET", "/personas"),
  createPersona: (p: Partial<Persona>) => req<Persona>("POST", "/personas", p),
  updatePersona: (id: string, p: Partial<Persona>) => req<Persona>("PATCH", `/personas/${id}`, p),
  deletePersona: (id: string) => req<void>("DELETE", `/personas/${id}`),
  regenerateKey: (id: string) => req<{ api_key: string }>("POST", `/personas/${id}/regenerate-key`),

  runs: (paperId: string) => req<Run[]>("GET", `/papers/${paperId}/runs`),
  startRun: (paperId: string, persona_ids: string[], rounds: number, include_initial: boolean) =>
    req<Run>("POST", `/papers/${paperId}/runs`, { persona_ids, rounds, include_initial }),
  cancelRun: (runId: string) => req<Run>("POST", `/runs/${runId}/cancel`),
  run: (runId: string) => req<Run>("GET", `/runs/${runId}`),

  eventsUrl: (paperId: string) => `${API_BASE}/papers/${paperId}/events`,

  experiments: (paperId: string) => req<Experiment[]>("GET", `/papers/${paperId}/experiments`),
  startExtraction: (paperId: string) => req<Experiment>("POST", `/papers/${paperId}/experiments`),
  updateExperiment: (id: string, patch: { title?: string; spec_md?: string; outcome_md?: string }) =>
    req<Experiment>("PATCH", `/experiments/${id}`, patch),
  recheckLeaks: (id: string) => req<Experiment>("POST", `/experiments/${id}/leak-check`),
  replicate: (expId: string, opts: { verifier_ids?: string[]; budget_usd?: number } = {}) =>
    req<Replication>("POST", `/experiments/${expId}/replications`, opts),
  replication: (id: string, eventsAfter?: number) =>
    req<Replication>("GET", `/replications/${id}${eventsAfter != null ? `?events_after=${eventsAfter}` : ""}`),
  cancelReplication: (id: string) => req<Replication>("POST", `/replications/${id}/cancel`),
  verify: (repId: string, verifier_ids: string[]) => req<Verification[]>("POST", `/replications/${repId}/verifications`, { verifier_ids }),
  /** Upload files for the replicator, reporting progress (0..1). */
  uploadAttachments: (expId: string, files: File[], onProgress?: (fraction: number) => void) =>
    new Promise<Attachment[]>((resolve, reject) => {
      const fd = new FormData();
      for (const f of files) fd.append("files", f, f.name);
      const xhr = new XMLHttpRequest();
      xhr.open("POST", `${API_BASE}/experiments/${expId}/attachments`);
      xhr.upload.onprogress = (e) => e.lengthComputable && onProgress?.(e.loaded / e.total);
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) return resolve(JSON.parse(xhr.responseText));
        let msg = `${xhr.status} ${xhr.statusText}`;
        try {
          msg = JSON.parse(xhr.responseText).detail ?? msg;
        } catch {
          /* not json */
        }
        reject(new Error(msg));
      };
      xhr.onerror = () => reject(new Error("Upload failed: the server could not be reached"));
      xhr.send(fd);
    }),
  updateAttachment: (id: string, note: string) => req<Attachment>("PATCH", `/attachments/${id}`, { note }),
  deleteAttachment: (id: string) => req<void>("DELETE", `/attachments/${id}`),
  attachmentUrl: (id: string) => `${API_BASE}/attachments/${id}/download`,
  replicationFileUrl: (repId: string, path: string) => `${API_BASE}/replications/${repId}/files/${path.split("/").map(encodeURIComponent).join("/")}`,
};
