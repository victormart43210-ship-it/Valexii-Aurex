/** Server-only canonical financial adapter. No network until explicitly admitted. */
import { createHash, randomUUID, timingSafeEqual } from 'node:crypto';

const HOST = 'https://aurex-api-aurex-staging.up.railway.app';
const JOB = /^job-[0-9a-f]{24}$/;
const HEX = /^[0-9a-f]{64}$/;
const ORIGINS = new Set(['https://valexii.com', 'https://www.valexii.com',
  'https://id-preview--811ffc43-2c8b-4c88-ab4c-4de668d089cb.lovable.app']);
type ObjectValue = Record<string, unknown>;
export type FinancialReceipt = {
  jobId: string; evidenceId: string; sha256: string; state: 'succeeded';
  observation: ObjectValue; integrity: 'RECORDED'; verification: 'NOT VERIFIED'; authority: 'NONE'; release: 'HOLD';
};
export type FinancialResult = {
  state: 'NOT_CONFIGURED' | 'PENDING' | 'HOLD' | 'STAGING_EXECUTION';
  jobId: string | null; receipt: FinancialReceipt | null;
  submissionAttempted: boolean; verification: 'NOT VERIFIED'; authority: 'NONE'; release: 'HOLD';
};
type Config = { enabled?: string | undefined; url?: string | undefined; token?: string | undefined };
type Transport = (url: string, init: RequestInit) => Promise<Response>;

export function authorizeFinancial(user: string, owner: string | undefined, origin: string | null): boolean {
  return !!owner && /^[0-9a-f-]{36}$/i.test(owner) && user === owner && !!origin && ORIGINS.has(origin);
}
function object(value: unknown): ObjectValue {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Invalid contract');
  return value as ObjectValue;
}
function exact(value: ObjectValue, keys: string[]) {
  if (Object.keys(value).sort().join(',') !== keys.sort().join(',')) throw new Error('Invalid fields');
}
function requireValue(condition: unknown): asserts condition {
  if (!condition) throw new Error('Invalid contract');
}

export function validateReceipt(raw: unknown, jobId: string): FinancialReceipt {
  const r = object(raw);
  exact(r, ['jobId', 'state', 'evidenceId', 'sha256', 'observation', 'integrity', 'verification', 'authority', 'release']);
  requireValue(JOB.test(jobId) && r['jobId'] === jobId && r['state'] === 'succeeded');
  requireValue(typeof r['evidenceId'] === 'string' && /^ev-[0-9a-f]{24}$/.test(r['evidenceId']));
  requireValue(typeof r['sha256'] === 'string' && HEX.test(r['sha256']));
  requireValue(r['integrity'] === 'RECORDED' && r['verification'] === 'NOT VERIFIED' && r['authority'] === 'NONE' && r['release'] === 'HOLD');
  const o = object(r['observation']);
  const counts = ['case_count', 'exact_case_matches', 'finding_labels', 'false_positive_flags', 'false_negative_flags'];
  exact(o, ['probe', 'synthetic', 'suite_sha256', ...counts, 'result', 'independent_verification', 'real_document_accuracy', 'authority', 'effect', 'production_release']);
  requireValue(o['probe'] === 'synthetic_field_audit_v1' && o['synthetic'] === true);
  requireValue(typeof o['suite_sha256'] === 'string' && HEX.test(o['suite_sha256']));
  for (const key of counts) requireValue(typeof o[key] === 'number' && Number.isInteger(o[key]) && (o[key] as number) >= 0 && (o[key] as number) <= 100);
  requireValue(o['case_count'] === 100 && ['PASS', 'HOLD', 'FAIL', 'SYNTHETIC_GATE_PASS_NOT_BETA_RELEASE'].includes(String(o['result'])));
  requireValue(o['independent_verification'] === 'NOT_VERIFIED' && o['real_document_accuracy'] === 'NOT_MEASURED' && o['authority'] === 'HOLD' && o['effect'] === 'NONE' && o['production_release'] === 'HOLD');
  // All admitted strings are ASCII enum literals/hex; integers are bounded.
  // Exactly Python json.dumps(sort_keys=True), including separator spaces.
  const canonical = '{' + Object.keys(o).sort().map(k => JSON.stringify(k) + ': ' + JSON.stringify(o[k])).join(', ') + '}';
  const digest = createHash('sha256').update(canonical, 'utf8').digest('hex');
  requireValue(timingSafeEqual(Buffer.from(digest), Buffer.from(r['sha256'])));
  return r as FinancialReceipt;
}

