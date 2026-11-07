// Server-only handler for DISPATER reconciliation. No client secrets exposed.
import {
  DispaterDocumentIngestionSchema,
  DispaterReconciliationReportSchema,
  DispaterRunListSchema,
  DispaterVerifiedExportSchema,
  ObservationDecisionSchema,
  type DispaterDocumentIngestion,
  type DispaterReconciliationReport,
  type DispaterRunList,
  type DispaterVerifiedExport,
  type ObservationDecision,
} from "./dispater-contract";

const OILFIELD_SYNTHETIC_FIXTURE: Record<string, unknown> = {
  tenant_id: "demo-oilfield-tenant",
  dataset_type: "SYNTHETIC_ONLY",
  jobs: [
    {
      job_id: "FT-WELL-104",
      customer_id: "APACHE-BASIN-OPERATOR",
      service_code: "PRESSURE_PUMPING",
      date: "2026-10-20",
    },
    {
      job_id: "FT-FLOWBACK-08",
      customer_id: "PERMIAN-RECOVERY-LLC",
      service_code: "FLOWBACK_CREW",
      date: "2026-10-22",
    },
  ],
  rates: [
    {
      rate_id: "RATE-PP-2026",
      customer_id: "APACHE-BASIN-OPERATOR",
      service_code: "PRESSURE_PUMPING",
      start: "2026-01-01",
      end: "2026-12-31",
      amount: "4500.00",
    },
    {
      rate_id: "RATE-FB-2026",
      customer_id: "PERMIAN-RECOVERY-LLC",
      service_code: "FLOWBACK_CREW",
      start: "2026-01-01",
      end: "2026-12-31",
      amount: "1250.00",
    },
  ],
  invoices: [
    {
      invoice_id: "INV-PP-104-A",
      job_id: "FT-WELL-104",
      amount: "5000.00", // Deliberate billing discrepancy: $5000 billed vs $4500 rate ($500 exposure)
      status: "open",
    },
    // FT-FLOWBACK-08 intentionally has no invoice: detects UNBILLED_JOB ($1250 exposure)
  ],
  payments: [],
};


export const CLEAN_CONTROL_FIXTURE: Record<string, unknown> = {
  tenant_id: "demo-oilfield-tenant",
  dataset_type: "SYNTHETIC_ONLY",
  jobs: [
    {
      job_id: "FT-CLEAN-01",
      customer_id: "PERMIAN-ALPHA-CORP",
      service_code: "PRESSURE_PUMPING",
      date: "2026-10-25",
    },
  ],
  rates: [
    {
      rate_id: "RATE-CLEAN-01",
      customer_id: "PERMIAN-ALPHA-CORP",
      service_code: "PRESSURE_PUMPING",
      start: "2026-01-01",
      end: "2026-12-31",
      amount: "3000.00",
    },
  ],
  invoices: [
    { invoice_id: "INV-CLEAN-01", job_id: "FT-CLEAN-01", amount: "3000.00", status: "open" },
  ],
  payments: [],
};

export class DispaterConfigError extends Error {
  constructor() {
    super("DISPATER backend is not configured");
    this.name = "DispaterConfigError";
  }
}

export interface DispaterServerConfig {
  serviceUrl?: string | undefined;
  serviceToken?: string | undefined;
  tenantId?: string | undefined;
  allowLocal?: boolean | undefined;
}

const TENANT_RE = /^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$/;

export function currentDispaterConfig(): DispaterServerConfig {
  return {
    serviceUrl: process.env["AUREX_SERVICE_URL"] ?? process.env["AUREX_STAGING_SERVICE_URL"],
    serviceToken: process.env["AUREX_SERVICE_TOKEN"] ?? process.env["AUREX_STAGING_SERVICE_TOKEN"],
    tenantId: process.env["DISPATER_TENANT_ID"],
    allowLocal: process.env["NODE_ENV"] !== "production",
  };
}

