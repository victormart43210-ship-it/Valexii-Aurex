"""AUREX: bounded synthetic company audit-preparation demonstration.

Nine typed synthetic documents -> source receipts -> Folio Index -> deterministic
reconciliation -> one explainable view. Not a financial, regulatory or tax audit.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from aurex.folio_index import Folio, FolioIndex, FolioLink, digest_of
from aurex.audit_challenge import hold_challenges

POLICY = "aurex-synthetic-company-one-spine-v1"
MAX_FILE_BYTES = 65_536
MAX_PACKET_FILES = 20
MAX_MANIFEST_BYTES = 16_384
REQUIRED = frozenset({
    "purchase_order", "invoice", "field_ticket", "payment", "bank_statement",
    "general_ledger", "tax_summary", "dot_checklist", "insurance_certificate",
})
_DOC_ID = re.compile(r"[A-Z][A-Z0-9-]{1,63}\Z")
_FILE = re.compile(r"[a-z][a-z0-9_]{0,63}\.json\Z")
_MONEY = re.compile(r"(?:0|[1-9][0-9]{0,8})\.[0-9]{2}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("duplicate JSON key rejected")
        out[k] = v
    return out


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite numeric token rejected")


def _read(path: Path, limit: int) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise ValueError("no-follow file opening unavailable")
    try:
        fd = os.open(path, flags | nofollow)
    except OSError as exc:
        raise ValueError("source unavailable or symlink refused") from exc
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("source is not a regular file")
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("source exceeds byte limit")
    return raw


def _json(raw: bytes) -> dict[str, Any]:
    try:
        obj = json.loads(
            raw.decode("utf-8", errors="strict"), object_pairs_hook=_no_duplicates,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, ValueError) as exc:
        raise ValueError("malformed UTF-8 JSON packet") from exc
    if not isinstance(obj, dict):
        raise ValueError("JSON object required")
    return obj


def _str(obj: dict[str, Any], key: str, *, pattern: re.Pattern[str] | None = None) -> str:
    v = obj.get(key)
    if not isinstance(v, str) or not v or len(v) > 128:
        raise ValueError(f"invalid {key}")
    if pattern is not None and pattern.fullmatch(v) is None:
        raise ValueError(f"invalid {key}")
    return v


def _cash(obj: dict[str, Any], key: str) -> Decimal:
    raw = _str(obj, key)
    if _MONEY.fullmatch(raw) is None:
        raise ValueError(f"invalid fixed-cent decimal {key}")
    try:
        return Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(f"invalid {key}") from exc


def _day(obj: dict[str, Any], key: str) -> date:
    raw = _str(obj, key)
    try:
        value = date.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(f"invalid ISO date {key}") from exc
    if value.isoformat() != raw:
        raise ValueError(f"noncanonical date {key}")
    return value


def _qty(obj: dict[str, Any]) -> int:
    n = obj.get("quantity")
    if type(n) is not int or not 1 <= n <= 10_000:
        raise ValueError("positive bounded integer quantity required")
    return n


def _finding(code: str, refs: tuple[str, ...], reason: str, *, observed: str = "") -> dict[str, Any]:
    return {
        "code": code, "sources": list(refs), "reason": reason,
        "observed": observed, "disposition": "HUMAN_REVIEW_REQUIRED",
        "regulatory_violation": "NOT_DETERMINED", "authority": "NONE",
    }


def run_packet(root: Path) -> dict[str, Any]:
    """Compute independently reproducible, deterministic synthetic report.

    Does not modify inputs, train a model, use a remote service or grant authority.
    """
    if not root.is_dir() or root.is_symlink():
        raise ValueError("packet root must be an existing non-symlink directory")
    manifest_bytes = _read(root / "manifest.json", MAX_MANIFEST_BYTES)
    manifest = _json(manifest_bytes)
    if manifest.get("synthetic") is not True or manifest.get("company_id") != "fictional_northstar_001":
        raise ValueError("pilot only accepts specifically labelled fictional fixture")
    if manifest.get("tenant") != "demo-tenant" or manifest.get("period") != "2026-09":
        raise ValueError("unexpected demo tenant or period")
    recorded = manifest.get("records")
    if not isinstance(recorded, list) or not 0 < len(recorded) <= MAX_PACKET_FILES:
        raise ValueError("invalid manifest record count")
    if len(recorded) != len(REQUIRED):
        raise ValueError("incomplete demo manifest")
    index = FolioIndex()
    documents: dict[str, dict[str, Any]] = {}
    receipts: list[dict[str, str]] = []
    seen_files: set[str] = set()
    seen_ids: set[str] = set()
    for entry in recorded:
        if not isinstance(entry, dict) or set(entry) != {"file", "sha256", "type", "id"}:
            raise ValueError("invalid manifest entry schema")
        name = _str(entry, "file", pattern=_FILE)
        typ = _str(entry, "type")
        rid = _str(entry, "id", pattern=_DOC_ID)
        expected_digest = _str(entry, "sha256")
        if typ not in REQUIRED or name in seen_files or rid in seen_ids or typ in documents:
            raise ValueError("duplicate or unknown record in packet")
        if not _SHA.fullmatch(expected_digest):
            raise ValueError("malformed manifest digest")
        seen_files.add(name)
        seen_ids.add(rid)
        raw = _read(root / name, MAX_FILE_BYTES)
        observed_digest = _hash(raw)
        if observed_digest != expected_digest:
            raise ValueError("packet source digest mismatch")
        doc = _json(raw)
        if (_str(doc, "type") != typ or _str(doc, "id", pattern=_DOC_ID) != rid
                or _str(doc, "company_id") != manifest["company_id"]):
            raise ValueError("source ID/type/company mismatch")
        documents[typ] = doc
        index.admit(Folio(
            accession=rid.lower(), tenant="demo-tenant", collection="demo.2026_09",
            kind="original", domain=("compliance" if typ in {"dot_checklist", "insurance_certificate"} else "finance"),
            sha256=observed_digest, captured_at="2026-10-18T00:00:00+00:00",
            visibility="private", source_date="2026-09", source_calendar="gregorian",
            facets=(typ,),
        ))
        receipts.append({"id": rid, "type": typ, "sha256": observed_digest,
                         "status": "HASH_MATCHED_INPUT_NOT_AUTHENTICATED"})
    if set(documents) != REQUIRED:
        raise ValueError("required synthetic document types missing")
    packet_names = {item.name for item in root.iterdir()}
    if packet_names != seen_files | {"manifest.json"}:
        raise ValueError("undeclared files or missing sources in packet")

    po = documents["purchase_order"]
    invoice = documents["invoice"]
    ticket = documents["field_ticket"]
    pay = documents["payment"]
    bank = documents["bank_statement"]
    ledger = documents["general_ledger"]
    tax = documents["tax_summary"]
    dot = documents["dot_checklist"]
    insurance = documents["insurance_certificate"]
    if not (
        _str(invoice, "po_id") == _str(po, "id")
        and _str(ticket, "po_id") == _str(po, "id")
        and _str(pay, "invoice_id") == _str(invoice, "id")
        and _str(bank, "payment_id") == _str(pay, "id")
        and _str(ledger, "invoice_id") == _str(invoice, "id")
        and _str(tax, "period") == "2026-09"
        and _str(ledger, "period") == "2026-09"
    ):
        raise ValueError("cross-document reference or period mismatch")
    po_total = _cash(po, "authorized_usd")
    if po_total != _qty(po) * _cash(po, "unit_rate_usd"):
        raise ValueError("PO authorization arithmetic inconsistent")
    invoice_total = _cash(invoice, "declared_total_usd")
    ticket_total = _cash(ticket, "declared_total_usd")
    payment_total = _cash(pay, "amount_usd")
    bank_total = _cash(bank, "transaction_amount_usd")
    gl_total = _cash(ledger, "expense_total_usd")
    tax_total = _cash(tax, "reported_expense_usd")
    if invoice_total != _qty(invoice) * _cash(invoice, "unit_rate_usd"):
        raise ValueError("invoice line arithmetic inconsistent")
    if ticket_total != _qty(ticket) * _cash(ticket, "unit_rate_usd"):
        raise ValueError("field-ticket line arithmetic inconsistent")

    findings: list[dict[str, Any]] = []
    if invoice_total > po_total:
        findings.append(_finding("INVOICE_EXCEEDS_PO", (invoice["id"], po["id"]),
                                 "Invoice exceeds supplied authorized PO amount",
                                 observed=f"difference_usd={invoice_total - po_total:.2f}"))
    if invoice_total != ticket_total:
        findings.append(_finding("INVOICE_VS_FIELD_TICKET", (invoice["id"], ticket["id"]),
                                 "Invoice amount differs from provided field ticket",
                                 observed=f"difference_usd={invoice_total - ticket_total:.2f}"))
    if payment_total != bank_total:
        findings.append(_finding("PAYMENT_VS_BANK_STATEMENT", (pay["id"], bank["id"]),
                                 "Payment register differs from supplied bank statement",
                                 observed=f"difference_usd={payment_total - bank_total:.2f}"))
    if gl_total != invoice_total:
        findings.append(_finding("LEDGER_VS_INVOICE", (ledger["id"], invoice["id"]),
                                 "Booked expense differs from invoice face amount",
                                 observed=f"difference_usd={invoice_total - gl_total:.2f}"))
    if tax_total != gl_total:
        findings.append(_finding("TAX_SUMMARY_VS_LEDGER", (tax["id"], ledger["id"]),
                                 "Reported tax-summary expense differs from ledger expense; account mapping requires review",
                                 observed=f"difference_usd={gl_total - tax_total:.2f}"))
    expected_inspection = _str(dot, "inspection_record_id", pattern=_DOC_ID)
    if expected_inspection not in seen_ids:
        findings.append(_finding("DOT_SUPPORT_NOT_IN_PACKET", (dot["id"],),
                                 "Referenced inspection document absent from this packet; this is not a regulatory violation finding",
                                 observed=f"missing_reference={expected_inspection}"))
    if _day(insurance, "expires_on") < _day(ticket, "service_date"):
        findings.append(_finding("INSURANCE_CERTIFICATE_EXPIRED", (insurance["id"], ticket["id"]),
                                 "Provided insurance certificate expired before documented service date; current coverage unknown"))

    relations = (
        (invoice["id"], po["id"], "interprets"),
        (ticket["id"], po["id"], "supports"),
        (pay["id"], invoice["id"], "supports"),
        (bank["id"], pay["id"], "tests"),
        (ledger["id"], invoice["id"], "interprets"),
        (tax["id"], ledger["id"], "tests"),
        (insurance["id"], ticket["id"], "tests"),
    )
    for a, b, relation in relations:
        index.relate("demo-tenant", FolioLink(
            source=a.lower(), target=b.lower(), relation=relation,
            rationale_sha256=digest_of(f"{a}|{relation}|{b}|{POLICY}".encode()),
        ))
    # Index intentionally cannot expose private records via its public read API.
    if index.list_receipts(tenant="demo-tenant"):
        raise AssertionError("private source catalog leaked through public listing")
    receipts.sort(key=lambda x: x["id"])
    findings.sort(key=lambda x: x["code"])
    report: dict[str, Any] = {
        "kind": "AUREX_SYNTHETIC_COMPANY_AUDIT_PREPARATION",
        "policy": POLICY,
        "company_id": manifest["company_id"], "tenant": "demo-tenant",
        "period": "2026-09", "synthetic": True, "visibility": "private",
        "original_manifest_sha256": _hash(manifest_bytes),
        "source_receipts": receipts, "source_count": len(receipts),
        "relations_evaluated": len(relations), "findings": findings,
        "challenge_results": hold_challenges(findings, receipts),
        "finding_count": len(findings),
        "one_view": {
            "title": "APIS PRIME · FINANCIAL EVIDENCE REVIEW",
            "tabs_added": 0,
            "now": f"{len(findings)} discrepancies or evidence gaps require review in {len(receipts)} synthetic documents",
            "changed": "NOT_COMPUTED_NO_PRIOR_PACKET",
            "next": "Obtain missing source evidence; reconcile monetary differences; request accountant/DOT/insurance specialist review",
            "why": "Deterministic cross-document comparisons using exact-decimal arithmetic and source hashes",
            "proof": {"source_count": len(receipts), "manifest_sha256": _hash(manifest_bytes),
                      "independent_verification": "NOT_VERIFIED"},
        },
        "independent_verification": "NOT_VERIFIED",
        "audit_opinion": "NONE", "irs_dot_insurance_compliance": "NOT_DETERMINED",
        "llm_training": "DISABLED", "production_authority": "HOLD",
        "spine_authority": "NONE", "external_spend_usd": 0,
    }
    report["report_sha256"] = _hash(_canonical(report))
    return report


def verify_report(root: Path, report: dict[str, Any]) -> bool:
    """Recompute full report; local integrity check, not independent witness."""
    if not isinstance(report, dict):
        return False
    claimed = report.get("report_sha256")
    payload = {k: v for k, v in report.items() if k != "report_sha256"}
    if not isinstance(claimed, str) or not _SHA.fullmatch(claimed):
        return False
    if _hash(_canonical(payload)) != claimed:
        return False
    return run_packet(root) == report
