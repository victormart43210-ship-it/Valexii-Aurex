# Real Worker Execution Lifecycle

AUREX implements worker execution through `aurex/adapters/execution.py` and `aurex/database.py`:
1. `JobCreateRequest` received at `POST /v1/jobs`
2. Idempotency & bearer token auth validated
3. Job created atomically in SQLite database (`queued` state)
4. Worker process executes deterministic or model task
5. SHA-256 fingerprint computed for input & output payloads
6. Evidence persisted in SQLite ledger (`aurex/database.py`)
7. Job transitions to `succeeded` with linked `evidence_id`
