import { z } from "zod";

const parameter = z.union([z.string(), z.number()]);

export const ManuscriptLayerSchema = z.object({
  id: z.string().min(1).max(80),
  method: z.string().min(1).max(80),
  parameters: z.record(z.string(), parameter),
  limitations: z.array(z.string().min(1).max(400)).min(1).max(6),
  sha256: z.string().regex(/^[0-9a-f]{64}$/),
  png_base64: z.string().min(1).max(500_000),
  width: z.number().int().positive().max(512),
  height: z.number().int().positive().max(512),
});

export const ManuscriptRegionSchema = z.object({
  id: z.string(),
  classification: z.literal("UNVERIFIED_COMPONENT"),
  bbox: z.tuple([z.number().int(), z.number().int(), z.number().int(), z.number().int()]),
  pixels: z.number().int().positive(),
  sha256: z.string().regex(/^[0-9a-f]{64}$/),
  png_base64: z.string().min(1).max(500_000),
  reading: z.null(),
});

export const ManuscriptReportSchema = z.object({
  schema: z.literal("aurex.manuscript_forensics.report.v1"),
  decision: z.enum(["RECORDED", "REFUSED"]),
  effect: z.literal("NONE"),
  authority: z.literal("NONE"),
  financial_authority: z.literal("NONE"),
  production: z.literal("HOLD"),
  launch: z.literal("NOT_STARTED"),
  recovered_text: z.null(),
  decipherment: z.literal("NOT_CLAIMED"),
  problems: z.array(z.string()),
  source_sha256: z.string().nullable(),
  layers: z.array(ManuscriptLayerSchema).max(16),
  regions: z.array(ManuscriptRegionSchema).max(24),
  limitations: z.array(z.string()).optional(),
  observation: z.string().optional(),
  fixture: z.string().optional(),
  filename_label: z.string().optional(),
  sniffed: z.string().optional(),
  width: z.number().int().optional(),
  height: z.number().int().optional(),
  decoded_png_sha256: z.string().optional(),
  tool: z
    .object({
      name: z.literal("aurex.manuscript_forensics"),
      pillow: z.string(),
    })
    .optional(),
});

export type ManuscriptReport = z.infer<typeof ManuscriptReportSchema>;
export type ManuscriptLayer = z.infer<typeof ManuscriptLayerSchema>;

export function selectedLayer(report: ManuscriptReport, method: string): ManuscriptLayer | null {
  return report.layers.find((layer) => layer.method === method) ?? report.layers[0] ?? null;
}
