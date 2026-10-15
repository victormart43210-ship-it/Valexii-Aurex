import assert from "node:assert/strict";
import { test } from "vitest";
import { createAurexClient } from "./aurex-client.server";
import { checkAurexService } from "./aurex-service.server";

test("canonical backend health and capabilities use separate authenticated endpoints", async () => {
  const data: Record<string, { body: unknown }> = {
    health: { body: { status: "ok", version: "test", time: "2026-10-14T00:00:00Z" } },
    capabilities: { body: { capabilities: [] } },
  };
  const fetcher = (async (input: URL | RequestInfo, init?: RequestInit) => {
    assert.equal(
      (init?.headers as Record<string, string>)["Authorization"],
      "Bearer " + "x".repeat(32),
    );
    const key = new URL(String(input)).pathname.split("/").at(-1)!;
    return new Response(JSON.stringify(data[key]!.body));
  }) as typeof fetch;
  assert.deepEqual(
    await checkAurexService(
      { url: "https://fixture.example.invalid", token: "x".repeat(32) },
      fetcher,
    ),
    { state: "HEALTHY", checks: { serviceHealthy: true, serviceCapabilities: [] } },
  );
});

test("tokens rejected by backend minimum are not configured", () => {
  assert.equal(
    createAurexClient({ url: "https://fixture.example.invalid", token: "x".repeat(16) }).configured,
    false,
  );
});

test("oversized chunked upstream body is cancelled before being fully buffered", async () => {
  let chunks = 0;
  let cancelled = false;
  const stream = new ReadableStream({
    pull(controller) {
      chunks++;
      controller.enqueue(new Uint8Array(100_000));
      if (chunks === 10) controller.close();
    },
    cancel() {
      cancelled = true;
    },
  });
  const fetcher = (async () => new Response(stream)) as typeof fetch;
  const client = createAurexClient({
    url: "https://fixture.example.invalid",
    token: "x".repeat(32),
    fetcher,
  });
  assert.deepEqual(await client.health(), { ok: false, error: "too_large" });
  assert.ok(chunks < 10);
  assert.equal(cancelled, true);
});
