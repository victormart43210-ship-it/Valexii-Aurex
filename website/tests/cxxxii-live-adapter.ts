// Offline integration harness: only loopback; never connects to Railway.
import assert from 'node:assert/strict';
import { financialRequest } from '../src/lib/aurex-financial.server.ts';
const local = process.argv[2];
assert.ok(local && /^http:\/\/127\.0\.0\.1:[0-9]+$/.test(local));
const cfg = { enabled: 'true', url: 'https://aurex-api-aurex-staging.up.railway.app', token: 'z'.repeat(40) };
const transport = (url: string, init: RequestInit) => {
  assert.ok(url.startsWith(cfg.url + '/v1/jobs'));
  return fetch(local + url.slice(cfg.url.length), init);
};
const created = await financialRequest(cfg, null, transport);
assert.equal(created.state, 'PENDING');
assert.ok(created.jobId);
let result = created;
for (let i = 0; i < 30 && result.state === 'PENDING'; i++) {
  await new Promise(resolve => setTimeout(resolve, 100));
  result = await financialRequest(cfg, created.jobId, transport);
}
assert.equal(result.state, 'STAGING_EXECUTION');
assert.equal(result.receipt?.observation['exact_case_matches'], 100);
console.log(JSON.stringify({ state: result.state, jobId: result.jobId, sha256: result.receipt?.sha256, verification: result.verification }));
