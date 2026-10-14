import { describe, expect, it } from "vitest";
import { parseCi, parseRepo, unavailable } from "@/lib/aurex-repo";

const sha = "a".repeat(40);
const now = new Date("2026-10-13T00:00:00Z");

describe("AUREX repository metadata", () => {
  it("parses valid metadata and keeps engine NOT_CONNECTED", () => {
    const m = parseRepo({ default_branch: "main" }, { sha, commit: { committer: { date: "2026-10-12T10:00:00Z" } } },
      { workflow_runs: [{ status: "completed", conclusion: "success", html_url: "https://github.com/x/y/actions/runs/1" }] }, now);
    expect(m.status).toBe("available");
    expect(m.engine).toBe("NOT_CONNECTED");
    if (m.status === "available") { expect(m.ci).toBe("success"); expect(m.commitUrl).toContain(sha); }
  });
  it("fails closed to unavailable on malformed responses", () => {
    expect(parseRepo(null, null, null, now).status).toBe("unavailable");
    expect(parseRepo({ default_branch: "main" }, { sha: "bad" }, null, now).status).toBe("unavailable");
    expect(parseRepo({ default_branch: "<script>" }, { sha }, null, now).status).toBe("unavailable");
  });
  it("never reports CI success without a completed successful run", () => {
    expect(parseCi(null).ci).toBe("unavailable");
    expect(parseCi({ workflow_runs: [] }).ci).toBe("none");
    expect(parseCi({ workflow_runs: [{ status: "in_progress" }] }).ci).toBe("pending");
    expect(parseCi({ workflow_runs: [{ status: "completed", conclusion: "cancelled" }] }).ci).toBe("failure");
    expect(parseCi({ workflow_runs: [{ status: "completed", conclusion: "success", html_url: "https://evil.example" }] }).ciUrl).toBeNull();
  });
  it("unavailable states carry reason and NOT_CONNECTED engine", () => {
    const u = unavailable("rate_limited", now);
    expect(u).toMatchObject({ status: "unavailable", reason: "rate_limited", engine: "NOT_CONNECTED" });
  });
});
