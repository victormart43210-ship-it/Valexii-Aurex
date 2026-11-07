// Server-only, default-off, fixed-destination synthetic execution adapter.
import { createHash } from 'node:crypto';
import { isDeepStrictEqual } from 'node:util';
const BASE='https://aurex-api-aurex-staging.up.railway.app/v1/industrial/audit/towing';
const fail=(res,code,reason)=>res.status(code).json({auditRuntime:'NOT_VERIFIED',authority:'NONE',release:'HOLD',reason});
async function bounded(response){
 if(!response.ok||!response.body)throw Error('unavailable');
 const reader=response.body.getReader();const chunks=[];let size=0;
 try{for(;;){const {done,value}=await reader.read();if(done)break;size+=value.length;if(size>32768)throw Error('oversize');chunks.push(value)}}finally{await reader.cancel()}
 return JSON.parse(Buffer.concat(chunks).toString('utf8'));
}
export function validateReceipt(x){
 if(!x||x.state!=='succeeded'||x.authority!=='NONE'||x.release!=='HOLD'||x.review!=='NOT_REVIEWED'||x.verification!=='NOT_VERIFIED'||x.integrity!=='CONSISTENT'||!/^cliv_[a-f0-9]{32}$/.test(x.job_id)||x.evidence_id!=='evidence_'+x.job_id)throw Error('invalid receipt');
 const o=x.observation;
 if(!o||o.schema!=='aurex.synthetic.towing.v1'||o.fixture!=='heavy_recovery_v1'||o.synthetic!==true||o.candidate_amount_cents!==385000||o.confirmed_revenue_cents!==0||o.authority!=='NONE'||o.release!=='HOLD'||o.review!=='NOT_REVIEWED')throw Error('invalid observation');
 // Canonical UTF-8 bytes are supplied for independent digest recomputation.
 if(typeof x.observation_canonical!=='string'||!isDeepStrictEqual(JSON.parse(x.observation_canonical),o)||createHash('sha256').update(x.observation_canonical,'utf8').digest('hex')!==x.sha256)throw Error('digest mismatch');
 return x;
}
export default async function handler(req,res){
 res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');
 if(req.method!=='POST')return fail(res,405,'METHOD_NOT_ALLOWED');
 if(req.headers?.origin!=='https://dispater.valexii.com')return fail(res,403,'ORIGIN_REJECTED');
 const input=req.body;
 if(!input||Array.isArray(input)||Object.keys(input).length!==1||input.fixture!=='heavy_recovery_v1')return fail(res,422,'FIXED_SYNTHETIC_SELECTOR_REQUIRED');
 const {AUREX_STAGING_SERVICE_TOKEN:token,DISPATER_OWNER_ID:owner,SUPABASE_URL:authUrl,SUPABASE_ANON_KEY:anon}=process.env;
 if(process.env.DISPATER_STAGING_ENABLED!=='1'||!token||token.length<32||!owner||!/^https:\/\/[a-z0-9-]+\.supabase\.co$/.test(authUrl||'')||!anon)return fail(res,503,'STAGING_NOT_CONFIGURED');
 const session=(req.headers.cookie||'').split(';').map(x=>x.trim()).find(x=>x.startsWith('dispater_owner_session='))?.slice(23);
 if(!session||session.length>8192||!/^[A-Za-z0-9_.-]+$/.test(session))return fail(res,401,'OWNER_SESSION_REQUIRED');
 const key=req.headers['idempotency-key'];
 if(typeof key!=='string'||!/^[A-Za-z0-9_-]{8,80}$/.test(key))return fail(res,422,'IDEMPOTENCY_KEY_REQUIRED');
 const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),8000);
 try{
  const user=await bounded(await fetch(authUrl+'/auth/v1/user',{headers:{Authorization:'Bearer '+session,apikey:anon},signal:controller.signal,redirect:'error',cache:'no-store'}));
  if(user.id!==owner)return fail(res,403,'OWNER_REQUIRED');
  const headers={Authorization:'Bearer '+token,'Content-Type':'application/json','Idempotency-Key':createHash('sha256').update(owner+':'+key).digest('hex')};
  const options={headers,signal:controller.signal,redirect:'error',cache:'no-store'};
  const created=validateReceipt(await bounded(await fetch(BASE,{...options,method:'POST',body:JSON.stringify(input)})));
  const persisted=validateReceipt(await bounded(await fetch(BASE+'/'+created.job_id+'/receipt',options)));
  if(persisted.job_id!==created.job_id||persisted.sha256!==created.sha256)throw Error('retrieval mismatch');
  return res.status(200).json({auditRuntime:'SYNTHETIC_EXECUTION_OBSERVED',receipt:persisted,independentFinancialVerification:'NOT_VERIFIED',authority:'NONE',release:'HOLD'});
 }catch{return fail(res,502,'AUTHENTICATION_OR_BACKEND_UNAVAILABLE')}finally{clearTimeout(timeout)}
}
