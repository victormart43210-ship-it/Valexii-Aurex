import test from "node:test";
import assert from "node:assert/strict";
import handler from "../api/railway-status.js";
function makeRes() {
  return { statusCode: 200, headers: {}, body: null,
    setHeader(key, value) { this.headers[key] = value; return this; },
    status(code) { this.statusCode = code; return this; },
    json(value) { this.body = value; return this; },
  };
}
test("Railway probe rejects methods other than GET", async () => {
  const res = makeRes();
  await handler({ method: "POST" }, res);
  assert.equal(res.statusCode, 405);
  assert.equal(res.body.state, "HOLD");
  assert.equal(res.body.error, "METHOD_NOT_ALLOWED");
});
test("Railway healthy endpoint is NOT audit execution authority", async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => ({ ok: true, status: 200 });
  try {
    const res = makeRes();
    await handler({ method: "GET" }, res);
    assert.equal(res.statusCode, 200);
    assert.equal(res.body.stagingReachability, "HEALTH_ENDPOINT_RESPONDED");
    assert.equal(res.body.auditRuntime, "NOT CONNECTED");
    assert.equal(res.body.modelInference, "NOT RUN");
    assert.equal(res.body.financialAuthority, "NONE");
    assert.equal(res.body.state, "HOLD");
  } finally { globalThis.fetch = originalFetch; }
});
test("Railway request failure fails closed", async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => { throw new Error("synthetic network failure"); };
  try {
    const res = makeRes();
    await handler({ method: "GET" }, res);
    assert.equal(res.body.stagingReachability, "NOT VERIFIED");
    assert.equal(res.body.financialAuthority, "NONE");
    assert.equal(res.body.state, "HOLD");
  } finally { globalThis.fetch = originalFetch; }
});

test("Railway v1 authorization cannot be bypassed or misreported as ready", async () => {
  const old = globalThis.fetch;
  globalThis.fetch = async (url, config) => {
    assert.ok(String(url).endsWith("/v1/health"));
    assert.equal(config.headers.Authorization, undefined);
    return { ok: false, status: 401 };
  };
  try {
    const res = makeRes();
    await handler({ method: "GET" }, res);
    assert.equal(res.statusCode, 200);
    assert.equal(res.body.reason, "BEARER_AUTHORIZATION_REQUIRED");
    assert.equal(res.body.stagingReachability, "NOT VERIFIED");
    assert.equal(res.body.auditRuntime, "NOT CONNECTED");
    assert.equal(res.body.financialAuthority, "NONE");
  } finally { globalThis.fetch = old; }
});
