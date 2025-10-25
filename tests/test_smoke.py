def test_import_package():
    import net_tui
    assert hasattr(net_tui, "__version__")

def test_cli_help_runs():
    import subprocess, sys
    # Проверяем, что CLI импортируется и показывает помощь
    p = subprocess.run([sys.executable, "-m", "net_tui", "--help"], capture_output=True, text=True)
    assert p.returncode == 0
    assert "net-tui" in p.stdout.lower()

def test_utils_validators():
    from net_tui.utils.validators import valid_ip, valid_hostname, valid_cidr
    assert valid_ip("127.0.0.1")
    assert not valid_ip("999.999.1.1")
    assert valid_hostname("example.com")
    assert not valid_hostname("-bad-")
    assert valid_cidr("192.168.1.0/24")
