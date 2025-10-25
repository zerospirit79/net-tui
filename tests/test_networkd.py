import subprocess
from unittest.mock import patch
from textwrap import dedent

def test_generate_networkd_unit_basic():
    from net_tui.networkd import generate_networkd_unit

    cfg = {
        "match": {"Name": "eth0"},
        "network": {"DHCP": "yes"},
    }
    text = generate_networkd_unit(cfg)
    assert "[Match]" in text and "Name=eth0" in text
    assert "[Network]" in text and "DHCP=yes" in text

def test_apply_networkd_configs_no_system_calls():
    from net_tui.networkd import apply_networkd_configs

    configs = {
        "/etc/systemd/network/10-eth0.network": dedent("""
            [Match]
            Name=eth0
            [Network]
            DHCP=yes
        """).strip()
    }

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout="", stderr="")
    with patch("subprocess.run", side_effect=fake_run) as run:
        ok = apply_networkd_configs(configs)
        assert ok is True
        called = " ".join(" ".join(a[0]) for a, _ in [(c.args, c.kwargs) for c in run.mock_calls if hasattr(c, "args")])
        assert "systemctl" in called

def test_generate_static_address_unit():
    from net_tui.networkd import generate_networkd_unit

    cfg = {
        "match": {"Name": "eth1"},
        "network": {"Address": ["192.168.10.5/24"], "Gateway": "192.168.10.1", "DNS": ["1.1.1.1", "8.8.8.8"]},
    }
    text = generate_networkd_unit(cfg)
    assert "Address=192.168.10.5/24" in text
    assert "Gateway=192.168.10.1" in text
    assert "DNS=1.1.1.1" in text and "DNS=8.8.8.8" in text