// Fails closed: no localhost or placeholder-token fallback. Local URLs need explicit non-production opt-in.
export function resolveDispaterConfig(config: DispaterServerConfig): {
  url: URL;
  token: string;
  tenantId: string;
} {
  const { serviceUrl, serviceToken, tenantId = "demo-oilfield-tenant" } = config;
  if (!serviceUrl || !serviceToken || serviceToken.length < 32 || !TENANT_RE.test(tenantId)) {
    throw new DispaterConfigError();
  }
  let url: URL;
  try {
    url = new URL(serviceUrl);
  } catch {
    throw new DispaterConfigError();
  }
  const local = ["localhost", "127.0.0.1", "[::1]"].includes(url.hostname);
  if (url.protocol !== "https:" && !(config.allowLocal && local && url.protocol === "http:")) {
    throw new DispaterConfigError();
  }
  if (local && !config.allowLocal) throw new DispaterConfigError();
  return { url, token: serviceToken, tenantId };
}

export function getFixture(name: "oilfield_demo_v1" | "clean_control_v1"): Record<string, unknown> {
  return name === "clean_control_v1" ? CLEAN_CONTROL_FIXTURE : OILFIELD_SYNTHETIC_FIXTURE;
}

export async function executeDispaterReconciliation(
  config: DispaterServerConfig,
  customDataset?: Record<string, unknown>,
  transport: typeof fetch = fetch,
): Promise<DispaterReconciliationReport> {
  const { url, token, tenantId } = resolveDispaterConfig(config);
  // Tenant comes from server configuration, never from the browser.
  const payload = { ...(customDataset ?? OILFIELD_SYNTHETIC_FIXTURE), tenant_id: tenantId };
  const endpoint = new URL("/v1/dispater/reconciliation", url).toString();

  let response: Response;
  try {
    response = await transport(endpoint, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(6000),
    });
  } catch {
    throw new Error("DISPATER backend unreachable");
  }

  if (!response.ok) {
    // Backend bodies are never forwarded to the browser.
    throw new Error(`DISPATER API error (${response.status})`);
  }
  const parsed = DispaterReconciliationReportSchema.safeParse(await response.json());
  if (!parsed.success) throw new Error("DISPATER API returned an invalid report");
  return parsed.data;
}

export async function readDispaterRun(
  config: DispaterServerConfig,
  runId: string,
  transport: typeof fetch = fetch,
): Promise<DispaterReconciliationReport> {
  const { url, token, tenantId } = resolveDispaterConfig(config);
  if (!/^run-[0-9a-f]{32}$/.test(runId)) throw new Error("DISPATER API returned an invalid report");
  const endpoint = new URL(`/v1/dispater/runs/${runId}`, url);
  endpoint.searchParams.set("tenant_id", tenantId);
  let response: Response;
  try {
    response = await transport(endpoint.toString(), {
      method: "GET",
      headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
      signal: AbortSignal.timeout(6000),
    });
  } catch {
    throw new Error("DISPATER backend unreachable");
  }
  if (!response.ok) throw new Error(`DISPATER API error (${response.status})`);
  const parsed = DispaterReconciliationReportSchema.safeParse(await response.json());
  if (!parsed.success || parsed.data.tenant_id !== tenantId || parsed.data.run_id !== runId) {
    throw new Error("DISPATER API returned an invalid report");
  }
  return parsed.data;
}

const SYNTHETIC_CSV = new TextEncoder().encode(
  "invoices,invoice_id,job_id,amount,status\ninvoices,I-SYN,MISSING,10.00,open\n",
);

export async function listDispaterRuns(
  config: DispaterServerConfig,
  transport: typeof fetch = fetch,
): Promise<DispaterRunList> {
  const { url, token, tenantId } = resolveDispaterConfig(config);
  const endpoint = new URL("/v1/dispater/runs", url);
  endpoint.searchParams.set("tenant_id", tenantId);
  endpoint.searchParams.set("limit", "8");
  let response: Response;
  try {
    response = await transport(endpoint.toString(), {
      method: "GET",
      headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
      signal: AbortSignal.timeout(6000),
    });
  } catch {
    throw new Error("DISPATER backend unreachable");
  }
  if (!response.ok) throw new Error(`DISPATER API error (${response.status})`);
  const parsed = DispaterRunListSchema.safeParse(await response.json());
  if (!parsed.success || parsed.data.tenant_id !== tenantId || parsed.data.count !== parsed.data.runs.length) {
    throw new Error("DISPATER API returned an invalid report");
  }
  return parsed.data;
}

