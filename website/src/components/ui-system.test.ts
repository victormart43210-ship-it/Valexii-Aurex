import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import {
  ActionButton,
  Card,
  EmptyState,
  ErrorState,
  LoadingSkeleton,
  SectionHeader,
  StatePanel,
} from "./ui-system";
import { Button } from "./ui/button";

const render = (element: Parameters<typeof renderToStaticMarkup>[0]) =>
  renderToStaticMarkup(element);
describe("shared UI accessible state contracts", () => {
  it("renders labelled unknown empty state without a success claim", () => {
    const html = render(
      createElement(EmptyState, { title: "UNKNOWN", children: "No live telemetry" }),
    );
    expect(html).toContain("aria-labelledby");
    expect(html).toContain("No live telemetry");
    expect(html).not.toContain('role="status"');
    expect(html).not.toMatch(/protected|PASS|trusted/i);
  });
  it("announces errors only when requested and never exposes raw exceptions", () => {
    const html = render(
      createElement(ErrorState, { title: "Unavailable", announce: "assertive", headingLevel: 1 }),
    );
    expect(html).toContain('role="alert"');
    expect(html).toContain("<h1");
    expect(html).toContain('data-tone="error"');
  });
  it("clamps skeleton edge cases and provides one accessible loading label", () => {
    for (const { lines, count } of [
      { lines: -1, count: 1 },
      { lines: 99, count: 6 },
      { lines: NaN, count: 3 },
    ]) {
      const html = render(createElement(LoadingSkeleton, { lines, label: "Loading VALEXII.AI" }));
      expect(html.match(/<span/g)).toHaveLength(count + 1);
      expect(html).toContain('aria-busy="true"');
      expect(html).toContain('aria-hidden="true"');
    }
  });
  it("disables busy actions without suggesting completion", () => {
    const html = render(
      createElement(ActionButton, {
        busy: true,
        children: "Submit",
        busyLabel: "Preparing draft…",
      }),
    );
    expect(html).toContain("disabled");
    expect(html).toContain("Preparing draft…");
    expect(html).toContain('type="button"');
    expect(html).not.toContain("Submit");
  });
  it("preserves explicit submit type, disabled state and icon label", () => {
    const html = render(
      createElement(Button, {
        type: "submit",
        disabled: true,
        "aria-label": "Send draft",
        size: "icon",
      }),
    );
    expect(html).toContain('type="submit"');
    expect(html).toContain('aria-label="Send draft"');
    expect(html).toContain("disabled");
  });
  it("gives separate state panels unique heading IDs", () => {
    const html = render(
      createElement(
        "div",
        null,
        createElement(StatePanel, { title: "A" }),
        createElement(StatePanel, { title: "B" }),
      ),
    );
    const ids = [...html.matchAll(/aria-labelledby="([^"]+)"/g)].map((m) => m[1]);
    expect(new Set(ids).size).toBe(2);
  });
  it("renders semantic repeatable cards and shrinkable section headings", () => {
    expect(render(createElement(Card, { padding: "compact", children: "Evidence" }))).toContain(
      "<article",
    );
    const html = render(
      createElement(SectionHeader, {
        title: "Research",
        eyebrow: "HOLD",
        copy: "Not a decipherment",
        action: createElement(Button, null, "Review"),
      }),
    );
    expect(html).toContain("<h2");
    expect(html).toContain("min-w-0");
    expect(html).toContain("Not a decipherment");
  });
});
