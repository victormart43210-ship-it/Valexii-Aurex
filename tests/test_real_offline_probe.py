from aurex.real_offline_probe import execute_sqlite_roundtrip


def test_real_roundtrip():
    result = execute_sqlite_roundtrip({"probe": "sqlite_roundtrip_v1"})
    assert result["executed"] is True
    assert result["passed"] is True
    assert result["verification"] == "NOT VERIFIED"
