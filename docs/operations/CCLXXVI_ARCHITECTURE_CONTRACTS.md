# CCLXXVI frozen industrial contracts

Contract version: `valexii.industrial.contracts.v1`.

Base: `origin/main` `061b97022797013ccd1395a377b9489e59ba83f3`. This branch does not contain pull request 193. That pull request was not merged, rebased, or activated.

These contracts are the code in `aurex/relationships/contracts.py`. A second prose copy is not the authority. DISPATER finding codes, qualifications, and the golden totals stay as they are.

## Preserved DISPATER surface

`POST /v1/dispater/reconciliation` is unchanged. Dollar results still come from `RevenueLeakageEngine`. Confirmed recovery from that engine remains `0.00`. The new routes are additional reads and a projection. They use the same tenant grant.

## Frozen objects

`company`, `job`, `well`, `equipment`, `crew`, `contract`, `field_ticket`, `invoice`, `rate_schedule`, `approval`, `payment`.

An identifier is `type:raw_id`. A rate schedule is not stored as a contract. A company name is null unless a future source supplies one. This projection does not invent the name.

## Frozen events and qualifiers

Events: `job_recorded`, `equipment_used`, `ticket_submitted`, `invoice_issued`, `rate_cited`, `contract_cited`, `approval_recorded`, `payment_recorded`.

Qualifiers: `concerns`, `uses`, `bills`, `governed_by`, `priced_by`, `approves`, `settles`, `assigns`, `located_at`.

The operational chain is Job, Equipment, Field Ticket, Invoice, Contract, Approval, Payment. A missing endpoint is `ENDPOINT_NOT_IN_SOURCE`. It is not created. More than one rate for the same customer and service is `NO_UNIQUE_RATE`. The log does not choose one.

Invoices and payments in the current DISPATER rows have no event date. The projection stores an empty time instead of inventing one. Payment attributes include `executed: false`.

## Findings and explanations

Existing qualifications map in one direction:

- `SUSPECTED_DISCREPANCY` → `SUSPECTED_EXPOSURE`
- `INSUFFICIENT_EVIDENCE` → `UNVERIFIED_INTERPRETATION`
- `STATUS_INCONSISTENCY` → `CALCULATED_DISCREPANCY`

`valexii.xaeli.explanation.v1` keeps observed evidence hashes, the suspected amount, the calculated amount, and confirmed recovery in separate fields. Confirmed recovery on this path is `0.00`. An explanation is built only from a stored run for the authorized tenant. No model is called.

## Approval labels

Accepted recorded labels: `PENDING_HUMAN_REVIEW`, `RECORDED_APPROVAL`, `RECORDED_REJECTION`, `WITHHELD`. The word `APPROVED` is rejected. A recorded label does not move money and does not change the finding totals.

## Tenant and effect

Every stored object, event, and relation is keyed by `tenant_id` and `dataset_sha256`. A caller authorized for a different tenant does not receive the rows. `effect` is `NONE`. Financial authority is `NONE`.

## Not in this contract

Anomaly scores, continuous connectors, and the audit dashboard are not part of v1. The advisory route `/v1/industrial-audit/readiness` is a different module and still returns its own not-verified response.
