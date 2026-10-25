import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath } from 'node:url';
const token=process.env['AUREX_SANDBOX_TOKEN'];
const port=Number(process.env['AUREX_SANDBOX_API_PORT']);
const ui=Number(process.env['AUREX_SANDBOX_UI_PORT']);
if(!token||token.length<32||!Number.isInteger(port)||port<1024||port>65535||!Number.isInteger(ui)||ui<1024||ui>65535)throw new Error('Use the isolated sandbox launcher');
export default defineConfig({root:fileURLToPath(new URL('.',import.meta.url)),plugins:[react()],server:{host:'127.0.0.1',port:ui,strictPort:true,fs:{allow:[fileURLToPath(new URL('..',import.meta.url))]},proxy:{'/__industrial':{target:`http://127.0.0.1:${port}`,rewrite:()=>'/v1/industrial/audit/demo',headers:{Authorization:`Bearer ${token}`},configure(proxy){proxy.on('proxyReq',(proxyReq,req,res)=>{if(req.method!=='POST'||req.headers.origin!==`http://127.0.0.1:${ui}`){proxyReq.destroy();res.writeHead(403);res.end('Forbidden');}});}}}}});
