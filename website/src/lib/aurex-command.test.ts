import { test, expect } from "vitest";
import { JobCreateSchema, JobSchema } from "./aurex-api-schema";
import { createAurexClient } from "./aurex-client.server";

test("local inference accepts a bounded prompt and zero budget", () => {
  expect(
    JobCreateSchema.safeParse({
      kind: "local_inference",
      params: { prompt: "Explain evidence" },
      maxCostUsd: 0,
    }).success,
  ).toBe(true);
});
test("local inference rejects empty, multibyte oversized, extra params and paid budget", () => {
  for (const [params, maxCostUsd] of [
    [{ prompt: " " }, 0],
    [{ prompt: "界".repeat(2731) }, 0],
    [{ prompt: "ok", command: "sh" }, 0],
    [{ prompt: "ok" }, 1],
  ]) {
    expect(JobCreateSchema.safeParse({ kind: "local_inference", params, maxCostUsd }).success).toBe(
      false,
    );
  }
});
test("terminal expiry is representable", () => {
  expect(
    JobSchema.safeParse({
      id: "job1",
      kind: "local_inference",
      state: "expired",
      createdAt: "2026-10-15T00:00:00Z",
      updatedAt: "2026-10-15T00:00:00Z",
      reservationUsd: 0,
    }).success,
  ).toBe(true);
});
test("client preserves advisory result and rejects authority spoofing", async () => {
  let authorityGranted = false;
  const client = createAurexClient({
    url: "https://fixture.example.invalid",
    token: "x".repeat(32),
    fetcher: async (url) => {
      expect(new URL(String(url)).pathname).toBe("/v1/jobs/job1/result");
      return new Response(
        JSON.stringify({
          jobId: "job1",
          state: "succeeded",
          verification: "NOT VERIFIED",
          result: {
            text: "Historical observation is not current authority.",
            model: "fixture",
            provider: "local",
            verification: "NOT VERIFIED",
            authorityGranted,
          },
        }),
      );
    },
  });
  expect((await client.jobResult("job1")).ok).toBe(true);
  authorityGranted = true;
  expect(await client.jobResult("job1")).toEqual({ ok: false, error: "malformed" });
  expect(await client.jobResult("../secrets")).toEqual({ ok: false, error: "invalid_input" });
});

test("command authorization rejects missing owner and another user before upstream access", async () => {
  const { ownerCommandClient } = await import("./aurex-command.server");
  const owner = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
  expect(() =>
    ownerCommandClient("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", { ownerId: owner }),
  ).toThrow("Forbidden");
  expect(() => ownerCommandClient(owner, {})).toThrow("Forbidden");
  expect(ownerCommandClient(owner, { ownerId: owner }).configured).toBe(false);
});

test("corrupt backend result remains an explicit failure", async () => {
  const client = createAurexClient({
    url: "https://fixture.example.invalid",
    token: "x".repeat(32),
    fetcher: async () => new Response("corrupt", { status: 409 }),
  });
  expect(await client.jobResult("job1")).toEqual({ ok: false, error: "http_error", status: 409 });
});

test("job evidence preserves integrity failure and rejects authority grants", async () => {
  let authorityGranted = false;
  const client = createAurexClient({
    url: "https://fixture.example.invalid",
    token: "x".repeat(32),
    fetcher: async () =>
      new Response(
        JSON.stringify({
          evidence: [
            {
              id: "ev1",
              capabilityId: "local-inference",
              kind: "model_response",
              collectedAt: "2026-10-15T00:00:00Z",
              sha256: "a".repeat(64),
              summary: "Execution record",
              verification: "NOT VERIFIED",
              integrity: "FAIL",
              authorityGranted,
            },
          ],
        }),
      ),
  });
  const read = await client.jobEvidence("job1");
  expect(read.ok && read.value.evidence[0]?.integrity).toBe("FAIL");
  authorityGranted = true;
  expect(await client.jobEvidence("job1")).toEqual({ ok: false, error: "malformed" });
});
