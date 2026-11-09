# Cursor #174 independent source challenge

**Disposition: HOLD.** A synthetic tow ticket carries 8 billable hours at $25. The same job yielded **$200.00** in the direct engine, **$0.00** through the authenticated reconciliation route, and **$25.00** through the authenticated documents route. Both routes returned HTTP success. Human review depends on which entry point the operator uses.

Reviewed canonical PR #174 at `2d0b62400e0ad40f2780f51b26ba0d09261cd724` in a detached, clean checkout. Compared Git diff against parent candidate #171 at `db4670ab78fa36c8a2b4b8b66df842350440e437`. Read the repository instructions and Cursor handoff. It reports implementation commit `8409075b27dc905e015e276ef90d6f63823af33c` plus handoff update. This reviewer developed counterexamples separately from the candidate author. All inputs and keys were synthetic. Release and financial approval remain with the owner.

| Boundary | Observed result | Source |
|---|---|---|
| Hourly rate through HTTP | The direct engine computes 8 × $25 correctly. The reconciliation request drops the equipment collection. The document path retains the equipment row but drops the rate unit and charges the unbilled job once at $25. | `aurex/dispater_api.py:ReconciliationRequest`, `aurex/dispater_ingest.py:REQUIRED, ingest_source`, `aurex/dispater_intelligence.py:_append_unbilled_hours` |
| Payment reversal | Direct engine nets a $40 reversal against a $100 payment to $60. Parsing the identical JSON drops the reversal kind, adding the $40 as a payment to $140. Both discrepancies have magnitude $40 while their directions are opposite. An unsigned difference alone misses the defect. | `aurex/dispater_intelligence.py:_signed_payment`, `aurex/dispater_ingest.py:_rows_from_json` |
| Ambiguous XLSX | A real workbook with two amount columns containing 999 and 1 returns an accepted invoice for 1. The parser takes the last value. Source inspection also finds repeated fields overwrite earlier fields in PDF text; PDF reproduction was outside this bounded test. | `aurex/dispater_documents.py:extract_xlsx, _pages_from_text` |
| Persisted event replay and tampering | A retry after closing/reopening SQLite connections returned the existing event ID. Rewriting only the stored event payload to claim financial authority GRANTED was returned on read, although the outer recovered amount remained zero. No payment executed. The v2 run receipt protects the report. The derived event payload has a separate integrity gap. | `aurex/dispater_monitor.py:persist_increment`, `aurex/dispater_store.py:save_monitor_event, _monitor_row` |
| Input provenance and money carried from #171 | All seven previous negative gates still fail: contradictory tenant/live labels, duplicate CSV amount headers, short CSV row exception, unsupported JSON tables, duplicate JSON keys, potentially duplicated remittance included in exposure, and omitted rate evidence for flat unbilled work. Both no-cash checks pass. | Replay of #171 cases against #174 runtime, including expanded ingest tables. |

Additional source observations: the monitor validates supplied digest length only and returns a cached event before validating supplied datasets. Its run and event writes use separate transactions. Recovery under a crash between those commits, true concurrent changed-payload replay, and process-crash durability were outside this probe. These checks measure stored event and API behavior only. Capture source bytes and corroborated financial outcomes separately for real-world verification.

## Reproduction

Use the clean #174 checkout as working directory. The standalone Work probe verifies candidate HEAD, checks tracked runtime state and import paths, runs the real local ASGI endpoints with a temp DB, and emits one JSON observation per check.

```bash
export PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1
../Valexii-Aurex/.venv/bin/python ../ccxxxvi/scripts/verification/ccxxxvi_cursor_174_probe.py
```

**Observed exit 1: 18 cases, 5 passed, 13 failed.** Nine inherited checks yielded two passes and seven failures; nine new checks yielded three passes and six failures. Entry-point reproductions deliberately cover financial defects at both module and HTTP boundaries. Counts refer to checks, not distinct defects. Used Python 3.12, openpyxl 3.1.5 and pypdf 6.21.4. The run emitted the installed Starlette TestClient deprecation warning and expected ephemeral-storage notices. Preserved actual output is reproduced by the probe. Full regressions, browsers, field validation, hosted storage and production deployments were outside this review lane. No product file was modified.
