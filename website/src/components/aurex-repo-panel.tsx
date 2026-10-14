import { useQuery } from "@tanstack/react-query";
import { getAurexRepoMetadata } from "@/lib/aurex-repo.functions";
import type { RepoMetadata } from "@/lib/aurex-repo";

const ciLabel: Record<string, string> = {
  success: "Latest workflow run passed",
  failure: "Latest workflow run did not pass",
  pending: "Latest workflow run in progress",
  none: "No workflow runs found",
  unavailable: "CI status unavailable",
};
const reasonLabel: Record<string, string> = {
  rate_limited: "GitHub rate limit reached — try again later.",
  not_found: "Repository not found.",
  network: "GitHub could not be reached.",
  invalid_response: "GitHub returned an unexpected response.",
};

export function RepoPanelView({ data, loading }: { data?: RepoMetadata | undefined; loading?: boolean }) {
  return (
    <section aria-labelledby="aurex-repo-title" className="section-space border-b border-border">
      <div className="site-grid">
        <p className="text-xs text-primary">PUBLIC · Real public source metadata · Read-only from GitHub</p>
        <h2 id="aurex-repo-title" className="mt-3 font-display text-3xl">AUREX source repository</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground">
          This panel shows live public repository facts, kept separate from the synthetic demonstration
          above. Repository and CI status describe code activity only; they do not verify the AUREX
          research engine, its evidence or any result.
        </p>
        <dl className="mt-6 grid gap-4 text-sm sm:grid-cols-2" aria-busy={loading} data-testid="aurex-repo">
          <div><dt className="text-muted-foreground">Research engine</dt>
            <dd className="text-amber">NOT_CONNECTED — cannot run research from this website</dd></div>
          {loading || !data ? (
            <div><dt className="text-muted-foreground">Repository</dt><dd>Loading…</dd></div>
          ) : data.status === "unavailable" ? (
            <div><dt className="text-muted-foreground">Repository status</dt>
              <dd>Unavailable · {reasonLabel[data.reason]} Checked {new Date(data.fetchedAt).toUTCString()}</dd></div>
          ) : (
            <>
              <div><dt className="text-muted-foreground">Default branch</dt><dd>{data.defaultBranch}</dd></div>
              <div><dt className="text-muted-foreground">Latest commit</dt>
                <dd><a className="underline underline-offset-4" href={data.commitUrl} target="_blank" rel="noopener noreferrer">
                  {data.commitSha.slice(0, 7)}</a>{data.commitDate ? ` · ${new Date(data.commitDate).toUTCString()}` : ""}</dd></div>
              <div><dt className="text-muted-foreground">CI (code checks only)</dt>
                <dd>{data.ciUrl ? <a className="underline underline-offset-4" href={data.ciUrl} target="_blank" rel="noopener noreferrer">{ciLabel[data.ci]}</a> : ciLabel[data.ci]}</dd></div>
              <div><dt className="text-muted-foreground">Fetched</dt><dd>{new Date(data.fetchedAt).toUTCString()}</dd></div>
            </>
          )}
        </dl>
        <p className="mt-6 text-sm">
          <a className="underline underline-offset-4" href={data?.repoUrl ?? "https://github.com/victormart43210-ship-it/Valexii-Aurex"} target="_blank" rel="noopener noreferrer">
            View repository on GitHub (opens in a new tab)
          </a>
        </p>
      </div>
    </section>
  );
}

export function AurexRepoPanel() {
  const q = useQuery({ queryKey: ["aurex-repo"], queryFn: () => getAurexRepoMetadata(), staleTime: 600_000, retry: false });
  return <RepoPanelView data={q.data} loading={q.isPending} />;
}
