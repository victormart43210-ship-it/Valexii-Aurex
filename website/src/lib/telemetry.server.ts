/**
 * Server-only OpenTelemetry tracing helper for VALEXII/DISPATER website server functions.
 * Generates W3C compliant traceparent headers and sanitizes sensitive headers.
 */

export function generateTraceId(): string {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

export function generateSpanId(): string {
  const bytes = new Uint8Array(8);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

export function formatTraceparent(traceId: string, spanId: string, sampled = true): string {
  return `00-${traceId}-${spanId}-${sampled ? "01" : "00"}`;
}

export interface TraceContext {
  traceId: string;
  spanId: string;
  correlationId: string;
  traceparent: string;
}

export function createTraceContext(incomingTraceparent?: string): TraceContext {
  const traceId = generateTraceId();
  const spanId = generateSpanId();
  const correlationId = incomingTraceparent?.split("-")[1] || traceId;
  const traceparent = formatTraceparent(traceId, spanId);
  return { traceId, spanId, correlationId, traceparent };
}

export function sanitizeTelemetryHeaders(headers: Record<string, string>): Record<string, string> {
  const result: Record<string, string> = {};
  for (const [key, value] of Object.entries(headers)) {
    const lower = key.toLowerCase();
    if (lower === "authorization" || lower === "cookie" || lower.includes("secret") || lower.includes("token")) {
      result[key] = "[REDACTED]";
    } else {
      result[key] = value;
    }
  }
  return result;
}
