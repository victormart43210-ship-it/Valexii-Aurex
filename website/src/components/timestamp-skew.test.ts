import { describe, expect, it } from "vitest";
import { evidenceFresh } from "../lib/aurex-api-schema";

describe("AUREX timestamp clock skew reproduction & validation", () => {
  it("allows bounded clock skew tolerance up to +60 seconds", () => {
    const now = Date.parse("2026-10-24T12:00:00.000Z");

    // Exact current time
    const exact = { collectedAt: "2026-10-24T12:00:00.000Z" };
    expect(evidenceFresh(exact, now)).toBe(true);

    // Minor cloud clock drift (+500ms ahead)
    const drift500ms = { collectedAt: "2026-10-24T12:00:00.500Z" };
    expect(evidenceFresh(drift500ms, now)).toBe(true);

    // Server clock 10 seconds ahead (well within 60s tolerance)
    const drift10s = { collectedAt: "2026-10-24T12:00:10.000Z" };
    expect(evidenceFresh(drift10s, now)).toBe(true);

    // Genuinely future-dated evidence (> 60s ahead) must be rejected
    const future2min = { collectedAt: "2026-10-24T12:02:00.000Z" };
    expect(evidenceFresh(future2min, now)).toBe(false);

    // Stale evidence (> 7 days old) must be rejected
    const stale8days = { collectedAt: "2026-10-10T12:00:00.000Z" };
    expect(evidenceFresh(stale8days, now)).toBe(false);
  });
});
