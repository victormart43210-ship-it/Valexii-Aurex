import { describe, expect, it } from "vitest";
import {
  createTraceContext,
  formatTraceparent,
  generateSpanId,
  generateTraceId,
  sanitizeTelemetryHeaders,
} from "../lib/telemetry.server";

describe("OpenTelemetry server-side tracing", () => {
  it("generates valid 128-bit trace ID and 64-bit span ID", () => {
    const traceId = generateTraceId();
    const spanId = generateSpanId();
    expect(traceId).toMatch(/^[0-9a-f]{32}$/);
    expect(spanId).toMatch(/^[0-9a-f]{16}$/);
  });

  it("formats W3C traceparent header correctly", () => {
    const traceId = generateTraceId();
    const spanId = generateSpanId();
    expect(formatTraceparent(traceId, spanId, true)).toBe(`00-${traceId}-${spanId}-01`);
    expect(formatTraceparent(traceId, spanId, false)).toBe(`00-${traceId}-${spanId}-00`);
  });

  it("creates trace context and correlates incoming traceparent", () => {
    const incomingTrace = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01";
    const ctx = createTraceContext(incomingTrace);
    expect(ctx.correlationId).toBe("4bf92f3577b34da6a3ce929d0e0e4736");
    expect(ctx.traceparent).toMatch(/^00-[0-9a-f]{32}-[0-9a-f]{16}-01$/);
  });

  it("redacts sensitive authorization headers", () => {
    const headers = {
      "content-type": "application/json",
      authorization: "Bearer secret-token-value",
      cookie: "session=xyz123",
      "x-trace-id": "tr-12345",
    };
    const cleaned = sanitizeTelemetryHeaders(headers);
    expect(cleaned["content-type"]).toBe("application/json");
    expect(cleaned.authorization).toBe("[REDACTED]");
    expect(cleaned.cookie).toBe("[REDACTED]");
    expect(cleaned["x-trace-id"]).toBe("tr-12345");
  });
});
