// Server-only handler for DISPATER reconciliation. No client secrets exposed.
import {
  DispaterReconciliationReportSchema,
  type DispaterReconciliationReport,
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
