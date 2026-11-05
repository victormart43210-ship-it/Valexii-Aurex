// Server-only handler for DISPATER reconciliation. No client secrets exposed.
import {
  DispaterReconciliationReportSchema,
  type DispaterReconciliationReport,
} from "./dispater-contract";

const OILFIELD_SYNTHETIC_FIXTURE = {
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

export async function executeDispaterReconciliation(
  config: {
    serviceUrl?: string | undefined;
    serviceToken?: string | undefined;
  },
  customDataset?: unknown,
  transport: typeof fetch = fetch,
): Promise<DispaterReconciliationReport> {
  const url = config.serviceUrl ?? "http://127.0.0.1:8000";
  const token = config.serviceToken ?? "0".repeat(32);
  const payload = customDataset ?? OILFIELD_SYNTHETIC_FIXTURE;

  const endpoint = new URL("/v1/dispater/reconciliation", url).toString();

  const response = await transport(endpoint, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(6000),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`DISPATER API error (${response.status}): ${errorText}`);
  }

  const rawJson = await response.json();
  return DispaterReconciliationReportSchema.parse(rawJson);
}
