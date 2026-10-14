# Linux / native Qwen connectivity

Status: **BLOCKED**. No authorized live Linux connection supplied. No connection to the user's localhost was attempted from this cloud environment. The backend contains a loopback llama.cpp adapter but no recovered Phase 44/45 gateway at 8944, and no API job invokes that adapter.

Local verification sequence, to run on the actual authorized Linux host:

```bash
git rev-parse HEAD
git status --short
ss -ltnp 'sport = :8944 or sport = :8080'
python3 -m pytest -q
ruff check .
python3 -m mypy aurex --strict
curl --fail --max-time 5 http://127.0.0.1:8080/v1/models
```

Do not include secret values in transcripts. Review actual gateway source before choosing its endpoints; `/health` and `/api/v1/*` are discovery candidates, not verified contracts. Use the actual process/service configuration to establish model identity, binary revision and model-file digest. An ID returned by the model server alone is not proof of artifact identity.

For an explicit inference check, invoke the existing LlamaCppAdapter locally with the actual model identifier and a synthetic request such as “Reply with the word READY.” Retain the exact request, response, HTTP outcome, UTC timestamp, model ID, adapter revision and model-file hash. Label this local inference evidence, not staging or website end-to-end evidence. Then test gateway outage, model outage, timeout, cancellation, replay and revoked authorization through the approved API path.

Minimum future connectivity: an operator-approved HTTPS AUREX API reachable from the website server, server-side credentials, authenticated application user/owner authorization, private access from AUREX to the local inference service, network egress controls and bounded requests. No inference-port exposure or unapproved tunnel. Hosting/network decisions require explicit authorization; no paid infrastructure was provisioned.
