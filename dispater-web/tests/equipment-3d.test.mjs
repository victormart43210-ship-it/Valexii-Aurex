import test from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import { readFile } from "node:fs/promises";
import {createFracTree, createTowTruck, MODEL_INFO} from "../equipment-models.mjs";

function inspectModel(group){
 let meshes=0,invalid=false;
 group.traverse(x=>{if(x.isMesh){meshes++;if(!x.geometry?.attributes?.position)invalid=true;}});
 const bounds=new THREE.Box3().setFromObject(group);
 const size=new THREE.Vector3();bounds.getSize(size);
 return {meshes,invalid,size};
}
test("original frac tree is a real 3D model with valves, not a flat image",()=>{
 const model=createFracTree(),x=inspectModel(model);
 assert.ok(model.isGroup);
 assert.ok(x.meshes>=60,"frac tree contains modeled flanges/bolts/valves");
 assert.equal(x.invalid,false);
 assert.ok(x.size.x>3&&x.size.y>4&&x.size.z>1);
 assert.equal(model.userData.telemetry,false);
 assert.equal(model.userData.classification,"ILLUSTRATIVE_3D_MODEL");
});
test("heavy-duty tow truck has modeled running gear, cab and rear lift",()=>{
 const model=createTowTruck(),x=inspectModel(model);
 assert.ok(model.isGroup);
 assert.ok(x.meshes>=50,"tow truck has actual 3D geometry");
 assert.equal(x.invalid,false);
 assert.ok(x.size.x>6&&x.size.z>2);
 assert.equal(model.userData.telemetry,false);
});
test("both viewer modes are described without readings, writes or certification",async()=>{
 assert.ok(MODEL_INFO["frac-tree"].summary.includes("no pressure data"));
 assert.ok(MODEL_INFO["tow-truck"].summary.includes("no dispatch data"));
 const html=await readFile(new URL("../index.html",import.meta.url),"utf8");
 const stage=html.indexOf('id="equipment-3d"');
 const factory=html.indexOf('class="factory-showcase"');
 const hero=html.indexOf('class="approved-hero-reference"');
 assert.ok(hero<stage && stage<factory,"original hero first, 3D equipment studio second");
 assert.ok(html.includes('id="equipment-frac"'));
 assert.ok(html.includes('id="equipment-tow"'));
 assert.ok(html.includes('src="/equipment-viewer.js"'));
 assert.ok(html.includes('src="/frac-tree.svg"'));
 assert.ok(html.includes('NO LIVE PRESSURE DATA')||html.includes("no pressure numbers"));
 const design=await readFile(new URL("../equipment-viewer.mjs",import.meta.url),"utf8");
 assert.ok(design.includes("OrbitControls"));
 assert.ok(design.includes('getContext("webgl2"'));
 assert.ok(design.includes('INTERACTIVE 3D'));
 assert.ok(!design.includes("API_KEY"));
});
