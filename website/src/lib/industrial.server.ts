// Server-only: imported dynamically by authenticated server function, never the component.
import { validateIndustrial, type IndustrialFixture, type IndustrialResult } from './industrial-contract';
const STAGING='https://aurex-api-aurex-staging.up.railway.app';
export function authorizeIndustrial(user:string,owner:string|undefined,origin:string|null):boolean {
  return !!owner && user===owner && origin==='https://valexii.com';
}
export async function industrialRequest(config:{enabled?:string|undefined;url?:string|undefined;token?:string|undefined},fixture:IndustrialFixture,transport:typeof fetch=fetch):Promise<IndustrialResult> {
  const unavailable:IndustrialResult={state:'NOT_VERIFIED',report:null};
  if(config.enabled!=='1'||config.url!==STAGING||!config.token||config.token.length<32) return unavailable;
  try {
    const response=await transport(`${STAGING}/v1/industrial/audit/demo`,{method:'POST',headers:{Authorization:`Bearer ${config.token}`,'Content-Type':'application/json'},body:JSON.stringify({fixture}),redirect:'error',signal:AbortSignal.timeout(5000)});
    if(!response.ok||!response.body) {await response.body?.cancel();return unavailable;}
    const reader=response.body.getReader(); const chunks:Uint8Array[]=[];let length=0;
    try {while(true){const part=await reader.read();if(part.done)break;length+=part.value.byteLength;if(length>16384)throw new Error('Too large');chunks.push(part.value);}}
    finally {await reader.cancel();reader.releaseLock();}
    const bytes=new Uint8Array(length);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}
    return {state:'STAGING_SYNTHETIC',report:validateIndustrial(JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes)),fixture)};
  } catch {return unavailable;}
}
