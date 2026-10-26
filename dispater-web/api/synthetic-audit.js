// Server-side fictional demonstration; never accepts client records or authorizes effects.
const sources = Object.freeze({
 towing: {ticket:"TOW-DEMO-042",invoice:"NO_MATCH",rateCents:250000,wreckerHours:3,wreckerHourlyCents:30000,supportHours:3,supportHourlyCents:15000},
 oilfield: {ticket:"FIELD-DEMO-014",invoice:"NO_MATCH",rateCents:125000,wreckerHours:0,wreckerHourlyCents:0,supportHours:0,supportHourlyCents:0}
});
export default function handler(req,res){
 res.setHeader("Cache-Control","no-store");res.setHeader("X-Content-Type-Options","nosniff");
 if(req.method!=="GET"){res.setHeader("Allow","GET");return res.status(405).json({error:"METHOD_NOT_ALLOWED"})}
 const sector=String(req.query?.sector||"towing");
 if(!Object.hasOwn(sources,sector))return res.status(400).json({error:"UNSUPPORTED_SECTOR"});
 const x=sources[sector],cents=x.rateCents+x.wreckerHours*x.wreckerHourlyCents+x.supportHours*x.supportHourlyCents;
 return res.status(200).json({schema:"dispater.synthetic.backend.v1",classification:"FICTIONAL_DATA_ONLY",runtime:"VERCEL_SYNTHETIC_DEMO",aurexRuntime:"NOT_CONNECTED",independentVerification:"NOT_VERIFIED",authority:"NONE",status:"HOLD",sector,stages:["EVIDENCE","QUALIFICATION","REALITY","AUTHORITY","EFFECT"],candidate:{ticket:x.ticket,invoice:x.invoice,amountCents:cents,reviewRequired:true,confirmedRevenue:false},source:"STATIC_SYNTHETIC_FIXTURE",warning:"No client records, AUREX audit execution, financial writeback or external effects."});
}
