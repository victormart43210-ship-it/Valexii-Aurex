import pytest

from aurex.dispater_csv import reconcile_csv
from aurex.dispater_pilot import InvalidSnapshot

INV = "invoice_id,ticket_id,service,quantity,unit_rate\n"
TIX = "ticket_id,service,quantity\n"
RATES = "service,approved_rate\ntow,100.00\n"


def codes(res):
    return [f["code"] for f in res["findings"]]


def test_clean():
    r = reconcile_csv(INV + "I1,T1,tow,1,100.00\n", TIX + "T1,tow,1\n", RATES)
    assert r["status"] == "NO_EXCEPTIONS_DETECTED"


def test_exceptions():
    inv = INV + "I1,T1,tow,2,110.00\nI1,T1,tow,2,110.00\nI2,T9,tow,1,100.00\n"
    r = reconcile_csv(inv, TIX + "T1,tow,2\nT3,tow,1\n", RATES)
    assert codes(r) == ["RATE_MISMATCH", "DUPLICATE_INVOICE_LINE", "MISSING_TICKET", "UNBILLED_TICKET"]
    assert r["findings"][0]["variance_usd"] == "20.00"
    assert r["authority"]["financial"] == "NONE"


def test_deterministic():
    a = reconcile_csv(INV, TIX, RATES)
    assert a == reconcile_csv(INV, TIX, RATES)


def test_bad_inputs():
    with pytest.raises(InvalidSnapshot):
        reconcile_csv("bad,cols\n1,2\n", TIX, RATES)
    with pytest.raises(InvalidSnapshot):
        reconcile_csv(INV + "I1,T1,tow,1,abc\n", TIX + "T1,tow,1\n", RATES)
    with pytest.raises(InvalidSnapshot):
        reconcile_csv(INV, TIX, RATES + "tow,1.00\n")
