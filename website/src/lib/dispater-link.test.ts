import { describe, expect, it } from "vitest";
import { dispaterLinkState } from "./dispater-link";

describe("dispater link state", () => {
  it("keeps an idle console disconnected and a missing backend unavailable", () => {
    expect(dispaterLinkState(false, null, null)).toBe("DISCONNECTED");
    expect(dispaterLinkState(true, null, null)).toBe("LOADING");
    expect(dispaterLinkState(false, null, "DISPATER backend is not configured")).toBe("UNAVAILABLE");
    expect(dispaterLinkState(false, null, "DISPATER backend unreachable")).toBe("DISCONNECTED");
    expect(dispaterLinkState(false, null, "DISPATER API error (401)")).toBe("ERROR");
  });
});
