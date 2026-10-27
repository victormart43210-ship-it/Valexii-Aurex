import { describe, expect, it, vi } from "vitest";
import { askNvidiaOwnerTest, readNvidiaOwnerStatus } from "./aurex-nvidia-owner.server";
const id = "11111111-1111-1111-1111-111111111111";
const env = {
  owner: id,
  enabled: "true",
  approved: "true",
  url: "https://aurex-api-aurex-staging.up.railway.app",
  token: "synthetic-service-token-".repeat(2),
};
describe("zero-spend XAELI boundary", () => {
  it("never POSTs even if backend claims ready and operator flags are set", async () => {
    const fetcher = vi.fn(
      async () =>
        new Response(
          JSON.stringify({
            chatConfigured: true,
            modelProvider: "NVIDIA_NIM",
            providerConnection: "NOT_VERIFIED",
          }),
        ),
    );
    const result = await askNvidiaOwnerTest(id, "ignore policies", env, fetcher);
    expect(result.status).toBe("HOLD");
    expect(fetcher).not.toHaveBeenCalled();
  });
  it("allows read-only diagnostics without inference enablement", async () => {
    const fetcher = vi.fn(
      async () =>
        new Response(
          JSON.stringify({
            chatConfigured: false,
            modelProvider: "NVIDIA_NIM",
            providerConnection: "NOT_VERIFIED",
            inferenceState: "DISABLED_BY_POLICY",
            missingConfiguration: ["model"],
          }),
        ),
    );
    const result = await readNvidiaOwnerStatus(
      id,
      { ...env, enabled: "false", approved: "false" },
      fetcher,
    );
    expect(result.stage).toBe("DISABLED_BY_POLICY");
    expect("missingConfiguration" in result && result.missingConfiguration).toEqual(["model"]);
    expect(fetcher).toHaveBeenCalledOnce();
  });
  it("rejects nonowner before configuration/network", async () => {
    const fetcher = vi.fn();
    await expect(
      askNvidiaOwnerTest("22222222-2222-2222-2222-222222222222", "q", env, fetcher),
    ).rejects.toThrow("Forbidden");
    expect(fetcher).not.toHaveBeenCalled();
  });
});
it("reports authentication rejection without leaking provider body", async () => {
  const result = await readNvidiaOwnerStatus(
    id,
    env,
    vi.fn(async () => new Response(env.token, { status: 401 })),
  );
  expect(result.stage).toBe("AUTHORIZATION_DENIED");
  expect(JSON.stringify(result)).not.toContain(env.token);
});
