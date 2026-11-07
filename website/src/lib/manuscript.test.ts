import { describe, expect, it } from "vitest";
import { ManuscriptReportSchema, selectedLayer } from "./manuscript-contract";
import { examineManuscriptFixture } from "./manuscript.server";

const TOKEN = "synthetic-manuscript-token-1234567890";

function layer(method: string) {
  return {
    id: method,
    method,
    parameters: { margin: 12 },
    limitations: ["These pixels are not a transcription."],
    sha256: "ab".repeat(32),
    png_base64: "iVBORw0KGgo=",
    width: 96,
    height: 64,
  };
}

const REPORT = {
  schema: "aurex.manuscript_forensics.report.v1",
  decision: "RECORDED",
  effect: "NONE",
  authority: "NONE",
  financial_authority: "NONE",
  production: "HOLD",
  launch: "NOT_STARTED",
  recovered_text: null,
  decipherment: "NOT_CLAIMED",
  problems: [],
  source_sha256: "cd".repeat(32),
  layers: [layer("original_rgb"), layer("grayscale")],
  regions: [],
  observation: "No component passed the 12-pixel minimum. This is not a reading.",
  fixture: "blank-v1",
};

describe("manuscript report", () => {
  it("rejects a report that claims recovered text", () => {
    expect(ManuscriptReportSchema.safeParse({ ...REPORT, recovered_text: "hello" }).success).toBe(false);
    expect(ManuscriptReportSchema.safeParse({ ...REPORT, effect: "DEPLOY" }).success).toBe(false);
    expect(selectedLayer(ManuscriptReportSchema.parse(REPORT), "grayscale")?.method).toBe("grayscale");
  });

  it("reads a synthetic fixture and refuses a disabled laboratory", async () => {
    const ok = (async (_url: string, init?: RequestInit) => {
      const body = JSON.parse(String(init?.body)) as { effect?: string; dataset_type?: string };
      expect(body.effect).toBe("NONE");
      expect(body.dataset_type).toBe("SYNTHETIC_ONLY");
      return new Response(JSON.stringify(REPORT), { status: 200 });
    }) as typeof fetch;
    const report = await examineManuscriptFixture(
      { serviceUrl: "https://a.example", serviceToken: TOKEN, allowLocal: false },
      "blank-v1",
      ok,
    );
    expect(report.decipherment).toBe("NOT_CLAIMED");
    const disabled = (async () => new Response("FORENSICS_DISABLED", { status: 403 })) as typeof fetch;
    await expect(
      examineManuscriptFixture(
        { serviceUrl: "https://a.example", serviceToken: TOKEN },
        "blank-v1",
        disabled,
      ),
    ).rejects.toThrow("Manuscript laboratory is disabled");
  });
});
