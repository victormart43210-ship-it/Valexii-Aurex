"""No host operations: validate candidate rendering and rejection boundaries."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

RENDER = Path(__file__).resolve().parents[1] / "integrations/private-admin/render.py"
DIGEST = "sha256:" + "a" * 64


def run(*args):
    assert RENDER.exists(), "offline renderer not implemented"
    return subprocess.run([sys.executable, str(RENDER), *args], capture_output=True, text=True)


def test_candidate_requires_reviewed_image_and_specific_host_address():
    assert RENDER.exists(), "offline renderer not implemented"
    result = run("--image-digest", DIGEST, "--vpn-bind-ip", "10.0.0.10")
    assert result.returncode == 0, result.stderr
    cfg = json.loads(result.stdout)
    service = cfg["services"]["wg-easy"]
    assert service["image"] == "ghcr.io/wg-easy/wg-easy@" + DIGEST
    assert service["profiles"] == ["admin-evaluation"]
    assert service["restart"] == "no"
    assert service["ports"] == ["10.0.0.10:51820:51820/udp", "127.0.0.1:51821:51821/tcp"]
    assert service["cap_add"] == ["NET_ADMIN"]
    assert not service.get("privileged", False)
    assert service.get("network_mode") != "host"
    assert service["volumes"] == ["wireguard_state:/etc/wireguard"]
    assert not any("AUREX" in key or "PASSWORD" in key for key in service["environment"])
    assert "/var/run/docker.sock" not in result.stdout
    assert "/data" not in result.stdout


@pytest.mark.parametrize("address", ["0.0.0.0", "127.0.0.1", "::", "::1", "224.0.0.1",
                                      "169.254.1.2", "255.255.255.255", "host.example", "10.0.0.1;id"])
def test_refuses_unsafe_or_ambiguous_bind_address(address):
    result = run("--image-digest", DIGEST, "--vpn-bind-ip", address)
    assert result.returncode == 2
    assert result.stdout == ""


@pytest.mark.parametrize("digest", ["latest", "15.4.0", "sha256:abc", "sha256:" + "G" * 64,
                                     "other/image@sha256:" + "a" * 64])
def test_refuses_tags_and_malformed_image_pins(digest):
    result = run("--image-digest", digest, "--vpn-bind-ip", "10.0.0.10")
    assert result.returncode == 2
    assert result.stdout == ""


def test_missing_inputs_do_not_render_or_start_anything():
    result = run()
    assert result.returncode == 2
    assert result.stdout == ""
