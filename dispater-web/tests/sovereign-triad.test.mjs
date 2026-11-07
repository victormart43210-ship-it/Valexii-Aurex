import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
const read=(file)=>readFile(new URL("../"+file,import.meta.url),"utf8");
test("Roman Dis Pater artwork is preserved and tow truck is relocated into the process",async()=>{
 const html=await read("index.html");
 const a=html.indexOf('data-equipment="frac-tree"');
 const b=html.indexOf('class="sovereign-art-stage"');
 const c=html.indexOf('data-equipment="tow-truck"');
 const d=html.indexOf('id="audit"');
 const process=html.indexOf('id="process"');
 assert.ok(a>0&&b>a&&d>b&&process>d&&c>process,"frac tree → Roman art → audit → process tow truck");
 const art=html.slice(b,html.indexOf('</figure>',b));
 assert.ok(art.includes('class="sovereign-art-image"'));
 assert.ok(art.includes('dispater-hero.jpg'));
 assert.ok(!art.includes("<h3")&&!art.includes("<button")&&!art.includes("<p"));
 assert.ok(!html.includes("CANONICAL ARTWORK PRESERVED"));
 assert.ok(!html.includes("Dis Pater · Industrial vision"));
});
test("triad remains responsive, isolated from security/audit authority and honors reduced motion",async()=>{
 const css=await read("launch.css"),html=await read("index.html");
 assert.ok(css.includes(".equipment-pair-grid:has(> .sovereign-art-stage)"));
 assert.ok(css.includes("@media(max-width:620px)"));
 assert.ok(css.includes(".sovereign-art-stage"));
 assert.ok(css.includes("prefers-reduced-motion:reduce"));
 assert.equal((html.match(/data-equipment="/g)||[]).length,2);
 assert.ok(html.includes("no official audit")&&html.includes("HUMAN AUTHORITY REQUIRED"));
});
