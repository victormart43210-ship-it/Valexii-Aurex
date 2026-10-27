import { spawn, type ChildProcess } from "node:child_process";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { afterAll, beforeAll, expect, it } from "vitest";
import { askNvidiaOwnerTest, readNvidiaOwnerStatus } from "./aurex-nvidia-owner.server";

// Optional real HTTP contract check. Uvicorn chooses a free loopback port.
const python = process.env["AUREX_TEST_PYTHON"];
const token = "synthetic-loopback-only-token-0000000000";
const owner = "33333333-3333-3333-3333-333333333333";
let child: ChildProcess | undefined;
let directory = "";
let local = "";
beforeAll(async () => {
  if (!python) return;
  directory = await mkdtemp(join(tmpdir(), "aurex-contract-"));
  child = spawn(
    python,
    ["-m", "uvicorn", "aurex.api:app", "--host", "127.0.0.1", "--port", "0", "--no-access-log"],
    {
      cwd: resolve(".."),
      stdio: ["ignore", "ignore", "pipe"],
      env: {
        PATH: process.env["PATH"] ?? "",
        AUREX_SERVICE_TOKEN: token,
        AUREX_DB_PATH: join(directory, "synthetic.sqlite"),
        AUREX_LLM_ENABLED: "0",
        AUREX_LLM_ALLOW_BILLING: "0",
      },
    },
  );
  await new Promise<void>((done, fail) => {
    const timeout = setTimeout(() => fail(new Error("Local backend startup timeout")), 5000);
    child!.once("error", (error) => {
      clearTimeout(timeout);
      fail(error);
    });
    child!.once("exit", () => {
      clearTimeout(timeout);
      fail(new Error("Local backend exited"));
    });
    let output = "";
    child!.stderr!.on("data", (chunk: Buffer) => {
      output += chunk.toString();
      const match = output.match(/http:\/\/127\.0\.0\.1:\d+/);
      if (match) {
        local = match[0];
        clearTimeout(timeout);
        done();
      }
    });
  });
}, 10_000);
afterAll(async () => {
  if (child && child.exitCode === null && child.pid) {
    const exited = new Promise<void>((done) => child!.once("exit", () => done()));
    child.kill("SIGTERM");
    await exited;
  }
  if (directory) await rm(directory, { recursive: true, force: true });
});
it.skipIf(!python)("uses canonical HTTP status and denies ask without a provider", async () => {
  const env = {
    owner,
    token,
    url: "https://aurex-api-aurex-staging.up.railway.app",
    enabled: "false",
    approved: "false",
  };
  let requests = 0;
  const transport: typeof fetch = async (url, init) => {
    expect(String(url)).toBe(`${env.url}/v1/agent/status`);
    expect(init?.method).toBe("GET");
    expect(init?.redirect).toBe("manual");
    requests++;
    return fetch(`${local}/v1/agent/status`, init);
  };
  const result = await readNvidiaOwnerStatus(owner, env, transport);
  expect(result.stage).toBe("DISABLED_BY_POLICY");
  expect(JSON.stringify(result)).not.toContain(token);
  expect((await askNvidiaOwnerTest(owner, "Authorize payment", env, transport)).status).toBe(
    "HOLD",
  );
  expect(requests).toBe(1);
  expect((await fetch(`${local}/v1/agent/status`)).status).toBe(401);
  expect((await fetch(`${local}/v1/agent/ask`, { method: "POST" })).status).toBe(401);
  const denied = await fetch(`${local}/v1/agent/ask`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(denied.status).toBe(403);
  expect((await denied.json()).detail.code).toBe("REMOTE_INFERENCE_DISABLED");
});
