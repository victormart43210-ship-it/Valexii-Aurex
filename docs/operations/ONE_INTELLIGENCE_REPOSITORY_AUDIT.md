# One Intelligence repository audit

Baseline `fc2bed4dd98054503254ad1a4c11fbecd7b0deca` on canonical `main`. Production HOLD. Merge authority NONE.

| Source | Observed relationship and disposition |
| --- | --- |
| #193 | Open, unmerged at `ff62f319c4c37ea3660d008b8fb119ca3dee476a`, targets the historical #192 branch at `f381db7c`. Recovered the five offline imaging modules only. The old router, frontend, TIFF and spectral paths remain isolated. |
| #212 | Open at `ad6a93201516a0ec9168f95128f396d38e39f158`. Candidate knowledge registry, not a durable evidence store. This integration does not depend on it. |
| #208 | Open at `f014111853c3dd89641297519871afdc957e969a`. Qwen diagnostic and startup changes remain outside this candidate. |
| #209 → #210 → #211 | Open cumulative Forge stack at `b995df78`, `b3d40627`, and `e3244e7a`. Not required for deterministic document processing. |
| #197 and #176 | Closed without merge. #205 selectively recovered industrial detectors and the audit package endpoint and is merged. |
| Jules CCCXXXIX, CCCXL, CCCXLI | No matching branches, PRs or issues in accessible GitHub searches. Private assignments and unpushed work remain unknown. |

The existing document boundary is `POST /v1/dispater/documents` in `aurex/dispater_api.py`. It uses `dispater_ingest` and `dispater_documents` for labeled CSV/JSON, digital PDF and text-only XLSX. PNG/JPEG and image-only PDF are rejected by this route without OCR. Findings and report receipts use the existing reconciliation and store. The document source wrapper is separate from that receipt.

The website already offers a fixed CSV and server-side backend connection on `/dispater`. `/voynich`, `/decipherment` and `/research` exist. The synthetic script calibration in `aurex/ascendancy/manuscript_adapter.py` measures rule versus memorizer behavior on labeled controls. It does not load historical script. CUSTOS policy and verification material exist, while no authenticated SHRIKE/CUSTOS orchestration is wired to the new imaging functions. XAELI private model work is separately gated.

Railway read-back identified successful deployment `a0f412a1-4e74-49ac-bdcd-137e642a1cd6` at baseline `fc2bed4`, with private Qwen in the existing staging environment. No candidate deployment or hosted inference was performed. Prior GitHub push CI at baseline succeeded. See the integration PR for candidate workflows.
