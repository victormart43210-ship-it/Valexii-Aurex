import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import * as Tabs from "@radix-ui/react-tabs";
import { FIXTURES, audit, reviewFinding } from "./audit.mjs";

const cls=(...a)=>a.filter(Boolean).join(" ");
const Card=({children,className=""})=><div className={cls("shad-card",className)}>{children}</div>;
const Badge=({children,tone=""})=><span className={cls("shad-badge",tone)}>{children}</span>;
const Button=({children,onClick,disabled=false,variant="primary",label})=><button type="button" onClick={onClick} disabled={disabled} aria-label={label} className={cls("shad-button",variant)}>{children}</button>;
const titleCase=s=>s.replaceAll("_"," ").toLowerCase().replace(/\b\w/g,c=>c.toUpperCase());
const INDEXES={
  irs:[
    {item:"Invoice and receipt register",supports:"Links transactions to supporting tickets or receipts"},
    {item:"Rate and service agreements",supports:"Supports billed terms, dates and reviewed adjustments"},
    {item:"Expense and payment reconciliation",supports:"Organizes business expense and payment evidence"},
    {item:"Payroll and contractor documentation",supports:"Prepares a list for qualified tax review"}
  ],
  dot:[
    {item:"Driver qualification files",supports:"Applicability depends on vehicles and operations"},
    {item:"Vehicle inspection and maintenance records",supports:"Possible records for regulated vehicle operations"},
    {item:"Hours-of-service and supporting logs",supports:"Only where the relevant rules apply"},
    {item:"Incident and safety documentation",supports:"Subject to jurisdiction and business activity"}
  ]
};
function Icon({name}){
 const map={overview:"◎",revenue:"↗",irs:"▤",dot:"⬡",proof:"♧"};
 return <span aria-hidden="true" className="shad-icon">{map[name]||"·"}</span>;
}
function Stat({label,value,foot,tone=""}){
 return <Card className="shad-stat"><div className="shad-stat-label">{label}<span aria-hidden="true">↗</span></div><strong className={cls("shad-stat-value",tone)}>{value}</strong><span className="shad-stat-foot">{foot}</span></Card>;
}
function Download(report,sector){
 if(!report)return;
 const content={...report,exportType:"FICTIONAL_EXAMPLE_NOT_TAX_OR_DOT_AUDIT"};
 const blob=new Blob([JSON.stringify(content,null,2)+"\n"],{type:"application/json"});
 const url=URL.createObjectURL(blob);
 const a=document.createElement("a");a.href=url;
 a.download="dispater-"+sector+"-FICTIONAL-exception-review.json";
 a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);
}
function IndexPane({kind,sector}){
 const isDOT=kind==="dot";
 return <div className="shad-section-view">
   <div className="shad-pane-header"><div>
     <Badge tone={isDOT?"amber":"cyan"}>{isDOT?"DOT / FMCSA DOCUMENT REVIEW":"IRS-SUPPORTING DOCUMENT REVIEW"}</Badge>
     <h4>{isDOT?"Make applicability clear before making compliance claims.":"Turn scattered supporting records into a reviewable index."}</h4>
     <p>{isDOT
       ?"The applicability of transportation requirements depends on the company, vehicle types, activities and jurisdiction. This example does not determine a carrier's legal obligations."
       :"A practical index can help a tax professional locate records and spot support gaps. This illustrative screen is not a tax return, IRS audit, tax determination or assurance of compliance."}</p>
    </div><Badge tone="hold">NOT VERIFIED</Badge></div>
   <div className="shad-evidence-table-wrap"><table className="shad-table"><thead><tr><th>Evidence category</th><th>Why it may matter</th><th>Example state</th></tr></thead><tbody>
     {INDEXES[kind].map((item,i)=><tr key={i}><td><span className="shad-table-key">{item.item}</span></td><td>{item.supports}</td><td><Badge tone="amber">NOT REVIEWED</Badge></td></tr>)}
   </tbody></table></div>
   <div className="shad-alert"><span aria-hidden="true">◇</span><p><b>Human review required.</b> These are example categories, not a complete legal checklist. Qualified tax or transportation specialists must evaluate applicable obligations and actual records.</p></div>
  </div>;
}
function RecordDistribution({sector}){
 const f=FIXTURES[sector],data=[
  {key:"Tickets",n:f.jobs.length},
  {key:"Invoices",n:f.invoices.length},
  {key:"Rate sheets",n:f.rates.length},
  {key:"Payments",n:f.payments.length},
  {key:"Evidence references",n:f.evidence.length}
 ];
 const total=data.reduce((a,x)=>a+x.n,0);
 return <Card className="shad-chart-card"><div className="shad-card-title">Source record distribution</div>
 <p>Counts are computed from the selected fictional fixture, not customer activity.</p>
 <div className="shad-bar-list">{data.map((x,i)=><div className="shad-bar-row" key={x.key}><span>{x.key}</span><div className="shad-bar-track"><div className={cls("shad-bar-fill","bar-"+i)} style={{width:(100*x.n/Math.max(1,total))+"%"}}></div></div><b>{x.n}</b></div>)}</div>
 <span className="shad-caption">SAMPLE TOTAL: {total} RECORDS · FICTIONAL</span>
 </Card>;
}
function RevenuePane({sector,report,onRun,onExport,onDisposition}){
 return <div className="shad-section-view">
  <div className="shad-pane-header"><div><Badge tone="cyan">REVENUE RECONCILIATION</Badge>
   <h4>Find candidate gaps. Follow the source.</h4>
   <p>Compare fictional tickets, rate sheets, invoices and payments, then send each flag through human review.</p></div>
   <div className="shad-actions"><Button onClick={onRun}>RUN FICTIONAL CHECK ↗</Button><Button onClick={onExport} disabled={!report} variant="subtle">EXPORT EXAMPLE ↓</Button></div>
  </div>
  <div className="shad-work-grid"><RecordDistribution sector={sector}/>
   <Card className="shad-workflow-card"><div className="shad-card-title">Review path</div>
   <p>Evidence → Qualification → Reality → Authority → Effect</p>
   <ol className="shad-flow"><li><b>01</b> Source record found</li><li><b>02</b> Candidate mismatch detected</li><li><b>03</b> Manager reviews evidence</li><li><b>04</b> No automated writeback</li></ol>
   <Badge tone="hold">FINANCIAL AUTHORITY: NONE</Badge></Card>
  </div>
  <Card className="shad-table-card"><div className="shad-card-title">Exception review queue <Badge tone="muted">SYNTHETIC</Badge></div>
   {!report?<div className="shad-empty">Run the fictional check to populate this queue. No business data is uploaded or retained.</div>:
    <div className="shad-evidence-table-wrap"><table className="shad-table"><thead><tr><th>Exception</th><th>Referenced record(s)</th><th>Human disposition</th></tr></thead><tbody>
     {report.findings.map(f=><tr key={f.id}><td><span className="shad-table-key">{f.title}</span><small>{f.explanation}</small></td><td className="shad-refs">{f.references.join(" · ")}</td><td><select aria-label={"Disposition for "+f.title} value={f.disposition} onChange={e=>onDisposition(f.id,e.target.value)}>
       <option value="NOT_REVIEWED">Not reviewed</option><option value="ACKNOWLEDGED">Acknowledged</option><option value="DISPUTED">Disputed</option><option value="REFER_TO_SPECIALIST">Refer to specialist</option>
     </select></td></tr>)}
     </tbody></table></div>}
  </Card>
 </div>;
}
function App(){
 const [sector,setSector]=useState("towing");
 const [report,setReport]=useState(null);
 const [tab,setTab]=useState("revenue");
 const [guideOpen,setGuideOpen]=useState(false);
 const [guideStep,setGuideStep]=useState(0);
 const [backendStatus,setBackendStatus]=useState("NOT CHECKED");
 const [backendCheckedAt,setBackendCheckedAt]=useState(null);
 const checkBackend=async()=>{setBackendStatus("CHECKING");try{const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),6000);let response;try{response=await fetch("/api/aurex-health",{cache:"no-store",signal:controller.signal,credentials:"omit",headers:{"Accept":"application/json"}})}finally{clearTimeout(timer)}if(!response.ok)throw Error("unavailable");const data=await response.json();if(!data||typeof data!=="object"||Array.isArray(data))throw Error("unexpected");setBackendStatus("REACHABLE · HEALTH ONLY")}catch{setBackendStatus("NOT VERIFIED")}setBackendCheckedAt(new Date().toLocaleTimeString())};
 useEffect(()=>{checkBackend()},[]);
 const f=FIXTURES[sector];
 const counts=report?.counts||{jobs:f.jobs.length,invoices:f.invoices.length,findings:"—"};
 const records=f.jobs.length+f.invoices.length+f.payments.length+f.rates.length+f.evidence.length;
 const changeSector=x=>{setSector(x);setReport(null);};
 const setDisposition=(id,value)=>{
   if(!report)return;
   if(value==="NOT_REVIEWED"){const x=report.findings.find(f=>f.id===id);if(x)x.disposition="NOT_REVIEWED";}
   else reviewFinding(report,id,value);
   setReport({...report,findings:[...report.findings]});
 };
 return <div className="shad-shell">
  <aside className="shad-sidebar" aria-label="Audit workspace navigation">
    <div className="shad-side-brand"><span>⬡</span><div>DISPATER <small>AUDIT READINESS</small></div></div>
    <div className="shad-side-section">WORKSPACE</div>
    {[["revenue","Revenue Audit"],["irs","IRS Evidence"],["dot","DOT / FMCSA Evidence"]].map(([id,label])=>
      <button key={id} type="button" onClick={()=>setTab(id)} className={cls("shad-side-link",tab===id&&"selected")} aria-current={tab===id?"page":undefined}><Icon name={id}/>{label}</button>)}
    <div className="shad-side-section">CONTROL GATES</div>
    <div className="shad-side-foot"><span>● DEMO MODE</span><strong>HUMAN REVIEW REQUIRED</strong><small>AUREX staging is separate. No IRS/DOT compliance authority.</small></div>
  </aside>
  <div className="shad-main">
   <div className="shad-topline"><div><span className="shad-breadcrumb">DISPATER / AUDIT COMMAND CENTER</span><h3>Audit Readiness Workspace</h3></div><div className="shad-topline-right"><Button variant="subtle" onClick={()=>{setGuideStep(0);setGuideOpen(true)}} label="Open guided audit walkthrough">GUIDED TOUR ◈</Button><Badge tone="hold">HOLD</Badge><Badge tone="cyan">FICTIONAL DATA</Badge></div></div>
   {guideOpen&&<div className="shad-guide-backdrop" onMouseDown={e=>{if(e.target===e.currentTarget)setGuideOpen(false)}}>
    <section className="shad-guide-panel" role="dialog" aria-modal="true" aria-labelledby="shad-guide-title" onKeyDown={e=>{if(e.key==="Escape")setGuideOpen(false)}}>
      <div className="shad-guide-header"><Badge tone="cyan">INTERACTIVE · FICTIONAL</Badge><button type="button" className="shad-guide-close" onClick={()=>setGuideOpen(false)} aria-label="Close guided tour">✕</button></div>
      <p className="shad-guide-kicker">AUREX/OX · EVIDENCE-FIRST REVIEW</p>
      <h4 id="shad-guide-title">How DISPATER's audit flow is designed to work</h4>
      <div className="shad-guide-progress" aria-label={"Step "+(guideStep+1)+" of 5"}>{["Evidence","Qualification","Reality","Authority","Effect"].map((name,i)=><button key={name} type="button" onClick={()=>setGuideStep(i)} aria-current={guideStep===i?"step":undefined} aria-label={"Go to "+name}><span>{String(i+1).padStart(2,"0")}</span><small>{name}</small></button>)}</div>
      <div className="shad-guide-detail">
       <span>STEP {guideStep+1} / 05</span>
       <h5>{["Connect the source","Qualify the records","Reconcile what happened","Put authority with people","Act only when permitted"][guideStep]}</h5>
       <p>{[
        "Start with a fictional heavy-recovery dispatch ticket, work record, rate sheet and invoice export. Each source remains identifiable.",
        "Check timestamps, completeness and source integrity. Missing information is not treated as verified.",
        "A $3,850 potential unbilled job is identified using invented example charges. This is a candidate for review, not confirmed lost revenue.",
        "An authorized reviewer validates the work, rate agreement, supporting evidence and any proposed billing action.",
        "Only a separately authorized production system could perform approved writebacks. This demonstration performs no operational or financial actions."
       ][guideStep]}</p>
       <div className="shad-guide-gate"><b>CONTROL GATE</b><span>{["SOURCE PROVENANCE REQUIRED","UNKNOWN ≠ SAFE","NOT VERIFIED ≠ CONFIRMED","HUMAN APPROVAL REQUIRED","FINANCIAL AUTHORITY: NONE"][guideStep]}</span></div>
      </div>
      <div className="shad-guide-actions"><Button variant="subtle" disabled={guideStep===0} onClick={()=>setGuideStep(Math.max(0,guideStep-1))}>← BACK</Button><Button onClick={()=>guideStep===4?setGuideOpen(false):setGuideStep(guideStep+1)}>{guideStep===4?"FINISH TOUR":"CONTINUE →"}</Button></div>
      <p className="shad-guide-foot">Concept demonstration only. No customer data, independent verification, automated decisions, or verified competitor performance claims.</p>
    </section>
   </div>}
   <div className="shad-toolbar"><div className="shad-toolbar-left"><span>INDUSTRY DATASET</span><div className="shad-toggle" role="group" aria-label="Select fictional industry dataset">
     <button type="button" aria-pressed={sector==="towing"} onClick={()=>changeSector("towing")}>Towing &amp; Recovery</button>
     <button type="button" aria-pressed={sector==="oilfield"} onClick={()=>changeSector("oilfield")}>Oilfield Operations</button>
   </div></div><span className="shad-powered">AUREX/OX · SOURCE-BASED REVIEW MODEL</span></div>
   <div className="shad-backend-status" role="status" aria-live="polite"><div><strong>AUREX/OX STAGING CONNECTION</strong><span>{backendStatus}</span><small>Read-only backend health check · Audit runtime NOT CONNECTED · No customer data sent · Authority NONE{backendCheckedAt?" · Checked "+backendCheckedAt:""}</small></div><Button variant="subtle" onClick={checkBackend} disabled={backendStatus==="CHECKING"}>CHECK CONNECTION ↻</Button></div>
   <div className="shad-stats-grid">
     <Stat label="Source records" value={String(records)} foot="Fictional indexed records" tone="cyan"/>
     <Stat label="Candidate exceptions" value={String(counts.findings)} foot="Review required, not findings of noncompliance"/>
     <Stat label="IRS evidence" value="UNREVIEWED" foot="Supporting categories only" tone="small"/>
     <Stat label="DOT applicability" value="UNKNOWN" foot="Jurisdiction and scope unassessed" tone="small"/>
   </div>
   <Tabs.Root value={tab} onValueChange={setTab} className="shad-tabs">
    <Tabs.List className="shad-tab-list" aria-label="Audit readiness sections">
      <Tabs.Trigger value="revenue">REVENUE AUDIT</Tabs.Trigger>
      <Tabs.Trigger value="irs">IRS EVIDENCE</Tabs.Trigger>
      <Tabs.Trigger value="dot">DOT / FMCSA EVIDENCE</Tabs.Trigger>
    </Tabs.List>
    <Tabs.Content value="revenue" className="shad-tab-content"><RevenuePane sector={sector} report={report} onRun={()=>setReport(audit(sector))} onExport={()=>Download(report,sector)} onDisposition={setDisposition}/></Tabs.Content>
    <Tabs.Content value="irs" className="shad-tab-content"><IndexPane kind="irs" sector={sector}/></Tabs.Content>
    <Tabs.Content value="dot" className="shad-tab-content"><IndexPane kind="dot" sector={sector}/></Tabs.Content>
   </Tabs.Root>
   <div className="shad-runtime-foot"><span>FICTIONAL RECORDS ONLY · NO LIVE CLIENT ACCOUNTS</span><span>INFERENCE: NOT RUN · FINANCIAL AUTHORITY: NONE</span></div>
  </div>
 </div>;
}
const node=document.getElementById("audit-dashboard-root");
if(node)createRoot(node).render(<App/>);
