#!/usr/bin/env python3
"""Read-only AUREX repository / website contract / CI readiness report."""
from __future__ import annotations
import argparse,datetime,json,pathlib,subprocess,sys

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=pathlib.Path,default=pathlib.Path.home()/'Valexii-Aurex')
    a=p.parse_args()
    root=a.root.resolve()
    def cmd(*args):
        r=subprocess.run(args,cwd=root,text=True,capture_output=True,timeout=12)
        return r.stdout.strip() if r.returncode==0 else 'NOT VERIFIED: '+r.stderr.strip()[:120]
    def files(glob): return sorted(str(x.relative_to(root)) for x in root.glob(glob) if x.is_file())
    findings={
        'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'repository':str(root),
        'branch':cmd('git','branch','--show-current'),
        'commit':cmd('git','rev-parse','HEAD'),
        'git_status':cmd('git','status','--short').splitlines(),
        'github_workflows':files('.github/workflows/*.yml')+files('.github/workflows/*.yaml'),
        'website_related_files':(files('integrations/**/*website*')+files('integrations/**/*railway*')+files('docs/**/*website*'))[:50],
        'bridge_contract_present':(root/'integrations/kusanagi-xvi').exists(),
        'local_model_adapter_present':(root/'aurex/local_inference.py').is_file(),
        'workflow_executor_present':(root/'aurex_workflows/local_executor.py').is_file(),
        'workflow_recovery_present':(root/'aurex_workflows/recovery.py').is_file(),
        'website_status':'NOT VERIFIED: no website deployment or authenticated integration test executed',
        'hosted_ci_status':'NOT VERIFIED: GitHub Actions runs require separate inspection',
        'railway_status':'NOT VERIFIED: deployment not queried',
        'xaeli_brain_trust_status':'NOT VERIFIED: no end-to-end integration established',
    }
    report=root/'aurex-xxiii-readiness.json'
    # output file intentionally untracked; avoid overwriting existing report
    if report.exists():
        print('REPORT ALREADY EXISTS (not overwritten):',report)
    else:
        with report.open('x') as fp: json.dump(findings,fp,indent=2)
        print('REPORT CREATED:',report)
    for key in ('branch','bridge_contract_present','local_model_adapter_present','workflow_executor_present','workflow_recovery_present','website_status','hosted_ci_status'):
        print(key+':',findings[key])
    print('NOTE: This audit makes no hosted CI, website, or Railway PASS claims.')
if __name__=='__main__': main()
