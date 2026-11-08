import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";
import { type DispaterReconciliationReport } from "./dispater-contract";

export const runDispaterDemoReconciliation = createServerFn({ method: "POST" })
  .validator((input: unknown) => {
    return z
      .object({
        fixture: z.enum(["oilfield_demo_v1", "clean_control_v1"]).default("oilfield_demo_v1"),
      })
      .parse(input);
  })
  .handler(async ({ data }) => {
    const { currentDispaterConfig, executeDispaterReconciliation, getFixture } = await import(
      "./dispater.server"
    );
    const report: DispaterReconciliationReport = await executeDispaterReconciliation(
      currentDispaterConfig(),
      getFixture(data.fixture),
    );
    return report;
  });

export const admitSyntheticDispaterDocument = createServerFn({ method: "POST" })
  .validator((input: unknown) => z.object({ kind: z.enum(["csv", "pdf"]).default("csv") }).strict().parse(input ?? {}))
  .handler(async ({ data }) => {
    const { currentDispaterConfig, executeDispaterDocument } = await import("./dispater.server");
    const admitted = await executeDispaterDocument(currentDispaterConfig(), fetch, data.kind);
    return {
      report: admitted.report,
      source: {
        filename: admitted.ingestion.filename,
        source_sha256: admitted.ingestion.source_sha256,
        rows: admitted.ingestion.provenance.map((item) => item.row),
        kind: data.kind,
      },
    };
  });

export const readDispaterStoredRun = createServerFn({ method: "POST" })
  .validator((input: unknown) =>
    z.object({ runId: z.string().regex(/^run-[0-9a-f]{32}$/) }).parse(input),
  )
  .handler(async ({ data }) => {
    const { currentDispaterConfig, readDispaterRun } = await import("./dispater.server");
    return readDispaterRun(currentDispaterConfig(), data.runId);
  });

export const listDispaterStoredRuns = createServerFn({ method: "GET" }).handler(async () => {
  const { currentDispaterConfig, listDispaterRuns } = await import("./dispater.server");
  return listDispaterRuns(currentDispaterConfig());
});

export const exportVerifiedDispaterRun = createServerFn({ method: "POST" })
  .validator((input: unknown) =>
    z.object({ runId: z.string().regex(/^run-[0-9a-f]{32}$/) }).parse(input),
  )
  .handler(async ({ data }) => {
    const { currentDispaterConfig, exportVerifiedDispaterRun: exportRun } = await import(
      "./dispater.server"
    );
    return exportRun(currentDispaterConfig(), data.runId);
  });

export const runGoldenLedger = createServerFn({ method: "POST" })
  .validator((input: unknown) => z.object({}).parse(input ?? {}))
  .handler(async () => {
    const { currentDispaterConfig, executeGoldenLedger } = await import("./dispater.server");
    return executeGoldenLedger(currentDispaterConfig());
  });

export const recordDispaterObservation = createServerFn({ method: "POST" })
  .validator((input: unknown) =>
    z.object({ sourceSha256: z.string().regex(/^[0-9a-f]{64}$/) }).parse(input),
  )
  .handler(async ({ data }) => {
    const { currentDispaterConfig, recordSyntheticObservation } = await import("./dispater.server");
    return recordSyntheticObservation(currentDispaterConfig(), data.sourceSha256);
  });
