"""Project a synthetic DISPATER dataset into an object-centric log.

The log follows OCEL 2.0 ideas: typed objects, timed events, and qualified
relationships. It is stored in SQLite. It does not invent a missing link, and
it does not change a financial finding.
"""

from __future__ import annotations

from typing import Any

from aurex.dispater_intelligence import (
    InvalidSnapshot,
    _optional_rows,
    digest,
)
from aurex.relationships.contracts import (
    APPROVAL_DISPOSITIONS,
    CONTRACT_VERSION,
    OPTIONAL_TABLES,
    object_id,
)

CHAIN = (
    ("field_ticket", "job", "concerns"),
    ("equipment", "field_ticket", "uses"),
    ("invoice", "job", "bills"),
    ("contract", "job", "governed_by"),
    ("approval", "invoice", "approves"),
    ("payment", "invoice", "settles"),
    ("job", "company", "concerns"),
    ("job", "rate_schedule", "priced_by"),
    ("crew", "job", "assigns"),
    ("job", "well", "located_at"),
)


def _rows(dataset: dict[str, Any], key: str) -> list[dict[str, str]]:
    if key not in dataset or dataset[key] in (None, []):
        return []
    return _optional_rows(dataset, key, OPTIONAL_TABLES[key])


def _add_object(
    objects: dict[str, dict[str, Any]],
    object_type: str,
    raw_id: str,
    attributes: dict[str, str | None],
    source_sha256: str,
) -> str:
    identifier = object_id(object_type, raw_id)
    objects.setdefault(
        identifier,
        {
            "object_id": identifier,
            "object_type": object_type,
            "attributes": attributes,
            "source_sha256": source_sha256,
        },
    )
    return identifier


