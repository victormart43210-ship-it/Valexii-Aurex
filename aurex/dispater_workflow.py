"""DISPATER synthetic workflow and knowledge-door design witnesses.

These deterministic, offline utilities illustrate intended checks, not an
authenticated connector, a secure deployment, model training, or live RAG.
They reject non-synthetic inputs and perform NO network or payroll actions.
"""

from __future__ import annotations

from typing import Any

from aurex.dispater_pilot import InvalidSnapshot, digest

_SYSTEMS = frozenset({"crm", "documents", "dispatch", "invoicing", "payroll"})
_ACTIONS = frozenset({"read", "propose_draft", "propose_update"})
_ROLES = frozenset({"owner", "dispatcher", "bookkeeper", "viewer"})


def propose_synthetic_workflow(spec: dict[str, Any]) -> dict[str, Any]:
    """Return an evidence-bearing proposal without creating any automation."""
    fields = {
        "dataset_type", "workflow_id", "source", "target", "action",
        "object_type", "field_names", "human_approval",
    }
    if not isinstance(spec, dict) or set(spec) != fields:
        raise InvalidSnapshot("workflow contract requires exact fields")
    if spec["dataset_type"] != "SYNTHETIC_ONLY":
        raise InvalidSnapshot("workflow proposals are synthetic-only")
    if spec["source"] not in _SYSTEMS or spec["target"] not in _SYSTEMS:
        raise InvalidSnapshot("unapproved integration system")
    if spec["action"] not in _ACTIONS:
        raise InvalidSnapshot("cannot execute or approve mutations")
    if not all(isinstance(spec[k], str) and 0 < len(spec[k]) <= 80
               for k in ("workflow_id", "source", "target", "action", "object_type")):
        raise InvalidSnapshot("invalid workflow identifier or object type")
    names = spec["field_names"]
    if not isinstance(names, list) or len(names) > 40:
        raise InvalidSnapshot("expected at most 40 field names")
    if any(not isinstance(name, str) or not 0 < len(name) <= 80 for name in names):
        raise InvalidSnapshot("invalid field name")
    if len(set(names)) != len(names):
        raise InvalidSnapshot("duplicate field names")
    if any(
        term in name.casefold()
        for name in names
        for term in ("password", "secret", "token", "ssn", "social_security", "routing_number")
    ):
        raise InvalidSnapshot("sensitive field rejected in synthetic workflow")
    if type(spec["human_approval"]) is not bool:
        raise InvalidSnapshot("approval flag must be boolean")

    sensitive_target = spec["target"] in {"payroll", "invoicing"}
    writes = spec["action"] != "read"
    blockers: list[str] = ["NO_EXTERNAL_CONNECTOR_CONFIGURED"]
    if sensitive_target and writes:
        blockers.append("PAYROLL_OR_BILLING_WRITE_PROHIBITED")
    if writes and not spec["human_approval"]:
        blockers.append("HUMAN_APPROVAL_UNSPECIFIED")
    result: dict[str, Any] = {
        "schema": "dispater.synthetic.workflow.v1",
        "workflow_id": spec["workflow_id"],
        "spec_sha256": digest(spec),
        "state": "HOLD",
        "execution": "DRY_RUN_ONLY",
        "model_authority": "NONE",
        "orchestrator_options": ["Make", "Zapier", "custom reviewed adapter"],
        "blockers": blockers,
        "required_for_real_pilot": [
            "customer DPA and owner consent",
            "per-tenant identity and scoped authorization",
            "server-side secrets and connector allowlist",
            "event signatures, idempotency, retries, and audit log",
            "human approval for payroll, invoicing and irreversible changes",
            "retention/deletion policy, rollback, and independent security review",
        ],
    }
    result["self_issued_sha256"] = digest(result)
    return result


def retrieve_synthetic_knowledge(
    documents: list[dict[str, Any]], *, caller_tenant: str, role: str, query: str
) -> dict[str, Any]:
    """Deterministic document candidate search; no LLM, embedding or network.

    Caller identity MUST come from authenticated server context in a future
    product. This demo trusts supplied values and is NOT an access gateway.
    """
    if not isinstance(caller_tenant, str) or not caller_tenant or len(caller_tenant) > 80:
        raise InvalidSnapshot("invalid tenant")
    if role not in _ROLES:
        raise InvalidSnapshot("unknown role")
    if not isinstance(query, str) or not query.strip() or len(query) > 200:
        raise InvalidSnapshot("invalid query")
    if not isinstance(documents, list) or len(documents) > 200:
        raise InvalidSnapshot("too many documents")
    tokens = {word.casefold() for word in query.split() if len(word) > 2}
    matches: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for document in documents:
        if not isinstance(document, dict) or set(document) != {
            "dataset_type", "tenant", "document_id", "title", "excerpt", "allow_roles",
        }:
            raise InvalidSnapshot("invalid knowledge document")
        if document["dataset_type"] != "SYNTHETIC_ONLY":
            raise InvalidSnapshot("real knowledge documents are not admitted")
        if not all(isinstance(document[field], str) and 0 < len(document[field]) <= 120
                   for field in ("tenant", "document_id", "title")):
            raise InvalidSnapshot("invalid document identity")
        if not isinstance(document["excerpt"], str) or len(document["excerpt"]) > 2048:
            raise InvalidSnapshot("invalid synthetic excerpt")
        roles = document["allow_roles"]
        if not isinstance(roles, list) or not roles or any(
            not isinstance(r, str) or r not in _ROLES for r in roles
        ):
            raise InvalidSnapshot("invalid access roles")
        key = (document["tenant"], document["document_id"])
        if key in seen:
            raise InvalidSnapshot("duplicate tenant document id")
        seen.add(key)
        if document["tenant"] != caller_tenant or role not in roles:
            continue
        searchable = (document["title"] + " " + document["excerpt"]).casefold()
        if tokens and not any(token in searchable for token in tokens):
            continue
        matches.append({
            "document_id": document["document_id"],
            "title": document["title"],
            "excerpt": document["excerpt"],
            "synthetic_citation_sha256": digest(document),
            "authority": "UNVERIFIED_DOCUMENT_CONTENT",
        })
    matches.sort(key=lambda m: m["document_id"])
    return {
        "schema": "dispater.synthetic.knowledge.v1",
        "state": "HOLD",
        "mode": "OFFLINE_RETRIEVAL_DEMO",
        "generated_answer": None,
        "model_training_performed": False,
        "independent_security_review": "NOT RUN",
        "candidates": matches[:10],
        "limits": "Caller identity is unverified; never expose to real company data or deploy as an access control layer.",
    }
