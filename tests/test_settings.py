import subprocess
from unittest.mock import patch

import pytest

from net_tui.services.settings import hostname_plan, resolvconf_plan, update_assignments
from net_tui.services.network import static_plan
from net_tui.services.hosts import validate_hosts
from net_tui.services.apply import ApplyPlan, apply_plan, show_diff
from net_tui.utils.files import write_atomic
from net_tui.utils.validators import valid_hostname


def test_hostname_updates_sysconfig_and_runtime():
    with patch("net_tui.services.settings.read_text_safe", return_value="# keep\nHOSTNAME=old\nNETWORKING=yes\n"):
        plan = hostname_plan("dc.test5.alt", "old")
    assert plan.commands == [["hostnamectl", "set-hostname", "dc.test5.alt"]]
    assert plan.rollback_commands == [["hostnamectl", "set-hostname", "old"]]
    assert plan.file_changes[0][2] == "dc.test5.alt\n"
    assert "HOSTNAME=dc.test5.alt\nNETWORKING=yes" in plan.file_changes[1][2]
    assert "hostnamectl set-hostname" in show_diff(plan)


@pytest.mark.parametrize("name", ["bad/name", "bad_name", "bad..name", "-host", "host-", "a\nHOSTNAME=bad"])
def test_reject_hostname(name):
    assert not valid_hostname(name)
    with pytest.raises(ValueError):
        hostname_plan(name, "old")


def test_resolvconf_idempotent_preserves_other_settings():
    original = '# note\nname_servers=8.8.8.8\nname_servers=1.1.1.1\nfoo=bar\n'
    with patch("net_tui.services.settings.read_text_safe", return_value=original):
        plan = resolvconf_plan("192.168.1.10", "test5.alt")
    text = plan.file_changes[0][2]
    assert text.count("name_servers=") == 1
    assert "name_servers=192.168.1.10" in text
    assert "search_domains=test5.alt" in text
    assert "# note" in text and "foo=bar" in text
    assert update_assignments(text, {"name_servers": "192.168.1.10", "search_domains": "test5.alt"}) == text
    assert plan.commands == [["resolvconf", "-u"]]


@pytest.mark.parametrize("servers, domains", [("abc", "test.alt"), ("1.1.1.1", "a;reboot"), ("", "test.alt")])
def test_reject_invalid_dns(servers, domains):
    with pytest.raises(ValueError):
        resolvconf_plan(servers, domains)


def test_hosts_inline_comments_and_ipv6():
    validate_hosts("::1 localhost # loopback\n192.168.1.2 dc.test.alt dc")
    with pytest.raises(ValueError):
        validate_hosts("not:ipv6 localhost")


def test_etcnet_static_plan_and_restart():
    with patch("net_tui.services.network.read_text_safe", return_value="TYPE=eth\nBOOTPROTO=dhcp\n"):
        plan = static_plan("eth0", "192.168.1.10/24", "192.168.1.1", "192.168.1.10", "test5.alt", "etcnet")
    files = {p: text for p, _, text in plan.file_changes}
    assert files['/etc/net/ifaces/eth0/ipv4address'] == '192.168.1.10/24\n'
    assert files['/etc/net/ifaces/eth0/ipv4route'] == 'default via 192.168.1.1\n'
    assert "BOOTPROTO=static" in files['/etc/net/ifaces/eth0/options']
    assert "TYPE=eth" in files['/etc/net/ifaces/eth0/options']
    assert plan.restart_units == ["network"]


def test_nm_uses_connection_uuid_and_records_rollback():
    uuid = "11111111-1111-1111-1111-111111111111"
    with patch("net_tui.services.network.run_cmd", side_effect=[uuid, "auto", "", "", "", "", "no"]):
        plan = static_plan("eth0", "192.168.1.10/24", "", "1.1.1.1", "test5.alt", "nm")
    assert plan.commands[0][:4] == ["nmcli", "con", "mod", uuid]
    assert "manual" in plan.commands[0]
    assert "auto" in plan.rollback_commands[0]
    assert plan.restart_units == ["NetworkManager"]


@pytest.mark.parametrize("interface, address, gateway", [
    ("../x", "192.168.1.2/24", ""), ("lo", "192.168.1.2/24", ""),
    ("eth0", "192.168.1.2", ""), ("eth0", "192.168.1.2/24", "10.0.0.1"),
    ("eth0", "::1/64", ""),
])
def test_reject_invalid_network_before_system_commands(interface, address, gateway):
    with patch("net_tui.services.network.run_cmd") as run:
        with pytest.raises(ValueError):
            static_plan(interface, address, gateway, "", "", "nm")
        run.assert_not_called()


def test_failed_apply_restores_files_removes_new_and_restarts(tmp_path):
    original, created = tmp_path / "old", tmp_path / "new"
    original.write_text("original")
    original.chmod(0o640)
    plan = ApplyPlan(file_changes=[(str(original), "original", "changed"), (str(created), "", "new")],
                     restart_units=["network"])
    def writer(path, data):
        return write_atomic(path, data, backup_root=str(tmp_path / "backups"))
    with patch("net_tui.services.apply.write_atomic", side_effect=writer), patch("net_tui.services.apply._run", side_effect=[RuntimeError("failed"), None]) as run:
        assert not apply_plan(plan)
    assert original.read_text() == "original"
    assert original.stat().st_mode & 0o777 == 0o640
    assert not created.exists()
    assert "failed" in plan.error
    assert run.call_count == 2


def test_detect_external_file_change(tmp_path):
    path = tmp_path / "config"
    path.write_text("changed elsewhere")
    plan = ApplyPlan(file_changes=[(str(path), "old", "new")])
    with patch("net_tui.services.apply._run") as run:
        assert not apply_plan(plan)
        run.assert_not_called()
    assert path.read_text() == "changed elsewhere"


def test_distinct_backup_for_same_basename(tmp_path):
    for directory in ("a", "b"):
        path = tmp_path / directory / "options"
        path.parent.mkdir()
        path.write_text(directory)
        backup = write_atomic(str(path), "new", backup_root=str(tmp_path / "backups"))
        assert __import__('pathlib').Path(backup).read_text() == directory


def test_failure_reports_stderr():
    plan = ApplyPlan(commands=[["false"]])
    with patch("net_tui.services.apply._run", side_effect=subprocess.CalledProcessError(1, ["false"], stderr="useful error")):
        assert not apply_plan(plan)
    assert "useful error" in plan.error


def test_networkd_plan():
    with patch("net_tui.services.network.Path.glob", return_value=[]):
        plan = static_plan("eth0", "192.168.1.10/24", "192.168.1.1", "1.1.1.1", "test5.alt", "networkd")
    assert plan.restart_units == ["systemd-networkd"]
    path, _, content = plan.file_changes[0]
    assert path == "/etc/systemd/network/10-net-tui-eth0.network"
    assert "Address=192.168.1.10/24" in content
    assert "Domains=test5.alt" in content


def test_atomic_refuses_symlink(tmp_path):
    target = tmp_path / "target"
    target.write_text("keep")
    link = tmp_path / "link"
    link.symlink_to(target)
    with pytest.raises(ValueError):
        write_atomic(str(link), "replace", backup_root=str(tmp_path / "backups"))
    assert target.read_text() == "keep"
    assert link.is_symlink()
