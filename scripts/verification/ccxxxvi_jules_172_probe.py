"""Reproduce review findings against the pinned candidate. All requests stay in process."""
import base64
import hashlib
import json
import os
import runpy
import subprocess
import sys
from pathlib import Path
TARGET = "46befcb04d2a98633876b4239775bedbf0b265ca"
head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
if head != TARGET:
    sys.exit("wrong candidate SHA: " + head)
sys.path.insert(0, str(Path.cwd()))
from fastapi.testclient import TestClient
from aurex import dispater_pipeline as P
from aurex.api import app
from aurex.dispater_envelope import DocumentCategory as D
from aurex.dispater_monitoring import ContinuousMonitoringEngine
if Path(P.__file__).resolve().parent.parent != Path.cwd():
    sys.exit("wrong pipeline module")
observations = {}
def capture(key, *values):
    observations[key] = list(values)

capture("Python",sys.version.split()[0],P.__file__)
s,docs=runpy.run_path('tests/test_dispater_36_month_pipeline.py')['build_36_month_synthetic_dataset']('tenant-a')
p=P.IndustrialAuditPipeline('tenant-a')
for d in docs:
    p.admit_document(d['source_id'], d['source_record_id'], d['category'], d['raw_bytes'], d['media_type'])
r=p.execute_audit_run(s)
capture('golden',r.envelopes_admitted,len(r.qualified_findings),len(r.withheld_findings))
for media,body in [('text/csv',b'amount\n100.00\n'),('application/pdf',b'%PDF-1.4'),('image/png',b'not a PNG'),('application/x-random',b'abc'),('application/json',b'{'),('application/json',b'{"amount":"NaN"}')]:
    pp=P.IndustrialAuditPipeline('tenant-a')
    e=pp.admit_document('x','record',D.INVOICE,body,media)
    capture('parsed '+repr(body),media,[(f.field_name,f.normalized_value,f.qualification_status.value,f.confidence) for f in e.provenance_fields])
pp=P.IndustrialAuditPipeline('tenant-a')
target=s['invoices'][6]
pp.admit_document('same-ledger','alias-A',D.INVOICE,json.dumps(target,separators=(',',':'),sort_keys=True).encode(),'application/json')
pp.admit_document('same-ledger','007',D.UNKNOWN,b'{}','application/json')
bad=pp.execute_audit_run(s)
capture('qualification with unrelated source',[(f['subject'],f['qualification']) for f in bad.qualified_findings])
rec=bad.audit_receipt_sha256
if bad.qualified_findings:
    bad.qualified_findings[0]['exposure_usd']='999999999.00'
    capture('tampered finding; receipt unchanged',bad.audit_receipt_sha256==rec)
monitor=ContinuousMonitoringEngine('tenant-a')
monitor.record_historical_audit(r)
capture('unrelated contract invalidated',monitor.process_contract_update('UNRELATED',{'version':1}))
tk='synthetic-review-token-for-local-test-012345'
os.environ['AUREX_SERVICE_TOKEN']=tk
os.environ['AUREX_DISPATER_TENANT_GRANTS']=json.dumps({hashlib.sha256(tk.encode()).hexdigest():['tenant-a']})
headers={'Authorization':'Bearer '+tk}
client=TestClient(app,raise_server_exceptions=False)
for data in ['!!!!',base64.b64encode(b'[]').decode(),base64.b64encode(b'{"k":1}').decode()]:
    response=client.post('/v1/dispater/pipeline/ingest?tenant_id=tenant-a',headers=headers,json=dict(source_id='x',source_record_id='r',document_category='INVOICE',media_type='application/json',payload_base64=data))
    capture('api ingest '+data,response.status_code,response.json().get('byte_count') if response.status_code==200 else response.text)
a=client.post('/v1/dispater/pipeline/audit',headers=headers,json={k:v for k,v in s.items() if k!='as_of'})
capture('api audit',a.status_code, a.json().get('envelopes_admitted'))

expected = {
    "golden": [72, 0, 2],
    "qualification with unrelated source": [[["INV-36M-007", "QUALIFIED_INDEPENDENT_CORROBORATION"]]],
    "tampered finding; receipt unchanged": [True],
    "unrelated contract invalidated": [["FND-RATE_MISMATCH-INV-36M-007","FND-RATE_MISMATCH-INV-36M-019"]],
    "api ingest !!!!": [200,0],
    "api ingest W10=": [500, "Internal Server Error"],
    "api ingest eyJrIjoxfQ==": [200,7],
    "api audit": [200,0],
    "parsed "+repr(b"amount\n100.00\n"): ["text/csv",[]],
    "parsed "+repr(b"%PDF-1.4"): ["application/pdf",[]],
    "parsed "+repr(b"not a PNG"): ["image/png",[["ocr_text","","PENDING_QUALIFICATION",0.9]]],
    "parsed "+repr(b"abc"): ["application/x-random",[]],
    "parsed "+repr(b"{"): ["application/json",[]],
    "parsed "+repr(b'{"amount":"NaN"}'): ["application/json",[["amount","NaN","QUALIFIED_INDEPENDENT",1.0]]],
}
actual=json.loads(json.dumps(observations))
mismatches=[k for k,v in expected.items() if actual.get(k)!=v]
print(json.dumps({"candidate":head,"observations":actual,"expected_on_defective_candidate":expected,"mismatches":mismatches,"checks":len(expected),"reproduced":len(expected)-len(mismatches)},sort_keys=True,indent=2))
sys.exit(2 if mismatches else 1)  # 1 = reproduced defective behavior, 2 = changed observations
