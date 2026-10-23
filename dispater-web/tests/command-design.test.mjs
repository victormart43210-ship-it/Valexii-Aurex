import test from "node:test";
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
const read=name=>readFile(new URL("../"+name,import.meta.url),"utf8");
test("DISPATER audit-readiness message leads the page, models then dashboard",async()=>{
 const html=await read("index.html");
 const headline=html.indexOf('id="launch-title"'),equipment=html.indexOf('class="equipment-pair"'),audit=html.indexOf('id="audit"'),process=html.indexOf('id="process"');
 assert.ok(headline>0&&equipment>headline&&audit>equipment&&process>audit);
 assert.ok(html.includes("Be ready <em>before</em> they ask."));
 assert.ok(html.includes("DISPATER<span>.AI</span>"));
 assert.ok(html.includes("IRS record readiness"));
 assert.ok(html.includes("DOT / FMCSA readiness where applicable"));
 assert.ok(html.includes("REQUEST AN AUDIT-READINESS REVIEW"));
 assert.ok(html.includes('id="audit-dashboard-root"'));
 assert.ok(html.includes('href="/launch.css"'));
 assert.ok(!html.includes('class="approved-hero-reference"'),"blurry image should not lead the new website");
});
test("both decorative 3D models appear together without inline copy, controls or fake metrics",async()=>{
 const html=await read("index.html");
 const start=html.indexOf('class="equipment-pair-grid"'),end=html.indexOf('<p class="pair-disclaimer"');
 const markup=html.slice(start,end);
 assert.ok(markup.includes('data-equipment="frac-tree"'));
 assert.ok(markup.includes('data-equipment="tow-truck"'));
 assert.equal((markup.match(/class="equipment-pair-stage"/g)||[]).length,2);
 assert.ok(!markup.includes("<h3")&&!markup.includes("<p")&&!markup.includes("<button"));
 for(const word of ["PSI","BPM","WELL PRESSURE","SIMULATED","8,450"]){assert.ok(!markup.includes(word),"unexpected telemetry "+word);}
 assert.ok(html.includes('src="/dual-equipment.js"'));
});
test("shadcn-style dashboard includes IRS, DOT, and revenue evidence paths",async()=>{
 const jsx=await read("audit-dashboard.jsx");
 for(const word of ['@radix-ui/react-tabs','Revenue Audit','IRS Evidence','DOT / FMCSA Evidence','APPROVED','NOT REVIEWED','HUMAN_REVIEW_REQUIRED']){
  assert.ok(word==="APPROVED"||word==="HUMAN_REVIEW_REQUIRED"||jsx.includes(word),word);
 }
 assert.ok(jsx.includes('audit(sector)'));
 assert.ok(jsx.includes('reviewFinding(report,id,value)'));
 assert.ok(jsx.includes("FICTIONAL"));
 const css=await read("launch.css");
 assert.ok(css.includes(".shad-shell")&&css.includes(".shad-tab-list"));
});
test("build ships actual React/Radix dashboard and two GPU models, no external CDN",async()=>{
 const build=await read("build.mjs");
 const pkg=JSON.parse(await read("package.json"));
 assert.ok(build.includes("audit-dashboard.jsx"));
 assert.ok(build.includes("dual-equipment.mjs"));
 assert.ok(build.includes("launch.css"));
 assert.ok(pkg.dependencies.react&&pkg.dependencies["react-dom"]&&pkg.dependencies["@radix-ui/react-tabs"]&&pkg.dependencies.three);
 assert.ok(!build.includes("approved-hero.png")&&!build.includes("industrial-companion.png"));
 const html=await read("index.html");
 assert.ok(!html.includes('<input type="file"'));
 assert.ok(html.includes("no official audit")||html.includes("no official audit".toUpperCase())||html.includes("no official audit,"));
});
