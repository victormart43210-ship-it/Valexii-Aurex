# CCLVII — START HERE

Canonicalrepository: https://github.com/victormart43210-ship-it/Valexii-Aurex
ActiveWorkbranch: `work/kusanagi-cclvii-sovereign-execution`, draftPR183.
BaseCopilot181: `c4f45925e086bbb23b643e66707b224419d52b60`. Main:`34cda4bd8f207f5b1284093b87e4760d782a4903`.
Cursor182:`8323f6db245186b98f2bf2c99a9297e88849e15e` remains separate.
Precedingdurablecheckpoint:`bdb09ec3bcf0d90fe8b2b4620fc2610100286f13`. AlwaysverifyactualremotebranchHEAD; self-referentialSHAprohibited.

## Next exact action
Fetch Workremotehead into a cleancheckout and run fullpytest withJUnit, Ruff, strictMypy, websiteVitest/tsc/build, dispater-webtests/build and existing realfrontendHTTPsandbox. Source reviewed repairs are complete; finalverificationpending. Donotrediscoveroldbranches or edit181/182.

## Completed
Proxyprivacyfix0638ace:23focusedPASS. Duplicateticketfixbdb09ec:37financialPASS. APIhourscollectionfix plus4formatoptionalfinancialmetadatafix:68selectedtests exit0; no frozenexpectedtotaledited. Separateagentreview found no critical/important boundedpatchissue; not external/human assurance.

## Environment/reproduce
Python3.12 venv: `python3 -m venv .venv`; `.venv/bin/pip install -e '.[dev]'`. Currentcandidateincludespypdf/openpyxl. HostSOCKSproxymayrequireenvironment-onlysocksio. Node/npmfrontendlockfiles unchanged. `cd website && npm ci --ignore-scripts`; same fordispater-web.
`PYTHONPATH=. AUREX_DB_PATH=<unique disposable path> .venv/bin/python -m pytest -q --junitxml=<evidence>/pytest.xml`.
`.venv/bin/ruff check .`; `.venv/bin/mypy --strict aurex`.
Website:`npx vitest run`; `npx tsc --noEmit`; `npm run build`.
DISPATER-web:`npm test`; `npm run build`.

## Remote recovery
`git fetch origin`; `git ls-remote origin refs/heads/work/kusanagi-cclvii-sovereign-execution`; compareactualheadandreadCCLVII_RECOVERY.json/EXECUTION_LEDGER. GitHubconnectedGit-datawritesusedbecause shellhasnopushauth; expected-SHAleaseandreadbackrequired. LocalcommitaloneLOCAL_ONLY.

## Risks and authority
ReadBUG_REGISTER,FINANCIAL_HARDENING,SECURITY_REVIEW,SOURCE_REVIEW,INTEGRATION_REPORT. Conflictingjob/customerrelationships,ambiguousparserfields,externalanchoring,plaintextfindingcolumns,retentionpolicy,port/HTTP/firewallgapsremain. Cursor182 stillneedsincorporationandreconciledSHAreview. MainlinemergeauthorityNONE. ProductionHOLD,financialNONE,no customerdata/paidinference/training/third-partycontact. No productiondeployment.
