import { test, expect } from "vitest";
import { createAurexClient } from "./aurex-client.server";
import { ownerCommandClient } from "./aurex-command.server";

test("owner analytics returns measured zeros without inventing visitors", async () => {
  const c = createAurexClient({
    url: "https://fixture.example.invalid",
    token: "x".repeat(32),
    fetcher: async (url) => {
      expect(new URL(String(url)).pathname).toBe("/v1/analytics");
      return Response.json({
        counts: {},
        jobsByState: {},
        measurement: "event_counts",
        uniqueVisitors: null,
      });
    },
  });
  expect(await c.analytics()).toEqual({
    ok: true,
    value: { counts: {}, jobsByState: {}, measurement: "event_counts", uniqueVisitors: null },
  });
});
test("analytics rejects fabricated visitor fields and negative counters", async () => {
  for (const payload of [
    {
      counts: { page_view: -1 },
      jobsByState: {},
      measurement: "event_counts",
      uniqueVisitors: null,
    },
    { counts: {}, jobsByState: {}, measurement: "event_counts", uniqueVisitors: 100 },
    {
      counts: { private_prompt: 1 },
      jobsByState: {},
      measurement: "event_counts",
      uniqueVisitors: null,
    },
  ]) {
    const c = createAurexClient({
      url: "https://fixture.example.invalid",
      token: "x".repeat(32),
      fetcher: async () => Response.json(payload),
    });
    expect(await c.analytics()).toEqual({ ok: false, error: "malformed" });
  }
});
test("analytics remains inaccessible to a non-owner", () => {
  expect(() =>
    ownerCommandClient("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", {
      ownerId: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    }),
  ).toThrow("Forbidden");
});
test("analytics outage is not converted to zero events", async () => {
  const c = createAurexClient({
    url: "https://fixture.example.invalid",
    token: "x".repeat(32),
    fetcher: async () => new Response("", { status: 503 }),
  });
  expect(await c.analytics()).toEqual({ ok: false, error: "http_error", status: 503 });
});
