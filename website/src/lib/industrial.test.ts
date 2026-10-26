import { describe, it, expect } from 'vitest';
import fixture from '../../tests/industrial-towing.json';
import { validateIndustrial } from './industrial-contract';
import { authorizeIndustrial, industrialRequest } from './industrial.server';

describe('industrial admission', () => {
  it('accepts only advisory fixed towing response', () => {
    expect(validateIndustrial(fixture, 'towing_v1').proof.status).toBe('NOT_VERIFIED');
    for (const altered of [{...fixture, authority:'CERTIFIED'}, {...fixture, changed:'COMPLIANT'}, {...fixture, proof:{status:'PASS'}}, {...fixture, extra:'data'}, {...fixture,now:[]}, {...fixture,now:fixture.now.map((row,i)=>i===0?{...row,record_ids:['demo-forged','demo-forged']}:row)}, {...fixture,now:fixture.now.map((row,i)=>i===4?{...row,record_ids:['demo-unexpected']}:row)}]) {
      expect(() => validateIndustrial(altered,'towing_v1')).toThrow();
    }
  });
  it('owner and origin required; cross-user rejected', () => {
    expect(authorizeIndustrial('owner','owner','https://valexii.com')).toBe(true);
    for (const args of [['other','owner','https://valexii.com'],['owner','','https://valexii.com'],['owner','owner',null],['owner','owner','https://evil.example']]) {
      expect(authorizeIndustrial(...args as [string,string,string|null])).toBe(false);
    }
  });
  it('disabled or unexpected destination never fetches', async () => {
    let calls=0; const never = async () => { calls++; throw new Error('must not fetch'); };
    expect((await industrialRequest({}, 'towing_v1', never)).state).toBe('NOT_VERIFIED');
    expect((await industrialRequest({enabled:'1',url:'https://evil.example',token:'x'.repeat(40)},'towing_v1',never)).state).toBe('NOT_VERIFIED');
    expect(calls).toBe(0);
  });
  it('bounded response, no redirect and no false success on failures', async () => {
    const config={enabled:'1',url:'https://aurex-api-aurex-staging.up.railway.app',token:'x'.repeat(40)};
    const ok = await industrialRequest(config,'towing_v1',async (_url, init) => {
      expect(init?.redirect).toBe('error'); expect(init?.body).toBe('{"fixture":"towing_v1"}');
      return new Response(JSON.stringify(fixture));
    });
    expect(ok.state).toBe('STAGING_SYNTHETIC');
    for (const response of [new Response('oops',{status:503}),new Response('x'.repeat(17000)),new Response('{"authority":"CERTIFIED"}')]) {
      expect((await industrialRequest(config,'towing_v1',async()=>response)).state).toBe('NOT_VERIFIED');
    }
  });
});
