import React, {useState, useRef} from 'react';
export function StagingPanel(){
 const [status,setStatus]=useState('NOT RUN');const [receipt,setReceipt]=useState(null);
 const key=useRef(null);
 async function run(){
  setStatus('RUNNING');setReceipt(null);key.current ||= crypto.randomUUID();
  try{
   const r=await fetch('/api/staging-audit',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','Idempotency-Key':key.current},body:JSON.stringify({fixture:'heavy_recovery_v1'}),signal:AbortSignal.timeout(10000)});
   if(!r.ok){setStatus(r.status===401||r.status===403?'OWNER SIGN-IN REQUIRED':'STAGING UNAVAILABLE · NOT VERIFIED');return}
   const x=await r.json();
   if(x.auditRuntime!=='SYNTHETIC_EXECUTION_OBSERVED'||x.authority!=='NONE'||x.release!=='HOLD'||x.receipt?.observation?.candidate_amount_cents!==385000||x.receipt?.review!=='NOT_REVIEWED')throw Error('invalid');
   setReceipt(x.receipt);setStatus('STAGING SYNTHETIC EXECUTION OBSERVED');
  }catch{setStatus('STAGING UNAVAILABLE · NOT VERIFIED')}
 }
 return <section className="shad-card" aria-label="Connected staging audit">
  <h4>AUREX staging · fictional towing audit</h4>
  <p>Separate from the local demonstration. Requires an authenticated owner session. No billing or review approval is performed.</p>
  <button type="button" className="shad-button primary" disabled={status==='RUNNING'} onClick={run}>RUN STAGING TOWING AUDIT</button>
  <p role="status">{status}</p>
  {receipt&&<><p>Candidate exception: $3,850.00 · confirmed revenue: $0.00 · human review required.</p><p>Job: {receipt.job_id}</p><p>Evidence: {receipt.evidence_id}</p><p style={{overflowWrap:'anywhere'}}>SHA-256: {receipt.sha256}</p><details><summary>Source evidence, calculations and limitations</summary><pre style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere'}}>{JSON.stringify(receipt,null,2)}</pre></details></>}
  <p>Independent financial verification: NOT VERIFIED. Production release: HOLD.</p>
 </section>;
}
