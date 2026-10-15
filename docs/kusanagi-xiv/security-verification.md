# Security verification checklist

This checklist maps repository components to required security hardening tasks and the verification steps.

Secrets and tokens

- Ensure AUREX_SERVICE_TOKEN and AUREX_ADMIN_TOKEN are set only on server-side/environment and never embedded into frontend code
- Verify tokens are >= 32 characters where required

Authentication and authorization

- Confirm authenticate() in aurex/api.py uses constant-time comparison (hmac.compare_digest) — verified
- Confirm admin/service token conflict handling is acceptable for your operations

Network controls

- Adapters must validate `base_url` values and disallow credentials, queries, fragments, and redirects (OpenAICompatibleAdapter and OllamaAdapter already perform these checks)

Budget controls

- BudgetGuard defaults to $0.00; ensure adapters call reserve()/settle() correctly

Logging

- Add structured diagnostics without secrets; do not log full bearer tokens or private keys

Tests and negative tests

- Add tests that exercise missing tokens, invalid hostnames, oversized responses, malformed JSON

