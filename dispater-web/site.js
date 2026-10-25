/** Read-only Railway staging connectivity check; health is not audit authorization. */
const check=document.getElementById("railway-check");
const status=document.getElementById("railway-result");
if(check&&status){
 check.addEventListener("click",async()=>{
   check.disabled=true;
   status.textContent="Checking read-only staging health…";
   try{
    const response=await fetch("/api/railway-status",{method:"GET",cache:"no-store",credentials:"same-origin"});
    if(!response.ok)throw Error("PROBE_UNAVAILABLE");
    const data=await response.json();
    const ok=data.stagingReachability==="HEALTH_ENDPOINT_RESPONDED";
    status.textContent=(ok?"STAGING HEALTH ENDPOINT ANSWERED":"STAGING HEALTH NOT VERIFIED")+
      " · AUREX FINANCIAL AUDIT NOT CONNECTED · AUTHORITY NONE";
   }catch{
    status.textContent="STAGING HEALTH NOT VERIFIED · NO FINANCIAL ACTION";
   }finally{check.disabled=false;}
 });
}
