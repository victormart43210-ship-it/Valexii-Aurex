# One Intelligence security verification

| Boundary | Observed scope |
| --- | --- |
| Malformed input | Regression tests cover malformed Base64, duplicate PDF values/table markers, and blank PDF. Format-specific PNG/JPEG magic and decoder limits are exercised offline. |
| Resource limits | Existing DISPATER body and page limits stay active. Imaging limits bytes and pixel dimensions before raster allocation, avoids changing Pillow global limits, and caps reported regions. General hostile-PDF sandboxing and hard wall-clock cancellation remain open. |
| Archive and formulas | Existing XLSX uncompressed-size and macro checks and CSV formula handling remain in the regression suite. No new upload surface. |
| Tenant and credentials | Backend denies unauthorized tenant grants. Website uses a server-owned fixture and tenant, rejects redirects for document submission, and requires agreement with the stored report. |
| Provenance | PDF response digest and page evidence are checked before presentation. Image transforms have separate digests. Report verification does not independently attest source authorship or persist the original file. |
| Injection and models | The new paths treat source data as data and call no model. Paid inference stays off. Existing XAELI negative tests run separately. Live outage, hosted timeouts and independent hypothesis falsification are not qualified. |
| Effects | Finance, research qualification and deployment authority remain NONE or HOLD. No customer material was used. No training, merge or deploy was initiated. |

Pillow 13 is optional for offline imaging. Affected CI suites install the imaging extra. Independent reviewer findings are recorded on the integration PR.
