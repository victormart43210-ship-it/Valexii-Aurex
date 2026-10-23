/**
 * DISPATER 3D viewer. Three.js MIT; original procedural geometry.
 * Client-side scene: static conceptual equipment, never telemetry or operational control.
 */
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { createFracTree, createTowTruck, MODEL_INFO } from "./equipment-models.mjs";

const $ = id => document.getElementById(id);
const viewport = $("equipment-stage");
const fallback = $("equipment-fallback");
const title = $("equipment-title");
const description = $("equipment-description");
const modeButtons = {
 "frac-tree": $("equipment-frac"),
 "tow-truck": $("equipment-tow"),
};
const resetBtn = $("equipment-reset");
const motionBtn = $("equipment-rotation");
const label = $("equipment-status");
if(!viewport||!fallback||!title||!description||!resetBtn||!motionBtn||!label||Object.values(modeButtons).some(x=>!x)){
  throw new Error("DISPATER 3D markup is incomplete");
}
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
let active = "frac-tree";
let engine = null;
let scene, camera, controls, renderer, display, observer, animationId=0;
let showMotion = !reducedMotion.matches;
let intersecting = false;
function displayText(key){
 const info=MODEL_INFO[key];
 title.textContent=info.title;
 description.textContent=info.summary;
 fallback.src=key==="frac-tree"?"/frac-tree.svg":"/tow-recovery.svg";
 fallback.alt=key==="frac-tree"?"Illustrated frac tree / wellhead (2D fallback)":"Tow and recovery vehicle illustration (2D fallback)";
 for(const [name,button] of Object.entries(modeButtons)){
   button.setAttribute("aria-pressed",String(name===key));
   button.classList.toggle("is-active",name===key);
 }
}
function cameraReset(){
 const info=MODEL_INFO[active];
 camera.position.set(...info.camera);
 controls.target.set(0,active==="frac-tree"?2.5:2.2,0);
 controls.minDistance=5;
 controls.maxDistance=info.maxDistance;
 controls.minPolarAngle=.2;
 controls.maxPolarAngle=Math.PI/2.03;
 controls.update();
}
function activate(key){
 if(!Object.hasOwn(MODEL_INFO,key))return;
 active=key;
 displayText(key);
 if(!engine)return;
 if(display) {scene.remove(display);display.traverse(child=>{
   if(child.isMesh){child.geometry?.dispose();}
 }); }
 display=key==="frac-tree"?createFracTree():createTowTruck();
 scene.add(display);
 cameraReset();
 label.textContent="INTERACTIVE 3D · ILLUSTRATIVE MODEL · NO LIVE TELEMETRY";
 draw();
}
function draw(){
 if(!renderer)return;
 controls.update();
 renderer.render(scene,camera);
}
function resize(){
 if(!renderer)return;
 const width=Math.max(240,viewport.clientWidth),height=Math.max(260,viewport.clientHeight);
 camera.aspect=width/height;camera.updateProjectionMatrix();
 renderer.setSize(width,height,false);
 draw();
}
function tick(){
 animationId=0;
 if(!renderer||!intersecting||document.hidden)return;
 controls.autoRotate=showMotion;
 controls.autoRotateSpeed=.46;
 draw();
 if(showMotion || controls.enabled)animationId=requestAnimationFrame(tick);
}
function runLoop(){
 if(animationId)cancelAnimationFrame(animationId);
 animationId=0;
 if(intersecting && !document.hidden)animationId=requestAnimationFrame(tick);
}
function init(){
 if(renderer)return;
 const canvas=document.createElement("canvas");
 canvas.className="equipment-canvas";
 canvas.setAttribute("aria-hidden","true");
 try{
   const gpu=canvas.getContext("webgl2",{alpha:true,antialias:true,powerPreference:"low-power"})||
             canvas.getContext("webgl",{alpha:true,antialias:true,powerPreference:"low-power"});
   if(!gpu)throw new Error("WEBGL_UNSUPPORTED");
   renderer=new THREE.WebGLRenderer({canvas,context:gpu,alpha:true,antialias:true,powerPreference:"low-power"});
   renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.5));
   renderer.setClearColor(0x041522,0);
   renderer.outputColorSpace=THREE.SRGBColorSpace;
   renderer.toneMapping=THREE.ACESFilmicToneMapping;
   renderer.toneMappingExposure=1.65;
   scene=new THREE.Scene();
   scene.fog=new THREE.FogExp2(0x021422,.014);
   camera=new THREE.PerspectiveCamera(44,1,.08,100);
   scene.add(new THREE.HemisphereLight(0xbbeeff,0x0e1726,3.6));
   const keyLight=new THREE.DirectionalLight(0xd7f5ff,5.1);keyLight.position.set(5,10,8);scene.add(keyLight);
   const fill=new THREE.DirectionalLight(0x19bbda,3.5);fill.position.set(-7,5,-6);scene.add(fill);
   const gold=new THREE.PointLight(0xf2bd72,55,20);gold.position.set(-3,7,4);scene.add(gold);
   const accent=new THREE.PointLight(0x00dcee,65,15);accent.position.set(2,1,2);scene.add(accent);
   controls=new OrbitControls(camera,canvas);
   controls.enableDamping=true;controls.dampingFactor=.075;
   controls.enablePan=false;
   controls.rotateSpeed=.67;
   controls.zoomSpeed=.7;
   controls.addEventListener("change",draw);
   viewport.append(canvas);
   fallback.hidden=true;
   engine=true;
   activate(active);
   resize();
   window.addEventListener("resize",resize,{passive:true});
   canvas.addEventListener("webglcontextlost",event=>{
     event.preventDefault();
     label.textContent="3D CONTEXT LOST · 2D EQUIPMENT PREVIEW AVAILABLE";
     fallback.hidden=false;canvas.hidden=true;
     if(animationId)cancelAnimationFrame(animationId);
   });
   canvas.addEventListener("webglcontextrestored",()=>{
     label.textContent="3D CONTEXT RESTORED · ILLUSTRATIVE EQUIPMENT";
     fallback.hidden=true;canvas.hidden=false;resize();runLoop();
   });
   observer=new IntersectionObserver(entries=>{intersecting=entries[0]?.isIntersecting??false;runLoop();},{rootMargin:"120px"});
   observer.observe(viewport);
   document.addEventListener("visibilitychange",runLoop);
   reducedMotion.addEventListener?.("change",event=>{
     if(event.matches){showMotion=false;motionBtn.setAttribute("aria-pressed","false");motionBtn.textContent="START ROTATION";}
     runLoop();
   });
   label.textContent="INTERACTIVE 3D READY · DRAG TO ROTATE · PINCH TO ZOOM";
 }catch(error){
   renderer?.dispose();renderer=null;
   canvas.remove();
   fallback.hidden=false;
   label.textContent="3D UNAVAILABLE · ILLUSTRATIVE 2D EQUIPMENT PREVIEW";
   motionBtn.disabled=true;
   resetBtn.disabled=true;
   console.info("DISPATER equipment viewer fallback active",error?.message||"WEBGL_UNAVAILABLE");
 }
}
for(const [key,button] of Object.entries(modeButtons)){
 button.addEventListener("click",()=>{activate(key);if(!renderer)init();runLoop();});
}
resetBtn.addEventListener("click",()=>{if(renderer)cameraReset();});
motionBtn.setAttribute("aria-pressed",String(showMotion));
motionBtn.textContent=showMotion?"PAUSE ROTATION":"START ROTATION";
motionBtn.addEventListener("click",()=>{
 if(!renderer){init();}
 if(!renderer)return;
 showMotion=!showMotion;
 motionBtn.setAttribute("aria-pressed",String(showMotion));
 motionBtn.textContent=showMotion?"PAUSE ROTATION":"START ROTATION";
 runLoop();
});
displayText(active);
label.textContent="ILLUSTRATIVE 3D · NO LIVE TELEMETRY";
const lazilyStart=new IntersectionObserver(entries=>{
 if(entries[0]?.isIntersecting){
  lazilyStart.disconnect();
  init();
 }
},{rootMargin:"220px"});
lazilyStart.observe(viewport);
