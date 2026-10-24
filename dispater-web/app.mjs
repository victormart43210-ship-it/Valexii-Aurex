import { FIXTURES, audit, reviewFinding } from "./audit.mjs";
const byId = id => document.getElementById(id);
const make = (tag, value, cls) => {
  const e = document.createElement(tag);
  e.textContent = value;
  if (cls) e.className = cls;
  return e;
};
let activeSector = "towing";
let current = null;
function setSector(sector) {
  if (!Object.hasOwn(FIXTURES, sector)) return;
  activeSector = sector;
  current = null;
  const example = FIXTURES[sector];
  byId("sector-name").textContent = example.title;
  byId("towing").setAttribute("aria-pressed", String(sector === "towing"));
  byId("oilfield").setAttribute("aria-pressed", String(sector === "oilfield"));
  byId("jobs").textContent = String(example.jobs.length);
  byId("invoices").textContent = String(example.invoices.length);
  byId("findings").textContent = "—";
  byId("export").disabled = true;
  byId("results").replaceChildren(make("p", "Run the example audit to see fictional review candidates.", "empty"));
}
function render() {
  const items = byId("results");
  items.replaceChildren();
  byId("findings").textContent = String(current.findings.length);
  if (!current.findings.length) {
    items.append(make("p", "No candidate findings in this fictional snapshot. This does not prove compliance.", "empty"));
    return;
  }
  for (const f of current.findings) {
    const card = make("article", "", "finding");
    const heading = make("h4", f.title);
    const desc = make("p", f.explanation);
    const refs = make("code", "EVIDENCE REFERENCES: " + f.references.join(" · "));
    const label = make("label", "Manager review (demo only)");
    const select = document.createElement("select");
    select.setAttribute("aria-label", "Disposition for " + f.title);
    for (const code of ["NOT_REVIEWED", "ACKNOWLEDGED", "DISPUTED", "REFER_TO_SPECIALIST"]) {
      const option = make("option", code.replaceAll("_", " "));
      option.value = code;
      select.append(option);
    }
    select.value = f.disposition;
    select.addEventListener("change", () => {
      if (select.value === "NOT_REVIEWED") {
        f.disposition = "NOT_REVIEWED";
      } else {
        reviewFinding(current, f.id, select.value);
      }
    });
    label.append(select);
    card.append(heading, desc, refs, label);
    items.append(card);
  }
}
byId("towing").addEventListener("click", () => setSector("towing"));
byId("oilfield").addEventListener("click", () => setSector("oilfield"));
byId("run").addEventListener("click", () => {
  current = audit(activeSector);
  render();
  byId("export").disabled = false;
});
byId("export").addEventListener("click", () => {
  if (!current) return;
  const copy = { ...current, exportType: "SYNTHETIC_DEMO_NOT_REGULATORY_OR_FINANCIAL_REPORT" };
  const blob = new Blob([JSON.stringify(copy, null, 2) + "\n"], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "dispater-" + activeSector + "-FICTIONAL-report.json";
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
});
setSector("towing");

const checkRailway = byId("railway-check");
if (checkRailway) {
  checkRailway.addEventListener("click", async () => {
    const status = byId("railway-result");
    checkRailway.disabled = true;
    status.textContent = "Checking read-only staging health …";
    try {
      const response = await fetch("/api/railway-status", { method: "GET", cache: "no-store", credentials: "same-origin" });
      if (!response.ok) throw new Error("PROBE_NOT_VERIFIED");
      const result = await response.json();
      if (result.stagingReachability === "HEALTH_ENDPOINT_RESPONDED")
        status.textContent = "RAILWAY HEALTH: ENDPOINT RESPONDED · FINANCIAL AUDIT: NOT CONNECTED · AUTHORITY: NONE";
      else
        status.textContent = "RAILWAY HEALTH: NOT VERIFIED · FINANCIAL AUDIT: NOT CONNECTED · AUTHORITY: NONE";
    } catch {
      status.textContent = "RAILWAY HEALTH: NOT VERIFIED · CHECK UNAVAILABLE · NO FINANCIAL ACTION";
    } finally {
      checkRailway.disabled = false;
    }
  });
}

/* View-only equipment interaction; never reads or computes sensor pressure. */
const treeInspect = byId("tree-inspect");
const treeViewer = byId("frac-tree-viewer");
if (treeInspect && treeViewer) {
  treeInspect.addEventListener("click", () => {
    const detailed = treeInspect.getAttribute("aria-pressed") !== "true";
    treeInspect.setAttribute("aria-pressed", String(detailed));
    treeInspect.setAttribute("aria-label", detailed ? "Return to full frac tree view" : "Zoom in on the frac tree");
    treeInspect.textContent = detailed ? "VIEW FULL TREE −" : "VIEW DETAILS +";
    treeViewer.classList.toggle("tree-detail", detailed);
  });
}