export async function exportVerifiedDispaterRun(
  config: DispaterServerConfig,
  runId: string,
  transport: typeof fetch = fetch,
): Promise<DispaterVerifiedExport> {
  const { url, token, tenantId } = resolveDispaterConfig(config);
  if (!/^run-[0-9a-f]{32}$/.test(runId)) throw new Error("DISPATER API returned an invalid report");
  const endpoint = new URL(`/v1/dispater/runs/${runId}/export`, url);
  endpoint.searchParams.set("tenant_id", tenantId);
  endpoint.searchParams.set("format", "json");
  let response: Response;
  try {
    response = await transport(endpoint.toString(), {
      method: "GET",
      headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
      signal: AbortSignal.timeout(6000),
    });
  } catch {
    throw new Error("DISPATER backend unreachable");
  }
  if (!response.ok) throw new Error(`DISPATER API error (${response.status})`);
  const parsed = DispaterVerifiedExportSchema.safeParse(await response.json());
  if (
    !parsed.success ||
    parsed.data.receipt_authenticity === "FAIL" ||
    parsed.data.report.tenant_id !== tenantId ||
    parsed.data.report.run_id !== runId
  ) {
    throw new Error("DISPATER API returned an invalid report");
  }
  return parsed.data;
}

export async function recordSyntheticObservation(
  config: DispaterServerConfig,
  sourceSha256: string,
  transport: typeof fetch = fetch,
): Promise<ObservationDecision> {
  const { url, token, tenantId } = resolveDispaterConfig(config);
  if (!/^[0-9a-f]{64}$/.test(sourceSha256)) throw new Error("DISPATER API returned an invalid report");
  const endpoint = new URL("/v1/dispater/observations", url).toString();
  let response: Response;
  try {
    response = await transport(endpoint, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        tenant_id: tenantId,
        source_sha256: sourceSha256,
        observed_at: new Date().toISOString(),
        hypothesis: "The stored synthetic receipt matches the report on screen.",
        counterevidence: ["This session produced both the receipt and the observation."],
        effect: "NONE",
      }),
      signal: AbortSignal.timeout(6000),
    });
  } catch {
    throw new Error("DISPATER backend unreachable");
  }
  if (!response.ok) throw new Error(`DISPATER API error (${response.status})`);
  const parsed = ObservationDecisionSchema.safeParse(await response.json());
  if (!parsed.success || parsed.data.tenant_id !== tenantId || parsed.data.effect !== "NONE") {
    throw new Error("DISPATER API returned an invalid report");
  }
  return parsed.data;
}

function bytesToBase64(bytes: Uint8Array): string {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
}

export async function executeDispaterDocument(
  config: DispaterServerConfig,
  transport: typeof fetch = fetch,
): Promise<DispaterDocumentIngestion> {
  const { url, token, tenantId } = resolveDispaterConfig(config);
  const endpoint = new URL("/v1/dispater/documents", url).toString();
  let response: Response;
  try {
    response = await transport(endpoint, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        tenant_id: tenantId,
        filename: "synthetic-invoice.csv",
        kind: "csv",
        content_base64: bytesToBase64(SYNTHETIC_CSV),
      }),
      signal: AbortSignal.timeout(6000),
    });
  } catch {
    throw new Error("DISPATER backend unreachable");
  }
  if (!response.ok) throw new Error(`DISPATER API error (${response.status})`);
  const parsed = DispaterDocumentIngestionSchema.safeParse(await response.json());
  if (!parsed.success) throw new Error("DISPATER API returned an invalid report");
  if (parsed.data.report.tenant_id !== tenantId) throw new Error("DISPATER API returned an invalid report");
  return parsed.data;
}
