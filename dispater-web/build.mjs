import { mkdir, copyFile, rm, readFile, writeFile } from "node:fs/promises";
const output = new URL("./dist/", import.meta.url);
await rm(output, { recursive: true, force: true });
await mkdir(output, { recursive: true });
for (const file of ["index.html", "styles.css", "app.mjs", "audit.mjs", "frac-tree.svg", "command.css", "reference.css", "oilfield-scene.svg", "tow-recovery.svg", "audit-intelligence.svg"]) {
  await copyFile(new URL(file, import.meta.url), new URL("dist/" + file, import.meta.url));
}
console.log("Built DISPATER fictional-data static preview.");

// Exact saved screenshot preview; stitched from source-controlled base64 fragments.
// No remote Canva URLs or expiring signed assets at build time.
const parts = ["hero-00.b64", "hero-01.b64", "hero-02.b64"];
const encoded = (await Promise.all(parts.map(async name => (await readFile(new URL("./assets/" + name, import.meta.url), "utf8")).trim()))).join("");
const approved = Buffer.from(encoded, "base64");
if (approved.length !== 50950 || approved.subarray(0,8).toString("hex") !== "89504e470d0a1a0a") throw Error("DISPATER approved hero asset is incomplete or corrupt");
await writeFile(new URL("./dist/approved-hero.png", import.meta.url), approved);

const factoryParts = ["factory-00.b64", "factory-01.b64", "factory-02.b64", "factory-03.b64"];
const factoryEncoded = (await Promise.all(factoryParts.map(async name => (await readFile(new URL("./assets/" + name, import.meta.url), "utf8")).trim()))).join("");
const factoryImage = Buffer.from(factoryEncoded, "base64");
if(factoryImage.length !== 69446 || factoryImage.subarray(0,8).toString("hex") !== "89504e470d0a1a0a") throw Error("DISPATER industrial companion is corrupt");
await writeFile(new URL("./dist/industrial-companion.png", import.meta.url), factoryImage);
