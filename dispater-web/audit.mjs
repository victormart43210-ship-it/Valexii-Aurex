/**
 * DISPATER — deterministic, fictional-data only browser demonstration.
 * NOT AUREX remote runtime, a legal audit, or a regulated financial service.
 */
export const FIXTURES = {
  towing: {
    title: "Towing & Recovery",
    jobs: [
      { id: "TOW-101", customer: "Example Roadside Club", service: "HOOKUP", day: "2026-10-20" },
      { id: "TOW-102", customer: "Example Roadside Club", service: "RECOVERY", day: "2026-10-21" }
    ],
    rates: [
      { id: "RATE-T-1", customer: "Example Roadside Club", service: "HOOKUP", cents: 18000 },
      { id: "RATE-T-2", customer: "Example Roadside Club", service: "RECOVERY", cents: 30000 }
    ],
    invoices: [{ id: "INV-T-1", job: "TOW-101", cents: 15000, status: "paid" }],
    payments: [{ id: "PAY-T-1", invoice: "INV-T-1", cents: 14000 }],
    evidence: [{ id: "DOC-T-1", domain: "DOT", state: "UNKNOWN", label: "Sample driver/vehicle file applicability" },
      { id: "DOC-T-2", domain: "IRS", state: "MISSING", label: "Sample business receipt index" }]
  },
  oilfield: {
    title: "Oilfield Operations",
    jobs: [
      { id: "WELL-10", customer: "Example Energy Co.", service: "FLOWBACK", day: "2026-10-20" },
      { id: "WELL-11", customer: "Example Energy Co.", service: "FLOWBACK", day: "2026-10-21" }
    ],
    rates: [{ id: "RATE-O-1", customer: "Example Energy Co.", service: "FLOWBACK", cents: 125000 }],
    invoices: [{ id: "INV-O-1", job: "WELL-11", cents: 120000, status: "open" }],
    payments: [],
    evidence: [{ id: "DOC-O-1", domain: "DOT", state: "UNKNOWN", label: "Sample driver qualification applicability" }]
  }
};
export const dollar = cents => "$" + (cents / 100).toFixed(2);
const candidate = (sector, type, subject, title, explanation, references) => ({
  id: sector + "-" + type + "-" + subject,
  type, subject, title, explanation, references,
  disposition: "NOT_REVIEWED", authority: "HUMAN_REVIEW_REQUIRED"
});
export function audit(sector) {
  if (!Object.hasOwn(FIXTURES, sector)) throw new TypeError("Unsupported demo sector");
  const f = FIXTURES[sector], findings = [];
  for (const job of f.jobs) {
    const invoices = f.invoices.filter(i => i.job === job.id);
    const rates = f.rates.filter(r => r.customer === job.customer && r.service === job.service);
    if (invoices.length === 0)
      findings.push(candidate(sector, "UNBILLED_JOB", job.id, "Completed job, no matching invoice",
        "This fictional work ticket has no invoice in the supplied sample.", [job.id]));
    if (invoices.length > 1)
      findings.push(candidate(sector, "MULTIPLE_INVOICES", job.id, "Several invoices share one job",
        "A manager must examine the sources before treating these as duplicates.", [job.id, ...invoices.map(x => x.id)]));
    if (rates.length !== 1)
      findings.push(candidate(sector, "RATE_UNKNOWN", job.id, "Approved rate not established",
        "Exactly one matching sample rate was not found.", [job.id]));
    else if (invoices.length === 1 && invoices[0].cents !== rates[0].cents)
      findings.push(candidate(sector, "RATE_DIFFERENCE", invoices[0].id, "Sample rate and invoice disagree",
        "Invoiced " + dollar(invoices[0].cents) + " versus example rate " + dollar(rates[0].cents) + ".",
        [job.id, rates[0].id, invoices[0].id]));
  }
  for (const invoice of f.invoices) {
    const payments = f.payments.filter(p => p.invoice === invoice.id);
    if (invoice.status === "paid" && payments.reduce((n, p) => n + p.cents, 0) !== invoice.cents)
      findings.push(candidate(sector, "PAID_UNRECONCILED", invoice.id, "Paid status is not reconciled",
        "Fictional invoice value does not match allocated payment records.",
        [invoice.id, ...payments.map(p => p.id)]));
  }
  for (const doc of f.evidence) {
    const unknown = doc.state === "UNKNOWN";
    findings.push(candidate(sector, unknown ? "APPLICABILITY_UNVERIFIED" : "EVIDENCE_INDEX_GAP", doc.id,
      unknown ? "DOT applicability needs specialist review" : "Illustrative document index has a gap",
      unknown ? "No determination has been made about applicable transportation rules." :
        "A fictional record category has no indexed evidence. This is not an IRS finding.",
      [doc.id]));
  }
  return {
    schema: "dispater.synthetic.preview.v1",
    classification: "FICTIONAL_DATA_ONLY",
    sector, asOf: "2026-10-23",
    status: "HOLD", nvidiaInference: "NOT RUN", aurexRuntime: "NOT CONNECTED",
    authority: "NONE", findings,
    counts: { jobs: f.jobs.length, invoices: f.invoices.length, findings: findings.length },
    warning: "Synthetic illustration only. No customer data, tax/DOT compliance decision, secure storage, financial writeback or AI call."
  };
}
export function reviewFinding(report, id, disposition) {
  if (report?.classification !== "FICTIONAL_DATA_ONLY" || report.status !== "HOLD")
    throw new TypeError("Only fictional HOLD reports are reviewable");
  if (!["ACKNOWLEDGED", "DISPUTED", "REFER_TO_SPECIALIST"].includes(disposition))
    throw new TypeError("Unsupported disposition");
  const finding = report.findings.find(f => f.id === id);
  if (!finding) throw new TypeError("Finding not found");
  finding.disposition = disposition;
  return finding;
}
