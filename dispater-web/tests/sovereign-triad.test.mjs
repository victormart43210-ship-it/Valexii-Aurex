import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
const read=(file)=>readFile(new URL("../"+file,import.meta.url),"utf8");
test("Roman Dis Pater artwork remains centered between both 3D models",async()=>{
 const html=await read("index.html");
 const a=html.indexOf('data-equipment="frac-tree"');
 const b=html.indexOf('class="sovereign-art-stage"');
 const c=html.indexOf('data-equipment="tow-truck"');
 const d=html.indexOf('id="audit"');
 assert.ok(a>0&&b>a&&c>b&&d>c,"frac tree → Roman art → tow truck → audit");
 const art=html.slice(b,c);
 assert.ok(art.includes('class="sovereign-art-image"'));
 assert.ok(art.includes('dispater-hero.jpg'));
 assert.ok(!art.includes("<h3")&&!art.includes("<button")&&!art.includes("<p"));
 assert.ok(!html.includes("CANONICAL ARTWORK PRESERVED"));
 assert.ok(!html.includes("Dis Pater · Industrial vision"));
});
test("triad remains responsive, isolated from security/audit authority and honors reduced motion",async()=>{
 const css=await read("launch.css"),html=await read("index.html");
 assert.ok(css.includes("grid-template-columns:minmax(0,1fr) minmax(225px,.78fr) minmax(0,1fr)"));
 assert.ok(css.includes("@media(max-width:760px)"));
 assert.ok(css.includes(".sovereign-art-stage"));
 assert.ok(css.includes("prefers-reduced-motion:reduce"));
 assert.equal((html.match(/data-equipment="/g)||[]).length,2);
 assert.ok(html.includes("no official audit")&&html.includes("HUMAN AUTHORITY REQUIRED"));
});
