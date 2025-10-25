  from dataclasses import dataclass
  from typing import List, Optional
  from net_tui.utils.validators import valid_ip, valid_hostname
  from net_tui.utils.files import read_file, write_atomic

  HOSTS_PATH = "/etc/hosts"
  BEGIN = "# net-tui begin"
  END = "# net-tui end"

  @dataclass
  class HostsEntry:
    ip: str
    names: List[str]
    comment: Optional[str] = None

  def parse_hosts(text: str):
    lines = text.splitlines()
    return lines

  def serialize_hosts(lines):
    return "n".join(lines) + ("n" if lines and not lines[-1].endswith("n") else "")

  def list_entries() -> list[HostsEntry]:
    text = read_file(HOSTS_PATH)
    out = []
    for ln in text.splitlines():
      s = ln.strip()
      if not s or s.startswith("#"):
        continue
      parts = s.split()
      if not parts:
        continue
      ip = parts[0]
      names = [p for p in parts[1:] if not p.startswith("#")]
      if valid_ip(ip) and all(valid_hostname(n) for n in names):
        out.append(HostsEntry(ip=ip, names=names))
    return out

  def add_entry(ip: str, names: list[str]):
    if not valid_ip(ip):
      raise ValueError("Invalid IP")
    if not names or not all(valid_hostname(n) for n in names):
      raise ValueError("Invalid hostnames")
    text = read_file(HOSTS_PATH)
    lines = text.splitlines()
    lines.append(f"{ip}t{' '.join(names)}")
    write_atomic(HOSTS_PATH, serialize_hosts(lines))

  def delete_entry(ip: str):
    text = read_file(HOSTS_PATH)
    new_lines = []
    for ln in text.splitlines():
      s = ln.strip()
      if s and not s.startswith("#") and s.split()[0] == ip:
        continue
      new_lines.append(ln)
    write_atomic(HOSTS_PATH, serialize_hosts(new_lines))
  

