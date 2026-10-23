import { mkdir, copyFile, rm } from "node:fs/promises";
const output = new URL("./dist/", import.meta.url);
await rm(output, { recursive: true, force: true });
await mkdir(output, { recursive: true });
for (const file of ["index.html", "styles.css", "app.mjs", "audit.mjs", "frac-tree.svg"]) {
  await copyFile(new URL(file, import.meta.url), new URL("dist/" + file, import.meta.url));
}
console.log("Built DISPATER fictional-data static preview.");
