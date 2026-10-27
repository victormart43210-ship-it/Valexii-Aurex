# CXCVIII runtime evidence — predeployment checkpoint

PR156 remains d2e55319f3261f51b2239350e44952e96b7db074; all four exact-head workflows PASS (40511697951,40511697872,40511697809,40511697828).
Qwen authentication defect: configured LLAMA_ARG_API_KEY is not the supported llama.cpp variable. Official server README documents LLAMA_API_KEY. Set LLAMA_API_KEY to a Railway reference to aurex-api.AUREX_MODEL_API_KEY in aurex-staging only; no secret read/display/rotation. New Qwen deployment 2e8a0944-592b-4e7f-a53f-73b04de12a39 SUCCESS, model loaded and IPv6 listening at 2026-10-27T15:00:48Z, previous no-key warning absent. Authentication requests and actual model ID remain NOT VERIFIED.

AUREX staging was externally changed to root /, Dockerfile /Dockerfile. Latest failed deployment7325b1d4-a353-412e-ad6c-a519d537b4b2 failed at SNAPSHOT_CODE: Failed to create code snapshot. No build/runtime logs returned.

Prepared staging patch89057db4-9bb5-4390-be04-f63ffdd687b0 (7 changes): pin PR156 d2e55319f3261f51b2239350e44952e96b7db074, restore /integrations/kusanagi-xvi/backend and Dockerfile, detach only staging /data mount without deleting volume, set exact private URL and staging probe flag. No model ID set without runtime evidence. Reviewed patch contains no production or unrelated changes.

Stateless app copies only app.py; does not open a database. Staging mount detachment avoids access to any unverified persisted data. Railway documents environment-specific volume instances; logical shared ID does not itself establish shared backing data. Production attachment must remain unchanged.

Production baseline read-only: environment9a139b10-9e6b-4ebd-89c7-731855cbbb5c, deploymentee18058c-cde8-4611-b0bd-443e124c9761 SUCCESS, pinned SHA57a079f93b947594f1a6f854aa46a6f606f86f76, root/integrations/kusanagi-xvi/backend, volume4d23b1e6-3625-4def-aa97-82e10859f04d mounted/data.

Rollback: staging source may be restored to main SHA585023a09fdbff5ec2349a67cc50ef45a9b6f9fd with legacy root, probe disabled. Do not automatically restore the unverified database mount; data remains retained. Production must not be changed. Current model auth should remain enabled.

References: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md ; https://docs.railway.com/integrations/api/manage-volumes ; https://docs.railway.com/guides/isolate-staging-production
