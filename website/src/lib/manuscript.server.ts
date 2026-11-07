import { ManuscriptReportSchema, type ManuscriptReport } from "./manuscript-contract";

export interface ManuscriptServerConfig {
  serviceUrl?: string;
  serviceToken?: string;
  allowLocal?: boolean;
}

const FIXTURES = ["faint-stroke-v1", "blank-v1", "noise-v1", "overlap-v1"] as const;
export type ManuscriptFixture = (typeof FIXTURES)[number];

function resolve(config: ManuscriptServerConfig): { url: URL; token: string } {
  if (!config.serviceUrl || !config.serviceToken) {
    throw new Error("Manuscript laboratory is not configured");
  }
  const url = new URL(config.serviceUrl);
  const local = url.hostname === "127.0.0.1" || url.hostname === "localhost";
  if (url.protocol !== "https:" && !(config.allowLocal && local && url.protocol === "http:")) {
    throw new Error("Manuscript laboratory is not configured");
  }
  return { url, token: config.serviceToken };
}

export function currentManuscriptConfig(): ManuscriptServerConfig {
  const serviceUrl = process.env["AUREX_SERVICE_URL"] ?? process.env["AUREX_STAGING_SERVICE_URL"];
  const serviceToken = process.env["AUREX_SERVICE_TOKEN"] ?? process.env["AUREX_STAGING_SERVICE_TOKEN"];
  return {
    ...(serviceUrl ? { serviceUrl } : {}),
    ...(serviceToken ? { serviceToken } : {}),
    allowLocal: process.env["NODE_ENV"] !== "production",
  };
}

export async function examineManuscriptFixture(
  config: ManuscriptServerConfig,
  fixture: ManuscriptFixture,
  transport: typeof fetch = fetch,
): Promise<ManuscriptReport> {
  if (!FIXTURES.includes(fixture)) throw new Error("Manuscript laboratory returned an invalid report");
  const { url, token } = resolve(config);
  const endpoint = new URL("/v1/manuscript-forensics/examine", url);
  let response: Response;
  try {
    response = await transport(endpoint.toString(), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ dataset_type: "SYNTHETIC_ONLY", fixture, effect: "NONE" }),
      signal: AbortSignal.timeout(8000),
    });
  } catch {
    throw new Error("Manuscript laboratory unreachable");
  }
  if (response.status === 403) throw new Error("Manuscript laboratory is disabled");
  if (!response.ok) throw new Error(`Manuscript laboratory error (${response.status})`);
  const parsed = ManuscriptReportSchema.safeParse(await response.json());
  if (!parsed.success || parsed.data.recovered_text !== null || parsed.data.effect !== "NONE") {
    throw new Error("Manuscript laboratory returned an invalid report");
  }
  return parsed.data;
}