async function boundedJson(response: Response): Promise<unknown> {
  if (!response.ok || response.redirected || !response.headers.get('content-type')?.includes('application/json')) {
    await response.body?.cancel(); throw new Error('Transport refused');
  }
  const reader = response.body?.getReader();
  if (!reader) throw new Error('Empty body');
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.length;
      if (size > 24_000) throw new Error('Body too large');
      chunks.push(value);
    }
    return JSON.parse(Buffer.concat(chunks).toString('utf8'));
  } finally { await reader.cancel(); reader.releaseLock(); }
}
function validateJob(raw: unknown, expected: string | null): ObjectValue {
  const j = object(raw);
  exact(j, ['id', 'kind', 'state', 'createdAt', 'updatedAt', 'reservationUsd']);
  requireValue(typeof j['id'] === 'string' && JOB.test(j['id']) && (!expected || j['id'] === expected));
  requireValue(j['kind'] === 'regression_scan' && j['reservationUsd'] === 0);
  requireValue(['queued', 'running', 'succeeded', 'failed', 'cancelled'].includes(String(j['state'])));
  requireValue(typeof j['createdAt'] === 'string' && Number.isFinite(Date.parse(j['createdAt'])) && typeof j['updatedAt'] === 'string' && Number.isFinite(Date.parse(j['updatedAt'])));
  return j;
}

/** Caller MUST authenticate/authorize owner+origin. Null means one fixed submit;
 * jobId means read-only recovery. Network exceptions never retry a POST. */
export async function financialRequest(cfg: Config, jobId: string | null, net: Transport = fetch): Promise<FinancialResult> {
  const out: FinancialResult = { state: 'NOT_CONFIGURED', jobId: null, receipt: null, submissionAttempted: false, verification: 'NOT VERIFIED', authority: 'NONE', release: 'HOLD' };
  if (cfg.enabled !== 'true' || cfg.url !== HOST || !cfg.token || cfg.token.length < 32 || /\s/.test(cfg.token)) return out;
  out.state = 'HOLD';
  if (jobId !== null && !JOB.test(jobId)) return out;
  out.jobId = jobId;
  const signal = AbortSignal.timeout(30_000);
  const call = (path: string, init: RequestInit = {}) => net(HOST + path, { ...init, redirect: 'error', cache: 'no-store', signal,
    headers: { Authorization: 'Bearer ' + cfg.token, 'Content-Type': 'application/json', ...(init.headers ?? {}) } });
  try {
    if (jobId === null) {
      out.submissionAttempted = true;
      const raw = await boundedJson(await call('/v1/jobs', { method: 'POST', headers: { 'Idempotency-Key': randomUUID() },
        body: JSON.stringify({ kind: 'regression_scan', params: { probe: 'synthetic_field_audit_v1' }, maxCostUsd: 0 }) }));
      const created = validateJob(raw, null);
      out.jobId = created['id'] as string;
      out.state = ['failed', 'cancelled'].includes(String(created['state'])) ? 'HOLD' : 'PENDING';
      return out;
    }
    const job = validateJob(await boundedJson(await call('/v1/jobs/' + jobId, { method: 'GET' })), jobId);
    if (job['state'] === 'failed' || job['state'] === 'cancelled') return out;
    out.state = 'PENDING';
    if (job['state'] !== 'succeeded') return out;
    const response = await call('/v1/jobs/' + jobId + '/receipt', { method: 'GET' });
    if (response.status === 409) { await response.body?.cancel(); return out; }
    const receipt = validateReceipt(await boundedJson(response), jobId);
    out.receipt = receipt;
    out.state = ['PASS', 'SYNTHETIC_GATE_PASS_NOT_BETA_RELEASE'].includes(String(receipt.observation['result'])) ? 'STAGING_EXECUTION' : 'HOLD';
    return out;
  } catch { out.state = 'HOLD'; out.receipt = null; return out; }
}
