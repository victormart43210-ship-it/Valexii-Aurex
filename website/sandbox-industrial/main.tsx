import React from 'react';
import { createRoot } from 'react-dom/client';
import { IndustrialAudit } from '../src/components/industrial-audit';
import { validateIndustrial } from '../src/lib/industrial-contract';
import './style.css';
createRoot(document.getElementById('root')!).render(<main><h1>AUREX / OX</h1><p>LOCAL SANDBOX — isolated test process, not Railway or production.</p><IndustrialAudit mode="LOCAL SANDBOX" run={async fixture=>{const response=await fetch('/__industrial',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({fixture})});if(!response.ok)throw new Error('Unavailable');return {state:'LOCAL_SANDBOX',report:validateIndustrial(await response.json(),fixture)};}}/></main>);
