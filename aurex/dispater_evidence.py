"""DISPATER synthetic document inventory for possible IRS/DOT review.

Client-specific obligations must be determined by competent reviewers.
This demonstration checks *submitted example metadata only* and provides
neither audit certification nor tax, employment, or DOT legal advice.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from aurex.dispater_pilot import InvalidSnapshot, _date, digest


def assess_synthetic_readiness(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Review synthetic document-index metadata under *supplied* demo rules."""
    if not isinstance(snapshot, dict) or set(snapshot) != {
        "dataset_type", "as_of", "requirements", "documents",
    }:
        raise InvalidSnapshot("invalid readiness snapshot")
    if snapshot["dataset_type"] != "SYNTHETIC_ONLY":
        raise InvalidSnapshot("only synthetic index metadata admitted")
    as_of = _date(snapshot["as_of"])
    rules = snapshot["requirements"]
    documents = snapshot["documents"]
    if not isinstance(rules, list) or not isinstance(documents, list):
        raise InvalidSnapshot("requirements/documents must be lists")
    if len(rules) > 1000 or len(documents) > 1000:
        raise InvalidSnapshot("demo record bound exceeded")
    rule_ids: set[str] = set()
    doc_ids: set[str] = set()
    for rule in rules:
        if not isinstance(rule, dict) or set(rule) != {
            "rule_id", "domain", "subject_id", "record_class", "reviewed", "applies",
        }:
            raise InvalidSnapshot("malformed requirement")
        if not all(
            isinstance(rule[key], str) and 0 < len(rule[key]) <= 120
            for key in ("rule_id", "domain", "subject_id", "record_class")
        ):
            raise InvalidSnapshot("invalid requirement text")
        if rule["domain"] not in {"IRS", "DOT"}:
            raise InvalidSnapshot("invalid domain")
        if type(rule["reviewed"]) is not bool or type(rule["applies"]) is not bool:
            raise InvalidSnapshot("reviewed/applies must be booleans")
        if rule["rule_id"] in rule_ids:
            raise InvalidSnapshot("duplicate rule_id")
        rule_ids.add(rule["rule_id"])
    for document in documents:
        if not isinstance(document, dict) or set(document) != {
            "document_id", "rule_id", "expires_on", "copy_available",
        }:
            raise InvalidSnapshot("malformed document")
        if not all(
            isinstance(document[key], str) and 0 < len(document[key]) <= 120
            for key in ("document_id", "rule_id")
        ):
            raise InvalidSnapshot("invalid document reference")
        if not isinstance(document["expires_on"], str):
            raise InvalidSnapshot("invalid expiry")
        if document["expires_on"]:
            _date(document["expires_on"])
        if type(document["copy_available"]) is not bool:
            raise InvalidSnapshot("invalid copy available state")
        if document["document_id"] in doc_ids:
            raise InvalidSnapshot("duplicate document_id")
        doc_ids.add(document["document_id"])
        if document["rule_id"] not in rule_ids:
            raise InvalidSnapshot("orphan document rule reference")

    findings: list[dict[str, Any]] = []
    indexed = 0
    for rule in rules:
        refs = [doc for doc in documents if doc["rule_id"] == rule["rule_id"]]
        code: str | None = None
        if not rule["reviewed"]:
            code = "APPLICABILITY_UNVERIFIED"
        elif not rule["applies"]:
            continue
        elif not any(
            doc["copy_available"] and (
                not doc["expires_on"] or _date(doc["expires_on"]) >= as_of
            )
            for doc in refs
        ):
            code = "EVIDENCE_MISSING_OR_EXPIRED"
        else:
            indexed += 1
        if code:
            findings.append({
                "code": code,
                "domain": rule["domain"],
                "rule_id": rule["rule_id"],
                "subject_id": rule["subject_id"],
                "record_class": rule["record_class"],
                "rule_sha256": digest(rule),
                "document_sha256": [digest(doc) for doc in refs],
                "authority": "HUMAN_REVIEW_REQUIRED",
            })
    findings.sort(key=lambda f: (f["code"], f["rule_id"]))
    result: dict[str, Any] = {
        "schema": "dispater.synthetic.evidence-readiness.v1",
        "status": "HOLD",
        "as_of": date.isoformat(as_of),
        "snapshot_sha256": digest(snapshot),
        "indexed_demo_requirements": indexed,
        "findings": findings,
        "independent_verification": "NOT VERIFIED",
        "limits": "Supplied rules are not law. Copies and metadata are not authenticated. Missing record is not proof of a regulatory violation.",
    }
    result["self_issued_sha256"] = digest(result)
    return result
