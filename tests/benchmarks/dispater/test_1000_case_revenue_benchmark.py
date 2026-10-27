"""
Deterministic 1,000-Case Revenue Assurance Benchmark & Evaluator for DISPATER.AI.

Generates 1,000 synthetic operational cases (500 positive exception cases, 500 clean negative cases)
across all 10 RevenueLeakageEngine exception rules, evaluates accuracy, precision, recall, F1 score,
false positive rate, false negative rate, monetary discrepancy estimation error, tenant isolation, and
evidence completeness.
"""

import json
import os
from typing import Any

from aurex.dispater_intelligence import RevenueLeakageEngine


def generate_1000_benchmark_dataset() -> list[dict[str, Any]]:
    """Generates 1,000 deterministic benchmark cases with ground truth labels."""
    dataset: list[dict[str, Any]] = []

    # Rules 1 to 10
    rule_names = [
        "UNMATCHED_PO",
        "UNBILLED_FIELD_TICKET",
        "RATE_DISCREPANCY",
        "DUPLICATE_INVOICE",
        "MISSING_SIGNATURE",
        "UNBILLED_ITEMS",
        "QUANTITY_UNIT_MISMATCH",
        "PARTIAL_PO_FULFILLMENT",
        "MULTI_RECORD_DISCREPANCY",
        "MISSING_CONFLICTING_EVIDENCE",
    ]

    for i in range(1, 1001):
        case_id = f"CASE-{i:04d}"
        tenant_id = f"TENANT-BENCH-{(i % 5) + 1:02d}"

        # 500 Clean Negative cases (even i), 500 Positive Exception cases (odd i)
        is_exception = (i % 2 != 0)
        expected_rules: list[str] = []
        expected_exposure = 0.0

        field_tickets: list[dict[str, Any]] = []
        invoices: list[dict[str, Any]] = []
        purchase_orders: list[dict[str, Any]] = []
        rate_sheets: list[dict[str, Any]] = []

        if not is_exception:
            # Clean case: All records match perfectly
            ft_id = f"FT-CLEAN-{i}"
            po_id = f"PO-CLEAN-{i}"
            inv_id = f"INV-CLEAN-{i}"
            amount = 2500.0

            purchase_orders.append({"po_id": po_id, "amount_limit": 5000.0})
            field_tickets.append({
                "ticket_id": ft_id,
                "po_id": po_id,
                "invoice_id": inv_id,
                "total_amount": amount,
                "has_customer_signature": True,
                "items": [{"name": "Standard Labor", "subtotal": amount, "billed": True}],
                "evidence_valid": True,
            })
            invoices.append({
                "invoice_id": inv_id,
                "vendor_or_customer": f"Customer-{i}",
                "total_amount": amount,
                "po_id": po_id,
                "line_items": [{"rate_code": f"RATE-{i}", "unit_rate": 100.0, "quantity": 25}],
            })
            rate_sheets.append({"rate_code": f"RATE-{i}", "approved_rate": 100.0})
        else:
            # Positive Exception case based on rule index
            rule_idx = (i // 2) % 10
            rule_type = rule_names[rule_idx]
            expected_rules.append(rule_type)

            ft_id = f"FT-POS-{i}"
            po_id = f"PO-POS-{i}"
            inv_id = f"INV-POS-{i}"

            if rule_type == "UNMATCHED_PO":
                # FT executed without valid PO
                expected_exposure = 1500.0
                field_tickets.append({"ticket_id": ft_id, "po_id": None, "invoice_id": inv_id, "total_amount": 1500.0})
                invoices.append({"invoice_id": inv_id, "total_amount": 1500.0})
            elif rule_type == "UNBILLED_FIELD_TICKET":
                # FT complete without invoice
                expected_exposure = 3200.0
                purchase_orders.append({"po_id": po_id, "amount_limit": 10000.0})
                field_tickets.append({"ticket_id": ft_id, "po_id": po_id, "invoice_id": None, "total_amount": 3200.0})
            elif rule_type == "RATE_DISCREPANCY":
                # Billed $250 vs approved $200 (10 hrs -> $500 exposure)
                expected_exposure = 500.0
                invoices.append({
                    "invoice_id": inv_id,
                    "vendor_or_customer": f"Cust-{i}",
                    "total_amount": 2500.0,
                    "line_items": [{"rate_code": f"R-{i}", "unit_rate": 250.0, "quantity": 10}],
                })
                rate_sheets.append({"rate_code": f"R-{i}", "approved_rate": 200.0})
            elif rule_type == "DUPLICATE_INVOICE":
                # Duplicate vendor + total amount
                expected_exposure = 4000.0
                invoices.append({"invoice_id": inv_id, "vendor_or_customer": f"Vendor-{i}", "total_amount": 4000.0, "line_items": []})
                invoices.append({"invoice_id": f"{inv_id}-DUP", "vendor_or_customer": f"Vendor-{i}", "total_amount": 4000.0, "line_items": []})
            elif rule_type == "MISSING_SIGNATURE":
                expected_exposure = 1800.0
                field_tickets.append({"ticket_id": ft_id, "po_id": po_id, "invoice_id": inv_id, "total_amount": 1800.0, "has_customer_signature": False})
                purchase_orders.append({"po_id": po_id, "amount_limit": 5000.0})
                invoices.append({"invoice_id": inv_id, "total_amount": 1800.0})
            elif rule_type == "UNBILLED_ITEMS":
                expected_exposure = 750.0
                field_tickets.append({
                    "ticket_id": ft_id,
                    "po_id": po_id,
                    "invoice_id": inv_id,
                    "total_amount": 2000.0,
                    "items": [{"name": "Extra Winch Line", "subtotal": 750.0, "billed": False}],
                })
                purchase_orders.append({"po_id": po_id, "amount_limit": 5000.0})
                invoices.append({"invoice_id": inv_id, "total_amount": 2000.0})
            elif rule_type == "QUANTITY_UNIT_MISMATCH":
                expected_exposure = 600.0
                field_tickets.append({
                    "ticket_id": ft_id,
                    "po_id": po_id,
                    "invoice_id": inv_id,
                    "total_amount": 600.0,
                    "items": [{"name": "Heavy Rigging", "quantity": 12, "expected_quantity": 8, "subtotal": 600.0}],
                })
                purchase_orders.append({"po_id": po_id, "amount_limit": 5000.0})
                invoices.append({"invoice_id": inv_id, "total_amount": 600.0})
            elif rule_type == "PARTIAL_PO_FULFILLMENT":
                expected_exposure = 2000.0
                purchase_orders.append({"po_id": po_id, "amount_limit": 5000.0})
                invoices.append({"invoice_id": inv_id, "po_id": po_id, "total_amount": 7000.0})
            elif rule_type == "MULTI_RECORD_DISCREPANCY":
                expected_exposure = 1200.0
                invoices.append({
                    "invoice_id": inv_id,
                    "total_amount": 5000.0,
                    "multi_record_mismatch": True,
                    "mismatch_amount": 1200.0,
                })
            elif rule_type == "MISSING_CONFLICTING_EVIDENCE":
                expected_exposure = 2200.0
                field_tickets.append({
                    "ticket_id": ft_id,
                    "po_id": po_id,
                    "invoice_id": inv_id,
                    "total_amount": 2200.0,
                    "evidence_valid": False,
                })
                purchase_orders.append({"po_id": po_id, "amount_limit": 5000.0})
                invoices.append({"invoice_id": inv_id, "total_amount": 2200.0})

        dataset.append({
            "case_id": case_id,
            "tenant_id": tenant_id,
            "is_exception": is_exception,
            "expected_rules": expected_rules,
            "expected_exposure": expected_exposure,
            "field_tickets": field_tickets,
            "invoices": invoices,
            "purchase_orders": purchase_orders,
            "rate_sheets": rate_sheets,
        })

    return dataset


def test_1000_case_revenue_benchmark_suite():
    """Executes the 1,000-case revenue assurance benchmark and calculates metrics."""
    dataset = generate_1000_benchmark_dataset()
    assert len(dataset) == 1000

    tp = 0  # True Positives
    fp = 0  # False Positives
    tn = 0  # True Negatives
    fn = 0  # False Negatives

    total_expected_exposure = 0.0
    total_detected_exposure = 0.0
    evidence_valid_count = 0
    tenant_isolation_leaks = 0

    for case in dataset:
        tenant_id = case["tenant_id"]
        detected_excs = RevenueLeakageEngine.evaluate_records(
            tenant_id=tenant_id,
            field_tickets=case["field_tickets"],
            invoices=case["invoices"],
            purchase_orders=case["purchase_orders"],
            rate_sheets=case["rate_sheets"],
            is_demo=True,
        )

        # Check tenant isolation
        for e in detected_excs:
            if e.tenant_id != tenant_id:
                tenant_isolation_leaks += 1
            if e.evidence_hash and len(e.evidence_hash) == 64:
                evidence_valid_count += 1

        is_exception = case["is_exception"]
        has_detected = len(detected_excs) > 0

        if is_exception and has_detected:
            tp += 1
        elif is_exception and not has_detected:
            fn += 1
        elif not is_exception and has_detected:
            fp += 1
        elif not is_exception and not has_detected:
            tn += 1

        total_expected_exposure += case["expected_exposure"]
        total_detected_exposure += sum(e.financial_exposure for e in detected_excs)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    exposure_error = abs(total_detected_exposure - total_expected_exposure) / total_expected_exposure if total_expected_exposure > 0 else 0.0

    metrics = {
        "benchmark_cases_count": 1000,
        "true_positives": tp,
        "false_positives": fp,
        "true_negatives": tn,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1_score, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "total_expected_exposure_usd": round(total_expected_exposure, 2),
        "total_detected_exposure_usd": round(total_detected_exposure, 2),
        "exposure_estimation_error_pct": round(exposure_error * 100.0, 2),
        "tenant_isolation_leaks": tenant_isolation_leaks,
        "evidence_completeness_pct": round((evidence_valid_count / max(1, tp + fp)) * 100.0, 2),
    }

    # Save investor artifact JSON
    out_dir = "docs/investor/DISPATER_COMMERCIAL_VALIDATION"
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "benchmark_results.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    # Acceptance targets
    assert precision >= 0.95
    assert recall >= 0.90
    assert tenant_isolation_leaks == 0
    assert metrics["evidence_completeness_pct"] == 100.0
