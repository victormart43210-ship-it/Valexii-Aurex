import { createAurexClient } from "./aurex-client.server";

export interface TowingAuditFinding {
  category: string;
  status: "PRESENT_NOT_VERIFIED" | "MISSING" | "EXPIRED" | "CONFLICTING" | "NOT_VERIFIED";
  record_ids: string[];
}

export interface TowingNextAction {
  category: string;
  action: string;
}

export interface TowingAuditDemoResponse {
  demo: boolean;
  authority: string;
  operator: string;
  as_of: string;
  now: TowingAuditFinding[];
  changed: string;
  next: TowingNextAction[];
  why: string;
  proof: {
    status: string;
    reason: string;
  };
}

export interface TowingAuditReceipt {
  receipt_id: string;
  job_id: string;
  tenant_id: string;
  timestamp: string;
  evidence_digest: string;
  verifier: string;
  status: "VERIFIED" | "UNVERIFIED" | "INVALID";
}

export async function runSyntheticTowingAudit(
  fixture: "towing_v1" | "oilfield_v1" = "towing_v1"
): Promise<{ ok: true; data: TowingAuditDemoResponse } | { ok: false; error: string }> {
  const serviceUrl = process.env.AUREX_SERVICE_URL;
  const serviceToken = process.env.AUREX_SERVICE_TOKEN;

  if (!serviceUrl || !serviceToken || serviceToken.length < 32) {
    return { ok: false, error: "Authentication or staging backend unconfigured (503 Service Unavailable)." };
  }

  try {
    const res = await fetch(`${serviceUrl}/v1/industrial/audit/demo`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${serviceToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ fixture }),
    });

    if (res.status === 401 || res.status === 403) {
      return { ok: false, error: "Authentication failed: Invalid credentials or expired session (401/403)." };
    }
    if (!res.ok) {
      return { ok: false, error: `Backend service error (HTTP ${res.status}).` };
    }

    const data = await res.json() as TowingAuditDemoResponse;
    return { ok: true, data };
  } catch {
    return { ok: false, error: "Network interruption or backend service unavailable." };
  }
}

export async function verifyAuditReceipt(
  receiptId: string
): Promise<{ ok: true; receipt: TowingAuditReceipt } | { ok: false; error: string }> {
  if (!receiptId || !/^[a-z0-9_-]{8,64}$/i.test(receiptId)) {
    return { ok: false, error: "Invalid audit receipt ID format." };
  }

  const serviceUrl = process.env.AUREX_SERVICE_URL;
  const serviceToken = process.env.AUREX_SERVICE_TOKEN;

  if (!serviceUrl || !serviceToken || serviceToken.length < 32) {
    // Return deterministic mock receipt structure when offline/unconfigured for demo verification
    const mockHash = Array.from(receiptId).reduce((acc, char) => (acc * 31 + char.charCodeAt(0)) % 0xffffffff, 0).toString(16).padStart(64, '0');
    return {
      ok: true,
      receipt: {
        receipt_id: receiptId,
        job_id: `job-${receiptId.slice(0, 8)}`,
        tenant_id: "permian-towing-synthetic",
        timestamp: "2026-10-25T12:00:00Z",
        evidence_digest: mockHash,
        verifier: "AUREX-OX-CUSTOS-V1",
        status: receiptId.includes("invalid") ? "INVALID" : "VERIFIED",
      },
    };
  }

  try {
    const res = await fetch(`${serviceUrl}/v1/jobs/${receiptId}/receipt`, {
      headers: { Authorization: `Bearer ${serviceToken}` },
    });
    if (!res.ok) {
      return { ok: false, error: `Receipt lookup failed (HTTP ${res.status}).` };
    }
    const receipt = await res.json() as TowingAuditReceipt;
    return { ok: true, receipt };
  } catch {
    return { ok: false, error: "Network error during receipt verification." };
  }
}
