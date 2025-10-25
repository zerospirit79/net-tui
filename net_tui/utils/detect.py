import os, subprocess

  def is_active(unit: str) -> bool:
    return subprocess.run(["systemctl", "is-active", "--quiet", unit]).returncode == 0

  def has_nm() -> bool:
    return os.path.exists("/usr/bin/nmcli") and is_active("NetworkManager")

  def has_networkd() -> bool:
    return is_active("systemd-networkd")

  def use_resolved() -> bool:
    if not is_active("systemd-resolved"):
      return False
    try:
      path = os.path.realpath("/etc/resolv.conf")
      return "systemd/resolve" in path
    except Exception:
      return False
