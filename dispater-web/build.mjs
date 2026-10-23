import { mkdir, copyFile, rm } from "node:fs/promises";
import { build as bundle } from "esbuild";
const output=new URL("./dist/",import.meta.url);
await rm(output,{recursive:true,force:true});
await mkdir(output,{recursive:true});
for(const file of ["index.html","styles.css","launch.css","site.js","audit.mjs","frac-tree.svg","tow-recovery.svg"]){
 await copyFile(new URL("./"+file,import.meta.url),new URL("./dist/"+file,import.meta.url));
}
const common={bundle:true,platform:"browser",format:"esm",target:["es2022"],minify:true,sourcemap:false,legalComments:"linked",logLevel:"warning"};
await Promise.all([
 bundle({...common,entryPoints:[new URL("./dual-equipment.mjs",import.meta.url).pathname],outfile:new URL("./dist/dual-equipment.js",import.meta.url).pathname}),
 bundle({...common,entryPoints:[new URL("./audit-dashboard.jsx",import.meta.url).pathname],outfile:new URL("./dist/audit-dashboard.js",import.meta.url).pathname,jsx:"transform"})
]);
console.log("DISPATER marketing + two independently interactive 3D models + shadcn-pattern Radix audit dashboard built.");
