import hashlib
import unittest
from r14.identity import IntakeAuthorizationError, TenantPrincipal, require_tenant, resolve_principal
from r14.service import register_metadata, retrieve_metadata


class FakeAdapter:
    def __init__(self):
        self.records = {}

    def register_intake(self, db_path, **kwargs):
        record = {**kwargs, 'id': 'synthetic-id', 'status': 'QUARANTINED', 'authority': 'NONE'}
        self.records[(kwargs['tenant_id'], record['id'])] = record
        return record

    def get_intake(self, db_path, *, tenant_id, record_id):
        return self.records.get((tenant_id, record_id))


class R14BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.token = 'synthetic-token-for-offline-tests-1234'
        self.mapping = {hashlib.sha256(self.token.encode()).hexdigest(): ('tenant-A', 'test-operator')}

    def test_valid_mapping(self):
        self.assertEqual(resolve_principal(presented_token=self.token, token_hash_to_tenant=self.mapping).tenant_id, 'tenant-A')

    def test_missing_or_wrong_token_denied(self):
        for token in (None, '', 'incorrect-token-long-enough'):
            with self.subTest(token=token), self.assertRaises(IntakeAuthorizationError):
                resolve_principal(presented_token=token, token_hash_to_tenant=self.mapping)

    def test_missing_mapping_denied(self):
        with self.assertRaises(IntakeAuthorizationError):
            resolve_principal(presented_token=self.token, token_hash_to_tenant={})

    def test_tenant_spoofing_denied(self):
        with self.assertRaises(IntakeAuthorizationError):
            require_tenant(TenantPrincipal('tenant-A', 'operator'), requested_tenant='tenant-B')

    def test_bridge_derives_tenant_and_scopes_retrieval(self):
        adapter = FakeAdapter()
        p = resolve_principal(presented_token=self.token, token_hash_to_tenant=self.mapping)
        record = register_metadata(adapter, ':memory:', principal=p, source_label='synthetic', content_sha256='a'*64, size_bytes=12, idempotency_key='idem')
        self.assertEqual(record['authority'], 'NONE')
        self.assertEqual(record['status'], 'QUARANTINED')
        self.assertEqual(retrieve_metadata(adapter, ':memory:', principal=p, record_id='synthetic-id'), record)
        self.assertIsNone(retrieve_metadata(adapter, ':memory:', principal=TenantPrincipal('tenant-B', 'other'), record_id='synthetic-id'))

    def test_oversized_metadata_denied(self):
        with self.assertRaises(ValueError):
            register_metadata(FakeAdapter(), ':memory:', principal=TenantPrincipal('tenant-A', 'op'), source_label='synthetic', content_sha256='a'*64, size_bytes=20*1024*1024+1, idempotency_key='idem')


if __name__ == '__main__':
    unittest.main()
