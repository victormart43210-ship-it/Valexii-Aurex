import { useRef, useState } from 'react';
import { useServerFn } from '@tanstack/react-start';
import { runFinancialStaging } from '@/lib/aurex-financial.functions';
import type { FinancialResult } from '@/lib/aurex-financial.server';

/** Mount only in the existing owner Financial Audit tab, beside LOCAL MOCK. */
export function AurexFinancialStaging() {
  const invoke = useServerFn(runFinancialStaging);
  const attempted = useRef(false);
  const busy = useRef(false);
  const [pending, setPending] = useState(false);
  const [consent, setConsent] = useState(false);
  const [jobId, setJobId] = useState('');
  const [result, setResult] = useState<FinancialResult | null>(null);
  const [error, setError] = useState(false);
  async function run(submit: boolean) {
    if (busy.current || !consent || (submit && attempted.current)) return;
    if (!submit && !/^job-[0-9a-f]{24}$/.test(jobId)) return;
    busy.current = true;
    if (submit) attempted.current = true;
    setPending(true); setError(false);
    try {
      const response = await invoke({ data: { jobId: submit ? null : jobId } });
      setResult(response);
      if (response.jobId) setJobId(response.jobId);
      // Safe to unlock only when server explicitly confirms NO submission attempt.
      if (submit && !response.submissionAttempted) attempted.current = false;
    } catch { setError(true); }
    finally { busy.current = false; setPending(false); }
  }
  return <section aria-labelledby="financial-staging-title" className="space-y-3 rounded-xl border p-4">
    <h3 id="financial-staging-title">Fictional financial audit — staging</h3>
    <p>Separate from LOCAL MOCK. Execution is held until staging is admitted. No uploads or customer documents.</p>
    <label className="flex gap-2"><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} />I consent to the fixed fictional, zero-inference-cost demonstration.</label>
    <button type="button" disabled={!consent || pending || attempted.current} onClick={() => void run(true)}>Submit fictional staging audit</button>
    <label className="block">Saved job ID <input className="block w-full font-mono" value={jobId} maxLength={28} onChange={e => setJobId(e.target.value)} placeholder="job-…" /></label>
    <button type="button" disabled={!consent || pending || !/^job-[0-9a-f]{24}$/.test(jobId)} onClick={() => void run(false)}>Read persisted job and receipt</button>
    <p role="status" aria-live="polite">{pending ? 'Request in progress' : error ? 'HOLD — request unavailable; do not resubmit an uncertain submission.' : result?.state ?? 'NOT RUN — staging admission required'}</p>
    {result?.jobId && <p className="break-all">Save this recovery ID: {result.jobId}</p>}
    {result?.receipt && <dl className="space-y-1 break-all">
      <dt>Evidence ID</dt><dd>{result.receipt.evidenceId}</dd>
      <dt>SHA-256 (recomputed server-side)</dt><dd className="font-mono">{result.receipt.sha256}</dd>
      <dt>Fictional cases matched</dt><dd>{String(result.receipt.observation['exact_case_matches'])} / {String(result.receipt.observation['case_count'])}</dd>
      <dt>Finding labels in synthetic suite</dt><dd>{String(result.receipt.observation['finding_labels'])}</dd>
      <dt>False positive / false negative flags</dt><dd>{String(result.receipt.observation['false_positive_flags'])} / {String(result.receipt.observation['false_negative_flags'])}</dd>
      <dt>Evaluation outcome</dt><dd>{String(result.receipt.observation['result'])}</dd>
    </dl>}
    <p>Review guidance: check duplicate references, invoice-versus-ticket values, approved rates, hours and missing source evidence. These are fixture categories, not returned invoice-level findings. The backend currently reports aggregate synthetic evaluation counts.</p>
    <p>Human review required. Digest consistency does not prove source accuracy. Independent verification: NOT VERIFIED. Financial authority: NONE. Production release: HOLD. No confirmed recovered savings.</p>
  </section>;
}
