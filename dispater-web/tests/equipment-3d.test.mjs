import test from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import {readFile} from "node:fs/promises";
import {createFracTree,createTowTruck,MODEL_INFO} from "../equipment-models.mjs";
function describe(root){
 let meshes=0;root.traverse(child=>{if(child.isMesh){meshes++;assert.ok(child.geometry?.attributes?.position);}});
 const bounds=new THREE.Box3().setFromObject(root),size=new THREE.Vector3();bounds.getSize(size);return {meshes,size};
}
test("frac tree is geometric model, has high-pressure hardware but NO live telemetry",()=>{
 const group=createFracTree(),d=describe(group);
 assert.ok(group.isGroup);assert.ok(d.meshes>=60);assert.ok(d.size.y>4);assert.equal(group.userData.telemetry,false);
 assert.equal(group.userData.classification,"ILLUSTRATIVE_3D_MODEL");
});
test("tow truck is independently rotatable 3D geometry, not a decorative PNG",()=>{
 const group=createTowTruck(),d=describe(group);
 assert.ok(group.isGroup);assert.ok(d.meshes>=50);assert.ok(d.size.x>6);assert.equal(group.userData.telemetry,false);
});
test("both models rotate in independent viewports, no visible model explanations",async()=>{
 const html=await readFile(new URL("../index.html",import.meta.url),"utf8");
 const source=await readFile(new URL("../dual-equipment.mjs",import.meta.url),"utf8");
 assert.ok(html.includes('data-equipment="frac-tree"')&&html.includes('data-equipment="tow-truck"'));
 assert.ok(source.includes("OrbitControls")&&source.includes("autoRotate"));
 assert.ok(source.includes("prefers-reduced-motion: reduce"));
 assert.ok(source.includes("getContext(\"webgl2\""));
 assert.ok(source.includes("IntersectionObserver"));
 assert.ok(source.includes("pointer"));
 assert.ok(!source.includes("API_KEY"));
 assert.ok(MODEL_INFO["frac-tree"].summary.includes("no pressure data"));
 assert.ok(MODEL_INFO["tow-truck"].summary.includes("no dispatch data"));
});
