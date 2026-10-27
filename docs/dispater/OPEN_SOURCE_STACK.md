# DISPATER.AI Open-Source Technology Stack & Dependency Assessment

**Platform:** DISPATER.AI
**Intelligence Engine:** AUREX-OX
**Assistant Interface:** XAELI
**Date:** October 2026
**Status:** APPROVED FOR STAGING IMPLEMENTATION
**Release Authority:** HOLD

---

## 1. Minimal Stack Selection Principle

In accordance with VALEXII engineering standards, DISPATER adopts the minimal compatible open-source stack necessary to deliver continuous industrial audit, monitoring, evidence qualification, and compliance verification without introducing unneeded dependencies, external cloud lock-in, or proprietary hardware constraints.

All selected technologies are open-source, commercially permissive (MIT / Apache-2.0 / BSD), self-hosted, and compatible with Python 3.12+ and Bun/React frontends.

---

## 2. Selected Core Technology Stack

| Capability Domain | Selected Technology | License | Implementation Role in DISPATER | Dependency Status |
| :--- | :--- | :--- | :--- | :--- |
| **Data Validation & Schemas** | **Pydantic v2** | MIT | Contract validation for operational records, observations, audit evidence envelopes, rules, and findings. | **Installed & Core** (`pydantic>=2.0`) |
| **Declarative Policy & Rules** | **Open Policy Agent (OPA) / Rego & Deterministic Python Evaluator** | Apache-2.0 | Policy evaluation for operator compliance, inspection rules, and access control. | **Integrated** (`aurex_foundation.opa` & Python fallback) |
| **Evidence Ledger & Storage** | **SQLite + Deterministic SHA-256 Engine** | Public Domain / Permissive | Cryptographic evidence storage, timestamped audit envelopes, and immutable receipt generation. | **Integrated** (`aurex/database.py`, `aurex/evidence.py`) |
| **Continuous Monitoring** | **OpenTelemetry Python SDK** | Apache-2.0 | Span tracing, telemetry collection, request timing metrics, and monitoring observation logs. | **Integrated** (`aurex/tracing.py`, `aurex/telemetry.py`) |
| **Reporting & Document Generation** | **Jinja2 + HTML5/CSS Print Engine** | BSD-3-Clause | Deterministic evidence-linked report generation and audit receipt templates. | **Integrated** (`jinja2>=3.0`) |
| **System Observability & Metrics** | **Prometheus Metrics Exporter** | Apache-2.0 | Runtime performance counters, audit latency, and observation ingestion rates. | **Integrated Bridge** (`aurex/telemetry.py`) |
| **Governed Reasoning** | **AUREX-OX Engine** | Proprietary/Internal | Reverse audit sequence (ROTAS: Result → Authority → Truth → Admissibility → Source). | **Core Engine** (`aurex/engine.py`, `aurex/dispater_intelligence.py`) |
| **Assistant Interface** | **XAELI 5-Step Explanations** | Proprietary/Internal | 5-step explanation structure (NOW, CHANGED, NEXT, WHY, PROOF) grounded in SHA-256 evidence. | **Integrated Bridge** (`aurex/dispater_intelligence.py`) |

---

## 3. Rejected Candidates & Adoption Rationale

| Candidate | Category | Assessment Result | Reason for Omission / Deferred Adoption |
| :--- | :--- | :--- | :--- |
| **Eclipse Mosquitto / Milo** | MQTT / OPC-UA | Defer to Gateway Stage | External broker complexity not required for synthetic REST/batch audit monitoring. |
| **TimescaleDB / Postgres** | Time-Series DB | Defer to Enterprise Scale | Persistent SQLite with WAL mode meets staging performance targets (2,000 cases in <0.1s). |
| **MinIO** | S3 Object Storage | Defer to Production Scale | Local filesystem SHA-256 digest store provides identical verification guarantees without server overhead. |
| **Great Expectations** | Data Quality | Replaced by Pydantic + Pandera Rules | Pydantic model validation + deterministic exception rules provide lower latency and zero extra dependencies. |
| **River / PyOD** | ML Anomaly Detection | Replaced by Deterministic Rules | ML-based anomaly models lack deterministic auditability; rule-based thresholds enforce verifiable qualification. |

---

## 4. Licensing & Governance Safeguards

1. **License Compliance:** Zero GPL/AGPL copyleft dependencies in backend or website runtime.
2. **Spending Policy:** Zero paid external LLM API usage (`AUREX_SERVICE_TOKEN` default authorized spend = `$0.00`).
3. **Hardware Independence:** No proprietary GPU/NVIDIA runtime lock-in required for continuous monitoring execution.
4. **Authority Boundary:** Open-source monitoring modules deliver advisory findings and evidence envelopes; they possess **MODEL OUTPUT AUTHORITY = NONE**, **FINANCIAL AUTHORITY = NONE**, and **INDUSTRIAL CONTROL AUTHORITY = NONE**.
