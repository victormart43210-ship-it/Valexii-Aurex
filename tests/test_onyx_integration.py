"""
Unit, security, and adversarial tests for AUREX Onyx Knowledge Retrieval Adapter.
"""

from fastapi.testclient import TestClient

from aurex.api import app
from aurex.dispater_documents import DocumentIntelligenceEngine
from aurex.integrations.onyx import OnyxKnowledgeAdapter

client = TestClient(app)
AUTH_HEADER = {"Authorization": "Bearer 12345678901234567890123456789012"}


def test_onyx_adapter_health():
    adapter_unconf = OnyxKnowledgeAdapter()
    assert adapter_unconf.check_health()["status"] == "UNCONFIGURED"

    adapter_conf = OnyxKnowledgeAdapter(api_token="TOKEN-12345")
    assert adapter_conf.check_health()["status"] == "HEALTHY"


def test_onyx_indexing_and_tenant_isolated_search():
    adapter = OnyxKnowledgeAdapter(api_token="TOKEN-12345")

    # Index Tenant A document
    doc_a = (
        "ticket_id,po_id,invoice_id,total_amount,has_signature\n"
        "FT-ONYX-A1,PO-A100,INV-A100,3500.0,true"
    ).encode("utf-8")
    doc_res_a = DocumentIntelligenceEngine.process_document("TENANT-A", "DOC-A1", "field_ticket_a.csv", doc_a)
    doc_res_a.index_in_onyx(adapter)

    # Index Tenant B document
    doc_b = (
        "ticket_id,po_id,invoice_id,total_amount,has_signature\n"
        "FT-ONYX-B1,PO-B200,INV-B200,8900.0,true"
    ).encode("utf-8")
    doc_res_b = DocumentIntelligenceEngine.process_document("TENANT-B", "DOC-B1", "field_ticket_b.csv", doc_b)
    doc_res_b.index_in_onyx(adapter)

    # Tenant A searches
    res_a = adapter.search_knowledge("TENANT-A", "FT-ONYX-A1")
    assert res_a.status == "SUCCESS"
    assert res_a.fallback_used is False
    assert len(res_a.citations) >= 1
    assert res_a.citations[0].tenant_id == "TENANT-A"

    # Cross-tenant search attempt: Tenant A searches for Tenant B ticket
    res_cross = adapter.search_knowledge("TENANT-A", "FT-ONYX-B1")
    assert res_cross.fallback_used is True  # No Tenant A match -> local fallback used
    assert res_cross.citations[0].tenant_id == "TENANT-A"  # Fallback citation remains Tenant A


def test_onyx_document_deletion():
    adapter = OnyxKnowledgeAdapter(api_token="TOKEN-12345")

    doc_data = (
        "ticket_id,po_id,invoice_id,total_amount,has_signature\n"
        "FT-DEL-01,PO-DEL,INV-DEL,1200.0,true"
    ).encode("utf-8")
    doc_res = DocumentIntelligenceEngine.process_document("TENANT-DEL", "DOC-DEL-01", "del_ticket.csv", doc_data)
    doc_res.index_in_onyx(adapter)

    # Verify indexed
    res_before = adapter.search_knowledge("TENANT-DEL", "FT-DEL-01")
    assert res_before.fallback_used is False

    # Delete index
    deleted_count = adapter.delete_document_index("TENANT-DEL", "DOC-DEL-01")
    assert deleted_count >= 1

    # Verify deleted
    res_after = adapter.search_knowledge("TENANT-DEL", "FT-DEL-01")
    assert res_after.fallback_used is True


def test_onyx_api_endpoint(monkeypatch):
    monkeypatch.setenv("AUREX_SERVICE_TOKEN", "12345678901234567890123456789012")

    resp = client.get("/v1/dispater/knowledge?tenant_id=TENANT-COMMERCIAL-01&query=rate", headers=AUTH_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert "citations" in data
    assert data["tenant_id"] == "TENANT-COMMERCIAL-01"
