# CXCVIII live inference verification

Status: BLOCKED. No model output, correlation ID or latency exists for this operation; none fabricated.
Qwen deployment2e8a0944-592b-4e7f-a53f-73b04de12a39 loaded the model and listens privately on IPv6. AUREX deployment patch is awaiting approval after the deployment tool rejected application. Actual /v1/models identifier and missing/invalid/valid authentication behavior remain NOT VERIFIED.

After approval: verify exact AUREX deploy SHA, run bounded private model discovery and auth matrix; set AUREX_QWEN_MODEL only from returned identifier; submit one authenticated empty-body synthetic-probe request, save sanitized result, request ID, timestamp, deployment IDs and upstream log references. No paid provider or fallback can satisfy the live test.
