# CCLV conflict resolution record

Trial merges were made (then aborted) against the Cursor-stack tip `77a97c1`.

| PR | Conflicting files | Decision |
|----|-------------------|----------|
| #168 CCXXIX evidence enforcement | dispater_api/intelligence/receipt/store, receipt + evidence-kernel tests, website console | **BLOCKED.** Competing receipt/store implementation. Not auto-resolved: picking either side could weaken receipt checks. |
| #172 CCXXXII 36-month pipeline (Jules/Work) | ingest, intelligence, receipt, store, api, golden/convergence/monitor tests, web contract | **BLOCKED.** A second financial engine. Keeping the Cursor stack avoids two calculation paths. Port only after fixture parity is shown; do not edit golden totals. |
| #175 CCXXXVIII assurance | dispater_api, JULES handoff | **BLOCKED.** Assures #171+#172; #172 excluded. |
| #176 Global Ascension III (Jules) | 16 files incl. api/intelligence/store, web contract, tests | **BLOCKED.** Also CONFLICTING against `main`. |
| #159 CCX (Jules) | adversarial library, handoffs, body-limit test | **BLOCKED.** Largely superseded by merged #160-#162/#165. |

Why the Cursor stack won: it is the only candidate that is linear on `main`, conflict-free, and has CI green (6 check runs) at its tip with a documented NO-GO decision. This is a selection of *integration base*, not a judgement that the excluded implementations are wrong. No security check or financial invariant was removed. Unresolved conflict = left out.
