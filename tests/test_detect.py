import subprocess
from unittest.mock import patch

def make_cp(rc=0, out="", err=""):
    return subprocess.CompletedProcess(args=[], returncode=rc, stdout=out, stderr=err)

def test_has_nmcli_true():
    from net_tui.utils import detect
    with patch("subprocess.run", return_value=make_cp(0, "nmcli tool")):
        assert detect.has_nmcli() is True

def test_has_nmcli_false():
    from net_tui.utils import detect
    with patch("subprocess.run", return_value=make_cp(127, "", "not found")):
        assert detect.has_nmcli() is False

def test_has_systemd_true():
    from net_tui.utils import detect
    with patch("subprocess.run", return_value=make_cp(0, "systemd 255")):
        assert detect.has_systemd() is True

def test_has_systemd_false():
    from net_tui.utils import detect
    with patch("subprocess.run", return_value=make_cp(127, "", "")):
        assert detect.has_systemd() is False
