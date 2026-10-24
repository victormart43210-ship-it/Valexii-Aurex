/**
 * DISPATER.AI original procedural 3D equipment concept geometry.
 * MIT Three.js dependency. No outside 3D model assets, no licensing uncertainty.
 * Illustrative meshes only: no live instrumentation, pressure, or physical simulation.
 */
import * as THREE from "three";
const mat = {
  frame: new THREE.MeshStandardMaterial({ color: 0x263b47, metalness: .94, roughness: .27 }),
  titanium: new THREE.MeshStandardMaterial({ color: 0x88a8b6, metalness: .88, roughness: .25 }),
  dark: new THREE.MeshStandardMaterial({ color: 0x101d27, metalness: .65, roughness: .38 }),
  black: new THREE.MeshStandardMaterial({ color: 0x030b13, metalness: .42, roughness: .66 }),
  red: new THREE.MeshStandardMaterial({ color: 0xce302b, metalness: .68, roughness: .27 }),
  redHighlight: new THREE.MeshStandardMaterial({ color: 0xff644c, metalness: .6, roughness: .29 }),
  rim: new THREE.MeshStandardMaterial({ color: 0xb8cad2, metalness: .93, roughness: .18 }),
  tire: new THREE.MeshStandardMaterial({ color: 0x090d14, roughness: .91 }),
  amber: new THREE.MeshStandardMaterial({ color: 0xefb858, metalness: .25, roughness: .29, emissive: 0xa85c12, emissiveIntensity: .36 }),
  cyan: new THREE.MeshStandardMaterial({ color: 0x04bfd4, metalness: .44, roughness: .33, emissive: 0x02596f, emissiveIntensity: .38 }),
  window: new THREE.MeshStandardMaterial({ color: 0x18475f, metalness: .52, roughness: .09, transparent: true, opacity: .86 }),
  paint: new THREE.MeshStandardMaterial({ color: 0x142737, metalness: .75, roughness: .27 }),
  paintHighlight: new THREE.MeshStandardMaterial({ color: 0x235579, metalness: .65, roughness: .3 }),
};
const v=(x,y,z)=>new THREE.Vector3(x,y,z);
function mesh(root,shape,material,x=0,y=0,z=0){const m=new THREE.Mesh(shape,material);m.position.set(x,y,z);root.add(m);m.castShadow=true;m.receiveShadow=true;return m;}
function box(root,w,h,d,m,x=0,y=0,z=0){return mesh(root,new THREE.BoxGeometry(w,h,d),m,x,y,z)}
function cyl(root,r1,r2,height,material,x=0,y=0,z=0,n=24){return mesh(root,new THREE.CylinderGeometry(r1,r2,height,n),material,x,y,z)}
function ball(root,r,material,x=0,y=0,z=0){return mesh(root,new THREE.SphereGeometry(r,16,12),material,x,y,z)}
function pipe(root,a,b,r,material){const mid=new THREE.Vector3().addVectors(a,b).multiplyScalar(.5),delta=new THREE.Vector3().subVectors(b,a);const m=cyl(root,r,r,delta.length(),material,mid.x,mid.y,mid.z);m.quaternion.setFromUnitVectors(v(0,1,0),delta.normalize());return m;}
function ring(root,r,t,material,x,y,z,plane="xy"){const ring=mesh(root,new THREE.TorusGeometry(r,t,10,40),material,x,y,z);if(plane==="xz")ring.rotation.x=Math.PI/2;if(plane==="yz")ring.rotation.y=Math.PI/2;return ring;}
function wheelValve(root,x,y,z,plane="xy",r=.49){
  ring(root,r,.055,mat.redHighlight,x,y,z,plane);
  ring(root,r*.7,.021,mat.red,x,y,z,plane);
  ball(root,.12,mat.rim,x,y,z);
  for(let i=0;i<6;i++){
    const a=i*Math.PI/3;
    const dir=plane==="xy"?v(Math.cos(a),Math.sin(a),0):plane==="xz"?v(Math.cos(a),0,Math.sin(a)):v(0,Math.cos(a),Math.sin(a));
    pipe(root,v(x,y,z).add(dir.clone().multiplyScalar(.1)),v(x,y,z).add(dir.multiplyScalar(r-.035)),.029,mat.redHighlight);
  }
}
function boltCircle(root,y,r,count=12){
 for(let i=0;i<count;i++){let a=i*Math.PI*2/count;cyl(root,.053,.053,.095,mat.rim,Math.cos(a)*r,y,Math.sin(a)*r,8);}
}
function flange(root,y,width=.64){
 cyl(root,width,width,.22,mat.frame,0,y,0,32);
 cyl(root,width+.04,width+.04,.06,mat.rim,0,y+.12,0,32);
 boltCircle(root,y+.11,width-.09);
}
function gauge(root,x,y,z){
 pipe(root,v(x,y-.5,z),v(x,y-.12,z),.062,mat.frame);
 let face=cyl(root,.25,.25,.095,mat.dark,x,y,z);
 face.rotation.x=Math.PI/2;
 let disk=cyl(root,.207,.207,.013,mat.titanium,x,y,z+.06);
 disk.rotation.x=Math.PI/2;
 let needle=box(root,.025,.14,.025,mat.redHighlight,x+.05,y+.032,z+.092);
 needle.rotation.z=-.7;
 ring(root,.225,.027,mat.rim,x,y,z+.072,"xy");
}
function halo(root,r,y){const a=ring(root,r,.016,mat.cyan,0,y,0,"xz");a.rotation.z=.07;}
function createBase(root,r=2.1){
 cyl(root,r,r,.13,mat.dark,0,.04,0,64);
 ring(root,r-.1,.025,mat.cyan,0,.11,0,"xz");
 ring(root,r-.43,.014,mat.titanium,0,.12,0,"xz");
 for(let a=0;a<12;a++){let theta=a*2*Math.PI/12,mark=box(root,.11,.03,.19,a%3===0?mat.amber:mat.cyan,Math.cos(theta)*(r-.2),.13,Math.sin(theta)*(r-.2));mark.rotation.y=-theta;}
}
/** A fracking wellhead / frac tree, deliberately not a sensor-fed operational digital twin. */
export function createFracTree(){
 const root=new THREE.Group();root.name="Illustrative frac tree, no live pressure telemetry";
 createBase(root,2.65);
 // Vertical wellhead stack, five forged blocks and large red bonnet flanges.
 cyl(root,.38,.48,4.8,mat.frame,0,2.5,0,36);
 for(const y of [.38,.82,1.55,2.34,3.05,3.94,4.5]){
   flange(root,y,y===.38?.87:.61);
 }
 for(const y of [.65,1.12,2.11,3.48,4.27]){
  box(root,.89,.38,.9,mat.titanium,0,y,0);
  box(root,.73,.42,.73,mat.frame,0,y,0);
 }
 // Dual high-pressure lateral lines, aligned with primary axis.
 for(const dir of [-1,1]){
   const sx=dir*.57;
   pipe(root,v(sx,2.7,0),v(dir*1.9,2.7,0),.29,mat.titanium);
   pipe(root,v(dir*1.88,2.7,0),v(dir*2.2,2.7,0),.35,mat.frame);
   const neck=cyl(root,.37,.37,.13,mat.red,dir*1.7,2.7,0);
   neck.rotation.z=Math.PI/2;
   const nut=cyl(root,.45,.45,.15,mat.rim,dir*2,2.7,0);
   nut.rotation.z=Math.PI/2;
   pipe(root,v(dir*2.2,2.7,0),v(dir*2.38,2.42,0),.21,mat.titanium);
   pipe(root,v(dir*2.38,2.42,0),v(dir*2.38,.85,0),.17,mat.frame);
   // Lateral handwheels sit on the near side, not accidental flat front textures.
   pipe(root,v(dir*1.05,2.7,.02),v(dir*1.05,2.7,.67),.09,mat.rim);
   wheelValve(root,dir*1.05,2.7,.71,"xy",.47);
 }
 // Stacked crown valves; upper rotating handwheel.
 for(const y of [1.1,3.48,4.8]){
   pipe(root,v(0,y,.32),v(0,y,.82),.075,mat.titanium);
   wheelValve(root,0,y,.86,"xy",y===4.8?.36:.44);
 }
 // Crown and gauge pressure housings are physical instruments, not readings.
 flange(root,4.91,.46);
 cyl(root,.24,.24,.43,mat.rim,0,5.2,0);
 cyl(root,.19,.19,.25,mat.red,0,5.53,0);
 gauge(root,-.66,3.91,.62);
 gauge(root,.67,3.91,.62);
 // Subtle floor effect comes from geometry, not fake data.
 halo(root,2.52,.16);
 root.userData={model:"frac-tree",classification:"ILLUSTRATIVE_3D_MODEL",telemetry:false,source:"original procedural Three.js geometry"};
 return root;
}
function truckTire(root,x,y,z){
 const tire=cyl(root,.58,.58,.31,mat.tire,x,y,z,32);tire.rotation.x=Math.PI/2;
 const hub=cyl(root,.34,.34,.33,mat.rim,x,y,z,24);hub.rotation.x=Math.PI/2;
 const cap=cyl(root,.16,.16,.35,mat.frame,x,y,z,24);cap.rotation.x=Math.PI/2;
 for(let n=0;n<8;n++){const a=n*Math.PI/4;let marker=ball(root,.055,mat.dark,x+Math.cos(a)*.23,y+Math.sin(a)*.23,z+Math.sign(z)*.18);}
}
function windowPane(root,w,h,d,x,y,z){const m=box(root,w,h,d,mat.window,x,y,z);return m;}
/** Heavy-duty boom-type tow/recovery truck — original stylized 3D geometry. */
export function createTowTruck(){
 const root=new THREE.Group();root.name="Illustrative towing and recovery vehicle";
 createBase(root,4.8);
 // Coordinate convention front/hood = negative X, rear recovery boom = positive X.
 const car=new THREE.Group();car.position.y=.31;root.add(car);
 box(car,7.2,.35,1.92,mat.dark,0,1.08,0); // chassis
 box(car,7.9,.19,1.99,mat.rim,0,.78,0);
 for(const x of [-2.7,-.65,1.72,2.9])for(const z of [-1.07,1.07])truckTire(car,x,.59,z);
 // Front long hood, grille and headlamps.
 box(car,2.2,.91,1.95,mat.paint,-2.85,1.75,0);
 let hood=box(car,2.26,.22,1.99,mat.paintHighlight,-2.84,2.25,0);
 hood.rotation.z=-.045;
 box(car,.1,.64,1.45,mat.black,-3.98,1.73,0);
 for(let k=0;k<8;k++)box(car,.024,.53,.04,mat.rim,-4.05,1.75,-.62+k*.17);
 for(const z of [-.7,.7])box(car,.07,.21,.33,mat.amber,-4.0,1.88,z);
 box(car,.24,.18,2.15,mat.rim,-4.03,1.15,0); // bumper
 // Cab with roof, glass on windshield and side.
 box(car,1.76,1.76,1.95,mat.paint,-1.0,2.17,0);
 box(car,1.89,.18,2.09,mat.rim,-1.06,3.14,0);
 windowPane(car,.1,.72,1.66,-1.94,2.45,0);
 for(const z of [-1.03,1.03])windowPane(car,1.14,.67,.04,-.95,2.55,z);
 for(const z of [-1.1,1.1]){box(car,.15,.12,.36,mat.frame,-1.75,2.53,z);box(car,.48,.06,.12,mat.rim,-1.74,2.47,z);}
 // Side trim / door lines.
 for(const z of [-1.04,1.04]){
   box(car,.9,.055,.06,mat.rim,-.95,1.87,z);
   box(car,.12,.09,.05,mat.amber,-.3,2.08,z);
   box(car,4.3,.12,.06,mat.amber,1.13,1.28,z);
 }
 // Operator recovery body and storage compartments.
 box(car,3.7,.89,1.92,mat.paint,1.82,1.72,0);
 box(car,3.68,.16,2.0,mat.rim,1.82,2.2,0);
 for(const z of [-1.02,1.02]){
   for(const x of [.61,1.7,2.8]){
     box(car,.94,.48,.055,mat.frame,x,1.8,z);
     box(car,.6,.035,.07,mat.rim,x,2.01,z+Math.sign(z)*.025);
   }
 }
 // Tow crane column, boom with tip pulley and hook, lifted toward back.
 box(car,.9,1.45,.78,mat.frame,1.28,2.65,0);
 pipe(car,v(1.26,3.24,0),v(3.49,4.38,0),.24,mat.titanium);
 pipe(car,v(1.37,3.21,0),v(3.7,4.33,0),.1,mat.amber);
 pipe(car,v(3.57,4.43,0),v(3.9,4.56,0),.12,mat.frame);
 let pulley=cyl(car,.25,.25,.25,mat.rim,3.8,4.38,0);pulley.rotation.x=Math.PI/2;
 pipe(car,v(3.9,4.34,0),v(3.9,3.3,0),.028,mat.titanium);
 const hook=mesh(car,new THREE.TorusGeometry(.14,.04,8,16,Math.PI*1.6),mat.red,3.9,3.16,0);
 hook.rotation.y=.24;
 // Outrigger arms / boom anchor.
 for(const side of [-1,1]){
   pipe(car,v(1.43,2.59,side*.35),v(2.25,1.6,side*1.01),.09,mat.frame);
   box(car,.34,.3,.25,mat.red,2.29,1.41,side*1.0);
 }
 // Amber beacons (static, nothing signaling real dispatch state).
 for(const z of [-.68,.68]){
   box(car,.24,.12,.23,mat.black,-.99,3.3,z);
   cyl(car,.1,.1,.2,mat.amber,-.99,3.45,z,12);
 }
 // Tow recovery hitch and lift.
 pipe(car,v(3.4,1.4,0),v(4.45,.65,0),.16,mat.titanium);
 pipe(car,v(4.43,.65,-.76),v(4.43,.65,.76),.15,mat.frame);
 for(const z of [-.76,.76])box(car,.55,.16,.2,mat.red,4.45,.57,z);
 root.rotation.y=-.14;
 root.userData={model:"tow-truck",classification:"ILLUSTRATIVE_3D_MODEL",telemetry:false,source:"original procedural Three.js geometry"};
 return root;
}
export const MODEL_INFO=Object.freeze({
  "frac-tree":{title:"Frac tree / wellhead",summary:"Valve bodies, forged flanges, lateral outlets and handwheels. Illustration only; no pressure data.",camera:[8.4,6.4,9.6],maxDistance:22},
  "tow-truck":{title:"Heavy-duty tow truck",summary:"Recovery boom, tow lift, operator cab, wheels and storage body. Illustration only; no dispatch data.",camera:[10.5,7.5,11.3],maxDistance:27},
});
