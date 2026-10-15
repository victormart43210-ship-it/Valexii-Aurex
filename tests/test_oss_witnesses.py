import pytest

from aurex.adapters.oss_witnesses import mobsf_json_witness, Witness


def test_mobsf_invalid_expected_sha():
    with pytest.raises(ValueError):
        mobsf_json_witness({}, "not-a-sha")


def test_mobsf_report_missing_sha():
    # expected_apk_sha is valid length but report missing sha -> returns Witness with status HOLD
    expected = "a" * 64
    w = mobsf_json_witness({}, expected)
    assert isinstance(w, Witness)
    assert w.status in ("HOLD", "INSUFFICIENT", "CONTESTED")
