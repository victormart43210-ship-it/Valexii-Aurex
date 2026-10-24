# KUSANAGI CL — Adversarial API Contract & Health Matrix

## Overview
Independent adversarial audit of the AUREX API health contracts, service adapters, and client bridges across `aurex/api.py`, `integrations/kusanagi-xvi/backend/app.py`, and `website/src/lib/aurex-*.ts`.

## Adversarial Test Matrix
| Scenario | Request | Backend / Adapter Reaction | Result State | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Missing Bearer Token** | `GET /v1/capabilities` | HTTP 401 Unauthorized | `unauthorized` | **PASS** |
| **Insecure Token (<32 chars)** | `GET /v1/health` | HTTP 500 / `NOT_CONFIGURED` | `NOT_CONFIGURED` | **PASS** |
| **Malformed JSON Body** | `GET /v1/health` (returns HTML/text) | JSON.parse fails closed | `OFFLINE` | **PASS** |
| **Missing `status` Field** | `GET /v1/health` (returns `{}`) | HealthSchema validation fails | `OFFLINE` | **PASS** |
| **Non-HTTPS / Local URL** | `https://localhost` or `http://...` | `validServiceUrl` returns null | `NOT_CONFIGURED` | **PASS** |
| **Missing `capabilities` Array** | `GET /v1/health` (returns `{"status":"ok"}`) | Missing `capabilities` array fails schema | `OFFLINE` | **PASS** |
| **Unknown Capability ID** | `capabilities: ["invalid_cap"]` | Regex filter `^[a-z-_]{1,64}$` strips unknown ID | `HEALTHY` (filtered) | **PASS** |
| **HTTP 503 Service Unavailable** | `GET /v1/jobs` (worker disabled) | HTTP 503 Service Unavailable | `http_error` (503) | **PASS** |
| **Oversized Response (>256KB)** | `GET /v1/jobs` | Response byte cap enforced | `too_large` | **PASS** |
| **Clock Skew (+30s Server Lead)** | `collectedAt: now + 30s` | `evidenceFresh()` within 60s tolerance | `HEALTHY` | **PASS** |
| **Genuinely Future Evidence (+120s)**| `collectedAt: now + 120s` | `evidenceFresh()` returns false | `OFFLINE` | **PASS** |
| **Stale Evidence (>7 Days)** | `collectedAt: now - 8 days` | `evidenceFresh()` returns false | `OFFLINE` | **PASS** |

## Conclusion
All 12 adversarial health-contract scenarios behave fail-closed. No valid evidence is accepted from untrusted sources, and transport reachability is never conflated with execution authority.
