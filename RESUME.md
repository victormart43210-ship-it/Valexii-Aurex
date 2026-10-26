# CLXXXIV resume

Read RECOVERY.json, docs/operations/KUSANAGI_CLXXXIV_SOVEREIGN_EXECUTION.md and docs/handoffs/KUSANAGI_CLXXXIV_WORK_TO_JULES.md.

Draft PR #150, branch work/kusanagi-clxxxiv-inference-guard. Tested implementation CP003: dc6ed44c486b94d1723a6d1095f2ff51e20aec09; containing later commit is documentation-only. Fetch remote head and compare before editing. Full tests 449 passed, 2 skipped; Ruff/MyPy PASS; DISPATER Node 25 passed/build PASS. Latest GitHub CI still requires readback.

First task: independently review the transport denial and run focused tests from the handoff. Next repair PR145's reproduced sibling-path policy defect before resolving its conflicts. Remote enablement requires durable accounting and complete admission controls; no environment flag may unlock it. Preserve Onyx PR146 rather than duplicate it. Do not repeat completed inventory except to detect new commits.

No paid inference, production, merge, credential changes or customer records. Full live end-to-end integration remains NOT VERIFIED. If interrupted, commit/publish with expected-head protection and verify remote SHA.
