export type Rect = { x0: number; y0: number; x1: number; y1: number };

export type Anchor = { page: number; rects: Rect[]; quote: string | null; kind: "text" | "box" };

export type Author = { type: "human" | "persona"; id: string | null; name: string; color: string };

export type Comment = {
  id: string;
  seq: number;
  thread_id: string;
  author: Author;
  body: string;
  reply_to: string | null;
  run_id: string | null;
  round: number | null;
  created_at: string;
};

export type Thread = {
  id: string;
  paper_id: string;
  anchor: Anchor | null;
  status: "open" | "resolved";
  created_at: string;
  comments: Comment[];
};

export type PageMeta = { number: number; width: number; height: number };

export type RunSummary = {
  id: string;
  persona_count: number;
  rounds: number;
  include_initial: boolean;
  status: Run["status"];
  created_at: string;
};

export type Paper = {
  id: string;
  title: string;
  filename: string;
  page_count: number;
  created_at: string;
  pages?: PageMeta[];
  thread_count: number;
  open_count: number;
  resolved_count: number;
  participants: Author[]; // who has commented
  last_run: RunSummary | null;
  // Extracted details
  authors: string[];
  year: number | null;
  venue: string | null;
  abstract: string | null;
  keywords: string[];
  field: string | null;
  doc_type: string | null;
  arxiv_id: string | null;
  doi: string | null;
  title_source: "pdf" | "metadata" | "user";
  metadata_status: "none" | "pending" | "running" | "done" | "failed";
  metadata_error: string | null;
};

export type Persona = {
  id: string;
  kind: "builtin" | "external";
  name: string;
  color: string;
  prompt: string;
  model: string;
  tagline: string;
  enabled: boolean;
  created_at: string;
  comment_count?: number;
  paper_count?: number;
  api_key?: string;
};

export type RunTask = {
  id: string;
  persona_id: string;
  persona_name: string;
  persona_color: string;
  round: number;
  status: "pending" | "running" | "done" | "failed" | "cancelled";
  steps: number;
  comment_count: number;
  reply_count: number;
  activity: string | null;
  error: string | null;
};

export type RunEvent = {
  seq: number;
  persona_id: string;
  persona_name: string;
  persona_color: string;
  round: number;
  call: string;
  code: number;
  at: string;
};

export type Run = {
  id: string;
  number: number;
  paper_id: string;
  persona_ids: string[];
  rounds: number;
  include_initial: boolean;
  status: "queued" | "running" | "completed" | "failed" | "cancelled";
  current_round: number | null;
  error: string | null;
  created_at: string;
  finished_at: string | null;
  tasks: RunTask[];
  events?: RunEvent[];
};

export type PendingAnchor = { page: number; rects: Rect[]; quote: string | null } | null;

export type Verification = {
  id: string;
  replication_id: string;
  persona_id: string;
  persona_name: string | null;
  persona_color: string | null;
  status: "pending" | "running" | "done" | "failed";
  report_md: string | null;
  error: string | null;
  created_at: string;
  finished_at: string | null;
};

export type ReplicationEvent = { seq: number; kind: "text" | "tool" | "result" | "stderr" | "info"; text: string; at: string };

export type Attachment = {
  id: string;
  experiment_id: string;
  filename: string;
  size: number;
  sha256: string;
  content_type: string | null;
  note: string;
  created_at: string;
};

export type Replication = {
  id: string;
  experiment_id: string;
  paper_id: string;
  status: "queued" | "running" | "done" | "failed" | "cancelled";
  spec_md: string;
  verifier_ids: string[];
  budget_usd: number;
  timeout_min: number;
  worker: string | null;
  workdir: string | null;
  report_md: string | null;
  cost_usd: number | null;
  cancel_requested: boolean;
  error: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  verifications: Verification[];
  files: { path: string; size: number }[];
  attachments: Attachment[]; // files this run was given
  events?: ReplicationEvent[];
};

export type Experiment = {
  id: string;
  paper_id: string;
  status: "extracting" | "checking" | "ready" | "needs_review" | "failed";
  title: string;
  spec_md: string;
  outcome_md: string;
  leak_check_md: string | null;
  leak_found: boolean | null;
  verifier_ids: string[];
  budget_usd: number;
  error: string | null;
  created_at: string;
  updated_at: string;
  replications: Replication[];
  attachments: Attachment[];
};
