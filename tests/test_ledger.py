from aurex.experiments.ledger import EvidenceLedger


def test_ledger_append_and_verify():
    ledger = EvidenceLedger()
    e = ledger.append("test_event", {"k": "v"})
    assert e.sequence == 0
    assert ledger.verify(expected_count=1) is True
