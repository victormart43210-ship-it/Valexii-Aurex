import { z } from 'zod';

export type IndustrialFixture = 'towing_v1' | 'oilfield_v1';
const row = z.object({category:z.string().max(128),status:z.enum(['PRESENT_NOT_VERIFIED','EXPIRED','CONFLICTING','NOT_VERIFIED','MISSING']),record_ids:z.array(z.string().regex(/^demo-[a-z0-9-]{1,80}$/)).max(10)}).strict();
const schema=z.object({demo:z.literal(true),authority:z.literal('ADVISORY_ONLY_NO_CERTIFICATION'),operator:z.enum(['Permian Recovery Services (fictional)','Permian Field Operations (fictional)']),as_of:z.literal('2026-10-24'),now:z.array(row).length(5),changed:z.literal('NOT_VERIFIED_NO_PRIOR_SNAPSHOT'),next:z.array(z.object({category:z.string().max(128),action:z.literal('HUMAN_REVIEW_REQUIRED')}).strict()).length(4),why:z.literal('Synthetic inventory-only demonstration; regulatory applicability not evaluated'),proof:z.object({status:z.literal('NOT_VERIFIED'),reason:z.literal('No authenticated evidence-ledger receipt or independent verifier in demo')}).strict()}).strict();
export type IndustrialReport=z.infer<typeof schema>;
export type IndustrialResult={state:'NOT_VERIFIED';report:null}|{state:'STAGING_SYNTHETIC'|'LOCAL_SANDBOX';report:IndustrialReport};
export function validateIndustrial(value:unknown, fixture:IndustrialFixture):IndustrialReport {
  const parsed=schema.parse(value);
  const categories=fixture==='towing_v1'?['driver_qualification','vehicle_inspection','maintenance','service_ticket','incident_register']:['crew_qualification','equipment_inspection','maintenance','field_ticket','incident_register'];
  const recordIds=[['demo-driver-01'],['demo-vehicle-01'],['demo-maint-01','demo-maint-02'],['demo-ticket-01'],[]];
  const statuses=['PRESENT_NOT_VERIFIED','EXPIRED','CONFLICTING','NOT_VERIFIED','MISSING'];
  const company=fixture==='towing_v1'?'Permian Recovery Services (fictional)':'Permian Field Operations (fictional)';
  if(parsed.operator!==company || parsed.now.some((row,i)=>row.category!==categories[i]||row.status!==statuses[i]||JSON.stringify(row.record_ids)!==JSON.stringify(recordIds[i])) || parsed.next.some((row,i)=>row.category!==categories[i+1])) throw new Error('Unexpected fictional result');
  return parsed;
}
