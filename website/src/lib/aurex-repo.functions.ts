import { createServerFn } from "@tanstack/react-start";
import { AUREX_REPO, parseRepo, unavailable, type RepoMetadata } from "./aurex-repo";

let cache: { at: number; value: RepoMetadata } | null = null;
const TTL_MS = 10 * 60 * 1000;

/** Unauthenticated, read-only public GitHub metadata. No token is used. */
export const getAurexRepoMetadata = createServerFn({ method: "GET" }).handler(
  async (): Promise<RepoMetadata> => {
    if (cache && Date.now() - cache.at < TTL_MS) return cache.value;
    const base = `https://api.github.com/repos/${AUREX_REPO.owner}/${AUREX_REPO.name}`;
    const get = (path: string) =>
      fetch(base + path, {
        headers: { Accept: "application/vnd.github+json", "User-Agent": "valexii-website" },
        signal: AbortSignal.timeout(5000),
      });
    let value: RepoMetadata;
    try {
      const repoRes = await get("");
      if (!repoRes.ok) {
        value = unavailable(
          repoRes.status === 404
            ? "not_found"
            : repoRes.status === 403 || repoRes.status === 429
              ? "rate_limited"
              : "network",
        );
      } else {
        const repo = await repoRes.json();
        const branch = encodeURIComponent(String(repo?.default_branch ?? ""));
        const [commitRes, runsRes] = await Promise.all([
          get(`/commits/${branch}`),
          get(`/actions/runs?per_page=1&branch=${branch}`),
        ]);
        const commit = commitRes.ok ? await commitRes.json() : null;
        const runs = runsRes.ok ? await runsRes.json() : null;
        value = parseRepo(repo, commit, runs);
      }
    } catch {
      value = unavailable("network");
    }
    cache = { at: Date.now(), value: value.status === "available" ? value : value };
    if (value.status === "unavailable") cache.at = Date.now() - TTL_MS + 60_000; // retry after 1 min
    return value;
  },
);
