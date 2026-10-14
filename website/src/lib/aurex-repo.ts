/**
 * Public GitHub repository metadata for AUREX. Browser-safe pure parsing.
 * Repository/CI metadata describes source code activity only; it never
 * verifies the AUREX research engine, evidence or authority.
 */
export const AUREX_REPO = { owner: "victormart43210-ship-it", name: "Valexii-Aurex" } as const;

export type CiStatus = "success" | "failure" | "pending" | "none" | "unavailable";

export type RepoMetadata =
  | {
      status: "available";
      fetchedAt: string;
      repoUrl: string;
      defaultBranch: string;
      commitSha: string;
      commitDate: string | null;
      commitUrl: string;
      ci: CiStatus;
      ciUrl: string | null;
      engine: "NOT_CONNECTED";
    }
  | {
      status: "unavailable";
      fetchedAt: string;
      reason: "rate_limited" | "not_found" | "network" | "invalid_response";
      repoUrl: string;
      engine: "NOT_CONNECTED";
    };

const repoUrl = `https://github.com/${AUREX_REPO.owner}/${AUREX_REPO.name}`;

export function unavailable(reason: Extract<RepoMetadata, { status: "unavailable" }>["reason"], now = new Date()): RepoMetadata {
  return { status: "unavailable", fetchedAt: now.toISOString(), reason, repoUrl, engine: "NOT_CONNECTED" };
}

const SHA = /^[0-9a-f]{40}$/;
const BRANCH = /^[\w./-]{1,100}$/;

export function parseCi(runs: unknown): { ci: CiStatus; ciUrl: string | null } {
  const run = (runs as { workflow_runs?: unknown[] } | null)?.workflow_runs?.[0] as
    | { status?: string; conclusion?: string | null; html_url?: string }
    | undefined;
  if (!runs || !Array.isArray((runs as { workflow_runs?: unknown }).workflow_runs)) return { ci: "unavailable", ciUrl: null };
  if (!run) return { ci: "none", ciUrl: null };
  const url = typeof run.html_url === "string" && run.html_url.startsWith("https://github.com/") ? run.html_url : null;
  if (run.status !== "completed") return { ci: "pending", ciUrl: url };
  return { ci: run.conclusion === "success" ? "success" : "failure", ciUrl: url };
}

export function parseRepo(repo: unknown, commit: unknown, runs: unknown, now = new Date()): RepoMetadata {
  const r = repo as { default_branch?: unknown } | null;
  const c = commit as { sha?: unknown; commit?: { committer?: { date?: unknown } } } | null;
  const branch = r?.default_branch;
  const sha = c?.sha;
  if (typeof branch !== "string" || !BRANCH.test(branch) || typeof sha !== "string" || !SHA.test(sha))
    return unavailable("invalid_response", now);
  const date = c?.commit?.committer?.date;
  return {
    status: "available",
    fetchedAt: now.toISOString(),
    repoUrl,
    defaultBranch: branch,
    commitSha: sha,
    commitDate: typeof date === "string" && !Number.isNaN(Date.parse(date)) ? date : null,
    commitUrl: `${repoUrl}/commit/${sha}`,
    ...parseCi(runs),
    engine: "NOT_CONNECTED",
  };
}
