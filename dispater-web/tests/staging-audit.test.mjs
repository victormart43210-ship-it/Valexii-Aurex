import test from 'node:test';
import assert from 'node:assert/strict';
import handler from '../api/staging-audit.js';
const response=()=>({code:200,body:null,setHeader(){},status(n){this.code=n;return this},json(x){this.body=x;return this}});
test('unconfigured staging adapter fails closed without sending requests',async()=>{
 const res=response();await handler({method:'POST',headers:{origin:'https://dispater.valexii.com'},body:{fixture:'heavy_recovery_v1'}},res);
 assert.equal(res.code,503);assert.equal(res.body.auditRuntime,'NOT_VERIFIED');
});
test('wrong origin rejected before authentication',async()=>{
 const res=response();await handler({method:'POST',headers:{origin:'https://attacker.invalid'},body:{}},res);
 assert.equal(res.code,403);
});
test('customer data rejected',async()=>{
 const res=response();await handler({method:'POST',headers:{origin:'https://dispater.valexii.com'},body:{records:[]}},res);
 assert.equal(res.code,422);
});

import {readFileSync} from 'node:fs';
import {validateReceipt} from '../api/staging-audit.js';
const receipt=JSON.parse(readFileSync(new URL('./fixtures/towing-receipt.json',import.meta.url)));
test('real canonical receipt digest validates; tampering rejects',()=>{
 assert.equal(validateReceipt(receipt).observation.candidate_amount_cents,385000);
 for(const change of [{sha256:'0'.repeat(64)},{authority:'APPROVED'},{observation:{...receipt.observation,candidate_amount_cents:1}}]){
  assert.throws(()=>validateReceipt({...receipt,...change}));
 }
});
test('authenticated proxy retrieves stored receipt separately and leaks no bearer',async()=>{
 const saved={...process.env};const old=globalThis.fetch;const calls=[];
 Object.assign(process.env,{DISPATER_STAGING_ENABLED:'1',AUREX_STAGING_SERVICE_TOKEN:'s'.repeat(40),DISPATER_OWNER_ID:'owner-1',SUPABASE_URL:'https://synthetic.supabase.co',SUPABASE_ANON_KEY:'public-test-key'});
 globalThis.fetch=async(url,options)=>{calls.push([url,options]);return new Response(JSON.stringify(url.endsWith('/auth/v1/user')?{id:'owner-1'}:receipt))};
 try{
  const res=response();await handler({method:'POST',headers:{origin:'https://dispater.valexii.com',cookie:'dispater_owner_session=synthetic.jwt.token','idempotency-key':'retry-0001'},body:{fixture:'heavy_recovery_v1'}},res);
  assert.equal(res.code,200);assert.equal(calls.length,3);assert.equal(calls[1][1].headers.Authorization,'Bearer '+'s'.repeat(40));
  assert.ok(calls[2][0].endsWith('/receipt'));assert.ok(!JSON.stringify(res.body).includes('s'.repeat(40)));
 }finally{globalThis.fetch=old;for(const key of Object.keys(process.env))if(!(key in saved))delete process.env[key];Object.assign(process.env,saved)}
});
