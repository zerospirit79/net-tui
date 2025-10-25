  from net_tui.utils.files import write_atomic, read_file
  import subprocess
  import os

  def render_network(ifname: str, dhcp: bool, addresses: list[str], gw: str | None, dns: list[str], domains: list[str]) -> str:
    lines = ["[Match]", f"Name={ifname}", "", "[Network]"]
    if dhcp:
      lines.append("DHCP=yes")
    else:
      lines.append("DHCP=no")
      for a in addresses:
        lines.append(f"Address={a}")
      if gw:
        lines.append(f"Gateway={gw}")
      for d in dns:
        lines.append(f"DNS={d}")
      if domains:
        lines.append("Domains=" + " ".join(domains))
    return "n".join(lines) + "n"

  def write_network(ifname: str, content: str, priority: int = 10):
    path = f"/etc/systemd/network/{priority}-{ifname}.network"
    write_atomic(path, content)

  def restart_networkd():
    subprocess.run(["systemctl", "restart", "systemd-networkd"], check=True)

