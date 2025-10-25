  import subprocess

  def _run(cmd: list[str]):
    subprocess.run(cmd, check=True)

  def set_static(con_name: str, addresses: list[str], gw: str | None, dns: list[str], search: list[str] | None):
    _run(["nmcli", "con", "mod", con_name, "ipv4.method", "manual"])
    if addresses:
      _run(["nmcli", "con", "mod", con_name, "ipv4.addresses", " ".join(addresses)])
    _run(["nmcli", "con", "mod", con_name, "ipv4.gateway", gw or ""])
    _run(["nmcli", "con", "mod", con_name, "ipv4.dns", " ".join(dns) if dns else ""])
    _run(["nmcli", "con", "mod", con_name, "ipv4.dns-search", " ".join(search) if search else ""])
    _run(["nmcli", "con", "mod", con_name, "ipv4.ignore-auto-dns", "yes"])

  def set_dhcp(con_name: str):
    _run(["nmcli", "con", "mod", con_name, "ipv4.method", "auto"])
    _run(["nmcli", "con", "mod", con_name, "-ipv4.addresses", ""])
    _run(["nmcli", "con", "mod", con_name, "-ipv4.gateway", ""])
    _run(["nmcli", "con", "mod", con_name, "-ipv4.dns", ""])
    _run(["nmcli", "con", "mod", con_name, "-ipv4.dns-search", ""])

  def apply(con_name: str, ifname: str | None = None):
    if ifname:
      subprocess.run(["nmcli", "dev", "reapply", ifname], check=False)
    subprocess.run(["nmcli", "con", "up", con_name], check=True)
  

