import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
const root = new URL("../", import.meta.url);
const read = name => readFile(new URL(name, root), "utf8");
test("approved command hero keeps frac tree, live buttons, and explicit fictional data labels", async () => {
  const html = await read("index.html");
  for (const phrase of [
    "DISPATER", "FRAC TREE / EQUIPMENT VISUALIZATION", "NO LIVE PRESSURE DATA", "VIEW DETAILS +",
    "REQUEST AN AUDIT", "BOOK A CONSULTATION", "VIEW DEMONSTRATION",
    "OILFIELD OPERATIONS", "TOWING &amp; RECOVERY", "AUDIT INTELLIGENCE",
    "FICTIONAL DEMO DATA", "SIMULATED", "Manager Review Workflow", "/frac-tree.svg",
    "/oilfield-scene.svg", "/tow-recovery.svg", "/audit-intelligence.svg",
    "id=\"audit\"", "id=\"run\"", "id=\"results\"", "id=\"railway-check\"",
  ]) assert.ok(html.includes(phrase), "missing required element: " + phrase);
  assert.ok(html.includes('href="https://valexii.com/contact?service=dispater-audit"'));
  assert.ok(html.includes('href="https://valexii.com/contact?service=dispater-consultation"'));
  assert.ok(html.includes('href="#audit"'));
  assert.ok(html.includes('href="/command.css"'));
  assert.ok(!html.includes("<input type=\"file\""), "never accept customer uploads");
});
test("industrial artwork and generated build assets stay local and reproducible", async () => {
  const build = await read("build.mjs");
  for (const asset of ["command.css", "frac-tree.svg", "oilfield-scene.svg", "tow-recovery.svg", "audit-intelligence.svg"]) {
    assert.ok(build.includes(asset), "asset missing from static bundle " + asset);
    const bytes = await read(asset);
    assert.ok(bytes.length > 100, "asset empty " + asset);
    if (asset.endsWith(".svg")) {
      assert.ok(bytes.startsWith("<svg"));
      assert.ok(bytes.includes("</svg>"));
    }
  }
});
test("audit demo stays browser-only and financial-authority HOLD", async () => {
 const html = await read("index.html");
 const script = await read("audit.mjs");
 assert.ok(html.includes("FICTIONAL DEMONSTRATION"));
 assert.ok(script.includes("NOT CONNECTED"));
 assert.ok(script.includes('authority: "NONE"'));
 assert.ok(!html.includes("api/execute"));
});

test("approved hero stays noninteractive above 3D studio, factory, and command center",async()=>{const html=await read("index.html");const a=html.indexOf('class="approved-hero-reference"');const equipment=html.indexOf('id="equipment-3d"');const f=html.indexOf('class="factory-showcase"');const c=html.indexOf('class="command-hero"');assert.ok(a>0 && equipment>a && f>equipment && c>f);const hero=html.slice(a,equipment);assert.ok(hero.includes('src="/approved-hero.png"'));assert.ok(!hero.includes('<a ') && !hero.includes('<button '));assert.ok(html.includes('src="/industrial-companion.png"'));const css=await read("reference.css");assert.ok(css.includes(".factory-showcase"));const build=await read("build.mjs");assert.ok(build.includes('industrial-companion.png'));});

test("equipment viewer displays frac tree without simulated pressure gauges", async () => {
  const html = await read("index.html");
  const from = html.indexOf('<div class="command-center"');
  const to = html.indexOf('<div class="command-right"', from);
  const viewer = html.slice(from, to);
  assert.ok(from >= 0 && to > from, "equipment viewer exists");
  assert.ok(viewer.includes('id="frac-tree-viewer"'));
  assert.ok(viewer.includes('id="tree-inspect"'));
  assert.ok(viewer.includes('src="/frac-tree.svg"'));
  assert.ok(viewer.includes("NO LIVE PRESSURE DATA"));
  for(const term of ["WELL PRESSURE", "8,450", "42.6", "PROPPANT", "STAGE", "PSI", "BPM"]) {
    assert.ok(!viewer.includes(term), "unexpected pressure/gauge telemetry: " + term);
  }
  const app = await read("app.mjs");
  assert.ok(app.includes('byId("tree-inspect")'));
  assert.ok(app.includes('setAttribute("aria-pressed"'));
  const css = await read("command.css");
  assert.ok(css.includes(".command-center.tree-detail .wellhead-art"));
});
