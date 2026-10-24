import { createServerFn } from '@tanstack/react-start';
import { getRequest } from '@tanstack/react-start/server';
import { requireSupabaseAuth } from '@/integrations/supabase/auth-middleware';
import { createRateLimiter } from './aurex-control';

const limit = createRateLimiter(20, 60_000);

/** Separate RPC avoids changing the legacy SQLite lab contract. Single-owner only. */
export const runFinancialStaging = createServerFn({ method: 'POST' })
  .middleware([requireSupabaseAuth])
  .inputValidator((input: unknown): { jobId: string | null } => {
    if (!input || typeof input !== 'object' || Array.isArray(input)
      || Object.keys(input).join(',') !== 'jobId') throw new Error('Invalid request');
    const jobId = (input as { jobId: unknown }).jobId;
    if (jobId !== null && (typeof jobId !== 'string' || !/^job-[0-9a-f]{24}$/.test(jobId))) throw new Error('Invalid request');
    return { jobId };
  })
  .handler(async ({ context, data }) => {
    const { authorizeFinancial, financialRequest } = await import('./aurex-financial.server');
    if (!authorizeFinancial(context.userId, process.env['AUREX_OWNER_USER_ID'], getRequest().headers.get('origin'))) throw new Error('Forbidden');
    if (!limit(context.userId)) throw new Error('Too many requests');
    return financialRequest({
      enabled: process.env['AUREX_STAGING_FINANCIAL_ENABLED'],
      url: process.env['AUREX_STAGING_SERVICE_URL'],
      token: process.env['AUREX_STAGING_SERVICE_TOKEN'],
    }, data.jobId);
  });
