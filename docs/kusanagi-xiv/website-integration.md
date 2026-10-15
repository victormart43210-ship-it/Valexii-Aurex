# Website integration instructions (Lovable)

The VALEXII.COM site uses Lovable. If you cannot modify Lovable directly, apply these server-side instructions on the website server.

Server-side adapter (recommended)

- Place the provided `aurex/web_adapter.py` on the website server (or install the repository as a package in the website environment).
- Configure environment variables on the website server only (example):
  - AUREX_SERVICE_TOKEN (>=32 chars)
  - AUREX_API_BASE (example: https://aurex-staging.valexii.internal)

Example usage (pseudo-Lovable route handler)

1. User POST /aurex/ask with JSON {"request_id": "r1", "claim": "...", "evidence": []}
2. Server-side route:
   - Verify logged-in user and authorization
   - Call WebsiteAdapter.create_job(...) and return job id to client
3. Client polls /aurex/jobs/{job_id} (server-side) which proxies to AUREX /v1/jobs/{job_id}

Security notes

- Do not expose tokens to the browser
- Use server-side session cookies or JWTs with short TTL
- Enforce per-user rate limits