def project(dataset: dict[str, Any], dataset_sha256: str) -> dict[str, Any]:
    """Build objects, events, and qualified links from one synthetic dataset."""
    if dataset.get("dataset_type") != "SYNTHETIC_ONLY":
        raise InvalidSnapshot("Only explicitly labeled SYNTHETIC_ONLY datasets are admitted")
    jobs = _optional_rows(dataset, "jobs", {"job_id", "customer_id", "service_code", "date"})
    invoices = _optional_rows(dataset, "invoices", {"invoice_id", "job_id", "amount", "status"})
    payments = _optional_rows(dataset, "payments", {"payment_id", "invoice_id", "amount"})
    equipment = _optional_rows(
        dataset,
        "equipment",
        {
            "ticket_id",
            "job_id",
            "equipment_id",
            "service_date",
            "billable_hours",
            "standby_hours",
            "invoiced_hours",
        },
    )
    rates = _optional_rows(
        dataset, "rates", {"rate_id", "customer_id", "service_code", "start", "end", "amount"}
    )
    companies = _rows(dataset, "companies")
    wells = _rows(dataset, "wells")
    crews = _rows(dataset, "crews")
    contracts = _rows(dataset, "contracts")
    approvals = _rows(dataset, "approvals")
    for approval in approvals:
        if approval["disposition"] not in APPROVAL_DISPOSITIONS:
            raise InvalidSnapshot("approval disposition is not a recorded review label")

    objects: dict[str, dict[str, Any]] = {}
    events: list[dict[str, Any]] = []
    relations: list[dict[str, str]] = []
    unresolved: list[dict[str, str]] = []
    known: set[str] = set()

    def relate(source: str, target: str, qualifier: str) -> None:
        if source not in known or target not in known:
            unresolved.append(
                {
                    "source_id": source,
                    "target_id": target,
                    "qualifier": qualifier,
                    "reason": "ENDPOINT_NOT_IN_SOURCE",
                }
            )
            return
        relations.append(
            {
                "source_id": source,
                "target_id": target,
                "qualifier": qualifier,
                "source_sha256": dataset_sha256,
            }
        )

    customer_company: dict[str, str] = {}
    for company in companies:
        identifier = _add_object(
            objects,
            "company",
            company["company_id"],
            {"company_id": company["company_id"], "customer_id": company["customer_id"], "name": None},
            dataset_sha256,
        )
        known.add(identifier)
        customer_company[company["customer_id"]] = identifier
    for job in jobs:
        customer = job["customer_id"]
        if customer not in customer_company:
            identifier = _add_object(
                objects,
                "company",
                customer,
                {"company_id": None, "customer_id": customer, "name": None},
                dataset_sha256,
            )
            known.add(identifier)
            customer_company[customer] = identifier
        job_identifier = _add_object(
            objects,
            "job",
            job["job_id"],
            {"job_id": job["job_id"], "customer_id": customer, "service_code": job["service_code"]},
            dataset_sha256,
        )
        known.add(job_identifier)
        events.append(
            {
                "event_id": f"job_recorded:{job['job_id']}",
                "event_type": "job_recorded",
                "event_time": job["date"],
                "object_ids": [job_identifier, customer_company[customer]],
                "qualifier": "concerns",
                "source_sha256": dataset_sha256,
            }
        )
    for rate in rates:
        identifier = _add_object(
            objects,
            "rate_schedule",
            rate["rate_id"],
            {"rate_id": rate["rate_id"], "amount": rate["amount"], "service_code": rate["service_code"]},
            dataset_sha256,
        )
        known.add(identifier)
    for row in equipment:
        ticket = _add_object(
            objects,
            "field_ticket",
            row["ticket_id"],
            {"ticket_id": row["ticket_id"], "billable_hours": row["billable_hours"]},
            dataset_sha256,
        )
        machine = _add_object(
            objects,
            "equipment",
            row["equipment_id"],
            {"equipment_id": row["equipment_id"]},
            dataset_sha256,
        )
        known.add(ticket)
        known.add(machine)
        events.append(
            {
                "event_id": f"ticket_submitted:{row['ticket_id']}",
                "event_type": "ticket_submitted",
                "event_time": row["service_date"],
                "object_ids": [ticket, machine],
                "qualifier": "uses",
                "source_sha256": dataset_sha256,
            }
        )
    for invoice in invoices:
        identifier = _add_object(
            objects,
            "invoice",
            invoice["invoice_id"],
            {
                "invoice_id": invoice["invoice_id"],
                "amount": invoice["amount"],
                "status": invoice["status"],
            },
            dataset_sha256,
        )
        known.add(identifier)
        events.append(
            {
                "event_id": f"invoice_issued:{invoice['invoice_id']}",
                "event_type": "invoice_issued",
                "event_time": "",
                "object_ids": [identifier],
                "qualifier": "bills",
                "source_sha256": dataset_sha256,
            }
        )
    for payment in payments:
        identifier = _add_object(
            objects,
            "payment",
            payment["payment_id"],
            {"payment_id": payment["payment_id"], "amount": payment["amount"], "executed": "false"},
            dataset_sha256,
        )
        known.add(identifier)
        events.append(
            {
                "event_id": f"payment_recorded:{payment['payment_id']}",
                "event_type": "payment_recorded",
                "event_time": "",
                "object_ids": [identifier],
                "qualifier": "settles",
                "source_sha256": dataset_sha256,
            }
        )
    for contract in contracts:
        identifier = _add_object(
            objects,
            "contract",
            contract["contract_id"],
            {"contract_id": contract["contract_id"]},
            dataset_sha256,
        )
        known.add(identifier)
    for approval in approvals:
        identifier = _add_object(
            objects,
            "approval",
            approval["approval_id"],
            {"approval_id": approval["approval_id"], "disposition": approval["disposition"]},
            dataset_sha256,
        )
        known.add(identifier)
        events.append(
            {
                "event_id": f"approval_recorded:{approval['approval_id']}",
                "event_type": "approval_recorded",
                "event_time": "",
                "object_ids": [identifier],
                "qualifier": "approves",
                "source_sha256": dataset_sha256,
            }
        )
    for crew in crews:
        identifier = _add_object(
            objects, "crew", crew["crew_id"], {"crew_id": crew["crew_id"]}, dataset_sha256
        )
        known.add(identifier)
    for well in wells:
        identifier = _add_object(
            objects, "well", well["well_id"], {"well_id": well["well_id"]}, dataset_sha256
        )
        known.add(identifier)

    job_ids = {object_id("job", row["job_id"]) for row in jobs}
    invoice_ids = {object_id("invoice", row["invoice_id"]) for row in invoices}
    for row in equipment:
        relate(object_id("field_ticket", row["ticket_id"]), object_id("job", row["job_id"]), "concerns")
        relate(object_id("equipment", row["equipment_id"]), object_id("field_ticket", row["ticket_id"]), "uses")
    for invoice in invoices:
        relate(object_id("invoice", invoice["invoice_id"]), object_id("job", invoice["job_id"]), "bills")
    for payment in payments:
        relate(
            object_id("payment", payment["payment_id"]),
            object_id("invoice", payment["invoice_id"]),
            "settles",
        )
    for contract in contracts:
        relate(object_id("contract", contract["contract_id"]), object_id("job", contract["job_id"]), "governed_by")
    for approval in approvals:
        relate(
            object_id("approval", approval["approval_id"]),
            object_id("invoice", approval["invoice_id"]),
            "approves",
        )
    for job in jobs:
        relate(object_id("job", job["job_id"]), customer_company[job["customer_id"]], "concerns")
    for crew in crews:
        relate(object_id("crew", crew["crew_id"]), object_id("job", crew["job_id"]), "assigns")
    for well in wells:
        relate(object_id("job", well["job_id"]), object_id("well", well["well_id"]), "located_at")

    rates_by_service: dict[tuple[str, str], list[str]] = {}
    for rate in rates:
        key = (rate["customer_id"], rate["service_code"])
        rates_by_service.setdefault(key, []).append(object_id("rate_schedule", rate["rate_id"]))
    for job in jobs:
        matches = rates_by_service.get((job["customer_id"], job["service_code"]), [])
        if len(matches) != 1:
            unresolved.append(
                {
                    "source_id": object_id("job", job["job_id"]),
                    "target_id": "",
                    "qualifier": "priced_by",
                    "reason": "NO_UNIQUE_RATE",
                }
            )
        else:
            relate(object_id("job", job["job_id"]), matches[0], "priced_by")

    ordered_objects = [objects[key] for key in sorted(objects)]
    ordered_events = sorted(events, key=lambda item: (item["event_time"], item["event_id"]))
    ordered_relations = sorted(relations, key=lambda item: (item["qualifier"], item["source_id"], item["target_id"]))
    return {
        "schema": CONTRACT_VERSION,
        "ocel": "OCEL-2.0-concepts",
        "graph_database": "NOT_USED",
        "dataset_sha256": dataset_sha256,
        "context_sha256": digest(
            {
                "companies": companies,
                "wells": wells,
                "crews": crews,
                "contracts": contracts,
                "approvals": approvals,
            }
        ),
        "objects": ordered_objects,
        "events": ordered_events,
        "relations": ordered_relations,
        "unresolved": sorted(unresolved, key=lambda item: (item["qualifier"], item["source_id"], item["target_id"])),
        "chain": [list(item) for item in CHAIN],
        "known_jobs": sorted(job_ids),
        "known_invoices": sorted(invoice_ids),
        "effect": "NONE",
        "financial_authority": "NONE",
    }
