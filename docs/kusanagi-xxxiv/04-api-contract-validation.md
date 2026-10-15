# API Contract Validation

OpenAPI v1 Endpoints (`aurex/api.py`):
- `GET /v1/health` - Public health check
- `GET /v1/capabilities` - Authenticated capabilities listing
- `GET /v1/jobs` - Authenticated job listing
- `POST /v1/jobs` - Authenticated job creation
- `GET /v1/jobs/{job_id}` - Authenticated job status
- `POST /v1/jobs/{job_id}/cancel` - Authenticated job cancellation
- `GET /v1/evidence` - Authenticated evidence ledger
- `GET /v1/budgets` - Authenticated budget status ($0.00 default)
