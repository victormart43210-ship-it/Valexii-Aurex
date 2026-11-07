/**
 * DISPATER twin-equipment showcase. Two independently orbitable conceptual 3D models.
 * Three.js MIT, original local geometry; NO sensors, operational data, API calls, writes.
 */
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { createFracTree, createTowTruck } from "./equipment-models.mjs";
const reduced=window.matchMedia("(prefers-reduced-motion: reduce)");
const targetList=[...document.querySelectorAll("[data-equipment]")];
const instances=[];
function init(stage) {
  const type=stage.dataset.equipment;
  if(!["frac-tree","tow-truck"].includes(type))return;
  const canvas=document.createElement("canvas");
  canvas.className="pair-canvas";
  canvas.setAttribute("aria-hidden","true");
  let renderer,observer,resizeObserver,anim=0,scene,camera,control,visible=false,active=false;
  const fallback=stage.querySelector(".pair-fallback");
  let lastTime=0,contextLost=false;
  const redraw=()=>{if(renderer&&!contextLost)renderer.render(scene,camera);};
  function fit(){
    if(!renderer)return;
    const w=Math.max(260,stage.clientWidth),h=Math.max(240,stage.clientHeight);
    camera.aspect=w/h;
    camera.updateProjectionMatrix();
    renderer.setSize(w,h,false);
    redraw();
  }
  function frame(t){
    anim=0;
    if(!renderer||!visible||document.hidden||contextLost)return;
    if(t-lastTime>=33){
      lastTime=t;
      control.autoRotate=!reduced.matches;
      control.autoRotateSpeed=.42;
      control.update();
      redraw();
    }
    anim=requestAnimationFrame(frame);
  }
  function schedule(){
    if(anim)cancelAnimationFrame(anim);
    anim=0;
    if(visible&&!document.hidden&&!contextLost&&renderer)anim=requestAnimationFrame(frame);
  }
  try{
    const gpu=canvas.getContext("webgl2",{antialias:true,alpha:true,powerPreference:"low-power"})||
              canvas.getContext("webgl",{antialias:true,alpha:true,powerPreference:"low-power"});
    if(!gpu)throw Error("WEBGL_UNAVAILABLE");
    renderer=new THREE.WebGLRenderer({canvas,context:gpu,alpha:true,antialias:true,powerPreference:"low-power"});
    renderer.setClearColor(0x031522,0);
    renderer.outputColorSpace=THREE.SRGBColorSpace;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.3));
    renderer.toneMapping=THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure=1.65;
    scene=new THREE.Scene();
    camera=new THREE.PerspectiveCamera(type==="frac-tree"?43:42,1,.1,90);
    const target=type==="frac-tree"?new THREE.Vector3(0,2.5,0):new THREE.Vector3(0,2.1,0);
    const coordinates=type==="frac-tree"?[8.6,6.8,10.5]:[11,7.7,13.4];
    camera.position.set(...coordinates);
    scene.add(new THREE.HemisphereLight(0xd0f5ff,0x0b2636,3.1));
    const sun=new THREE.DirectionalLight(0xfff3df,4.4);sun.position.set(5,12,6);scene.add(sun);
    const blue=new THREE.DirectionalLight(0x18d8ef,3.4);blue.position.set(-8,6,-3);scene.add(blue);
    const glow=new THREE.PointLight(0x2fdaec,55,18);glow.position.set(2,5,7);scene.add(glow);
    const warm=new THREE.PointLight(0xeabb66,29,22);warm.position.set(-4,3,-4);scene.add(warm);
    scene.add(type==="frac-tree"?createFracTree():createTowTruck());
    control=new OrbitControls(camera,canvas);
    control.target.copy(target);
    control.enableDamping=true;
    control.dampingFactor=.075;
    control.enablePan=false;
    control.enableZoom=true;
    control.minDistance=4.8;
    control.maxDistance=type==="frac-tree"?23:28;
    control.minPolarAngle=.15;
    control.maxPolarAngle=Math.PI*.66;
    control.autoRotate=!reduced.matches;
    control.autoRotateSpeed=.42;
    control.rotateSpeed=.65;
    control.zoomSpeed=.7;
    control.update();
    control.addEventListener("change",redraw);
    stage.appendChild(canvas);
    fallback.hidden=true;
    canvas.addEventListener("webglcontextlost",event=>{
      event.preventDefault();contextLost=true;fallback.hidden=false;canvas.hidden=true;schedule();
    });
    canvas.addEventListener("webglcontextrestored",()=>{
      contextLost=false;fallback.hidden=true;canvas.hidden=false;fit();schedule();
    });
    observer=new IntersectionObserver(entries=>{
      visible=entries[0]?.isIntersecting||false;schedule();
    },{rootMargin:"140px"});
    observer.observe(stage);
    resizeObserver=new ResizeObserver(()=>fit());
    resizeObserver.observe(stage);
    stage.addEventListener("keydown",event=>{
      if(!["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","+","-"].includes(event.key))return;
      event.preventDefault();
      if(event.key==="+"||event.key==="-"){
        const k=event.key==="+"?.87:1.14;
        camera.position.sub(target).multiplyScalar(k).add(target);
      }else{
        const delta=event.key==="ArrowLeft"?.13:event.key==="ArrowRight"?-.13:0;
        camera.position.sub(target).applyAxisAngle(new THREE.Vector3(0,1,0),delta).add(target);
        if(event.key==="ArrowUp"||event.key==="ArrowDown")camera.position.y+=(event.key==="ArrowUp"?-.22:.22);
      }
      control.update();redraw();
    });
    fit();
    window.addEventListener("resize",fit,{passive:true});
    document.addEventListener("visibilitychange",schedule);
    reduced.addEventListener?.("change",schedule);
    instances.push({stage,renderer,control});
  }catch(e){
    canvas.remove();fallback.hidden=false;
    stage.dataset.fallback="true";
    console.info("DISPATER conceptual 3D fallback enabled",String(e?.message||e));
  }
}
if("IntersectionObserver" in window){
  const loader=new IntersectionObserver(entries=>{
    for(const item of entries){
      if(item.isIntersecting){loader.unobserve(item.target);init(item.target);}
    }
  },{rootMargin:"240px"});
  targetList.forEach(stage=>loader.observe(stage));
}else targetList.forEach(init);
