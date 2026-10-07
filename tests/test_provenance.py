from aurex.provenance import fingerprint


def test_fingerprint_is_order_independent_for_objects() -> None:
    assert fingerprint({"b": 2, "a": 1}) == fingerprint({"a": 1, "b": 2})


def test_fingerprint_changes_with_content() -> None:
    assert fingerprint({"a": 1}) != fingerprint({"a": 2})
