import test from "node:test";
import assert from "node:assert/strict";
import { FIXTURES, audit, reviewFinding, dollar } from "../audit.mjs";

test("both industry fixtures produce bounded synthetic HOLD reports", () => {
  for (const sector of ["towing", "oilfield"]) {
    const out = audit(sector);
    assert.equal(out.classification, "FICTIONAL_DATA_ONLY");
    assert.equal(out.status, "HOLD");
    assert.equal(out.authority, "NONE");
    assert.equal(out.aurexRuntime, "NOT CONNECTED");
    assert.equal(out.nvidiaInference, "NOT RUN");
    assert.equal(out.counts.jobs, FIXTURES[sector].jobs.length);
    assert.ok(out.findings.length >= 2);
    for (const f of out.findings) {
      assert.equal(f.authority, "HUMAN_REVIEW_REQUIRED");
      assert.ok(f.references.length > 0);
    }
  }
});

test("towing example flags missing invoice, rate gap and payment mismatch", () => {
  const types = new Set(audit("towing").findings.map(f => f.type));
  assert.ok(types.has("UNBILLED_JOB"));
  assert.ok(types.has("RATE_DIFFERENCE"));
  assert.ok(types.has("PAID_UNRECONCILED"));
  assert.ok(types.has("APPLICABILITY_UNVERIFIED"));
});

test("oilfield example flags unbilled and rate mismatch but no payment action", () => {
  const result = audit("oilfield");
  const types = new Set(result.findings.map(f => f.type));
  assert.ok(types.has("UNBILLED_JOB"));
  assert.ok(types.has("RATE_DIFFERENCE"));
  assert.ok(result.findings.every(f => f.authority === "HUMAN_REVIEW_REQUIRED"));
});

test("review acknowledgement never upgrades authority or report status", () => {
  const result = audit("towing");
  const first = result.findings[0];
  const changed = reviewFinding(result, first.id, "ACKNOWLEDGED");
  assert.equal(changed.disposition, "ACKNOWLEDGED");
  assert.equal(result.status, "HOLD");
  assert.equal(result.authority, "NONE");
  assert.throws(() => reviewFinding(result, first.id, "APPROVE_PAYMENT"));
  assert.throws(() => reviewFinding(result, "missing", "ACKNOWLEDGED"));
});

test("invalid industries are rejected and all example dollars are fictional", () => {
  assert.throws(() => audit("production"));
  assert.equal(dollar(18000), "$180.00");
  assert.deepEqual(audit("towing"), audit("towing"));
});
