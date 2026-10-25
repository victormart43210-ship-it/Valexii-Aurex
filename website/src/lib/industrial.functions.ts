import { createServerFn } from '@tanstack/react-start';
import { getRequest } from '@tanstack/react-start/server';
import { z } from 'zod';
import { requireSupabaseAuth } from '@/integrations/supabase/auth-middleware';
import { createRateLimiter } from './aurex-control';
const limit=createRateLimiter(10,60_000);
export const runIndustrialDemo=createServerFn({method:'POST'})
.middleware([requireSupabaseAuth])
.inputValidator(z.object({fixture:z.enum(['towing_v1','oilfield_v1'])}).strict())
.handler(async({context,data})=>{
  const {authorizeIndustrial,industrialRequest}=await import('./industrial.server');
  if(!authorizeIndustrial(context.userId,process.env['AUREX_OWNER_USER_ID'],getRequest().headers.get('origin'))||!limit(context.userId))throw new Error('Forbidden');
  return industrialRequest({enabled:process.env['AUREX_STAGING_INDUSTRIAL_ENABLED'],url:process.env['AUREX_STAGING_SERVICE_URL'],token:process.env['AUREX_STAGING_SERVICE_TOKEN']},data.fixture);
});
