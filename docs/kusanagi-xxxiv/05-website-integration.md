# Website Integration (VALEXII.COM / Lovable)

- **Frontend Project:** Lovable `811ffc43-2c8b-4c88-ab4c-4de668d089cb`
- **Server Bridge:** `AUREX_SERVICE_TOKEN` / `AUREX_ADMIN_TOKEN` constant-time bearer authentication
- **UI States:** CONNECTED / DEGRADED / UNAVAILABLE / NOT CONFIGURED / NOT VERIFIED
- **Browser Security:** Direct browser access to backend bearer tokens is strictly forbidden; calls route through authenticated server-side bridge.
