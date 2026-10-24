import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { validateReceipt, financialRequest, authorizeFinancial } from '../src/lib/aurex-financial.server.ts';

const receipt = JSON.parse(readFileSync(new URL('./cxxxii-receipt.json', import.meta.url), 'utf8'));
const config = { enabled: 'true', url: 'https://aurex-api-aurex-staging.up.railway.app', token: 't'.repeat(40) };
const job = { id: receipt.jobId, kind: 'regression_scan', state: 'succeeded', createdAt: '2026-10-23T00:00:00Z', updatedAt: '2026-10-23T00:00:00Z', reservationUsd: 0 };
test('Python worker receipt matches TypeScript digest exactly', () => {
  assert.deepEqual(validateReceipt(receipt, receipt.jobId), receipt);
});
test('receipt corruption, authority promotion, unexpected fields and legacy IDs fail closed', () => {
  for (const patch of [{ sha256: '0'.repeat(64) }, { authority: 'APPROVED' }, { extra: true }, { jobId: 'f'.repeat(32) }, { state: 'cancelled' }, { observation: { ...receipt.observation, exact_case_matches: 1 } }]) {
    assert.throws(() => validateReceipt({ ...receipt, ...patch }, receipt.jobId));
  }
});
test('owner and origin are both required', () => {
  const owner = '12345678-1234-1234-1234-123456789abc';
  assert.equal(authorizeFinancial(owner, owner, 'https://valexii.com'), true);
  for (const origin of [null, 'null', 'http://valexii.com', 'https://valexii.com.evil.example']) assert.equal(authorizeFinancial(owner, owner, origin), false);
  assert.equal(authorizeFinancial('other', owner, 'https://valexii.com'), false);
  assert.equal(authorizeFinancial(owner, undefined, 'https://valexii.com'), false);
  assert.equal(authorizeFinancial('-'.repeat(36), '-'.repeat(36), 'https://valexii.com'), false);
});
test('recomputed digest cannot bless malformed observation types or extra fields', () => {
  for (const patch of [{ result: ['PASS'] }, { exact_case_matches: 1.5 }, { extra: true }, { probe: 'sqlite_roundtrip_v1' }]) {
    const observation = { ...receipt.observation, ...patch };
    const canonical = '{' + Object.keys(observation).sort().map(k => JSON.stringify(k) + ': ' + JSON.stringify(observation[k])).join(', ') + '}';
    const sha256 = createHash('sha256').update(canonical).digest('hex');
    assert.throws(() => validateReceipt({ ...receipt, observation, sha256 }, receipt.jobId));
  }
});
test('disabled, missing credential and wrong destination make zero calls', async () => {
  let calls = 0;
  const net = async () => { calls++; throw new Error('must not call'); };
  for (const patch of [{ enabled: undefined }, { token: undefined }, { url: 'https://evil.example' }]) {
    assert.equal((await financialRequest({ ...config, ...patch }, null, net)).state, 'NOT_CONFIGURED');
  }
  assert.equal(calls, 0);
});
test('submit is fixed, bounded and never retried; refresh retrieves persisted receipt', async () => {
  const calls: { url: string; init: RequestInit }[] = [];
  const net = async (url: string, init: RequestInit) => {
    calls.push({ url, init });
    return Response.json(url.endsWith('/receipt') ? receipt : job);
  };
  const submitted = await financialRequest(config, null, net);
  assert.equal(submitted.state, 'PENDING');
  assert.equal(calls.length, 1);
  assert.equal(calls[0]?.init.redirect, 'error');
  assert.deepEqual(JSON.parse(calls[0]?.init.body as string), { kind: 'regression_scan', params: { probe: 'synthetic_field_audit_v1' }, maxCostUsd: 0 });
  const result = await financialRequest(config, receipt.jobId, net);
  assert.equal(result.state, 'STAGING_EXECUTION');
  assert.equal(result.receipt?.sha256, receipt.sha256);
  assert.equal(calls.filter(c => c.init.method === 'POST').length, 1);
});
test('queued, failed, cancelled, invalid IDs, oversized responses and errors cannot succeed', async () => {
  for (const state of ['queued', 'running', 'failed', 'cancelled']) {
    const result = await financialRequest(config, receipt.jobId, async () => Response.json({ ...job, state }));
    assert.equal(result.state, ['queued', 'running'].includes(state) ? 'PENDING' : 'HOLD');
    assert.equal(result.receipt, null);
  }
  let calls = 0;
  assert.equal((await financialRequest(config, '../bad', async () => { calls++; return Response.json(job); })).state, 'HOLD');
  assert.equal(calls, 0);
  for (const net of [async () => new Response('x'.repeat(25000)), async () => new Response(null, { status: 302 }), async () => { throw new Error('secret'); }]) {
    const result = await financialRequest(config, receipt.jobId, net);
    assert.equal(result.state, 'HOLD');
    assert.equal(JSON.stringify(result).includes('secret'), false);
  }
});
test('409 stays pending and streaming size cap cancels the response', async () => {
  const pending = await financialRequest(config, receipt.jobId, async url => url.endsWith('/receipt') ? new Response(null, { status: 409 }) : Response.json(job));
  assert.equal(pending.state, 'PENDING');
  let cancelled = false;
  const body = new ReadableStream({ pull(controller) { controller.enqueue(new Uint8Array(25001)); }, cancel() { cancelled = true; } });
  const result = await financialRequest(config, receipt.jobId, async () => new Response(body, { headers: { 'Content-Type': 'application/json' } }));
  assert.equal(result.state, 'HOLD');
  assert.equal(cancelled, true);
});
