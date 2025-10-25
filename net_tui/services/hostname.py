  import subprocess
  from net_tui.services.hosts import add_entry, list_entries

  def get_hostname() -> str:
    p = subprocess.run(["hostnamectl", "status", "--pretty"], capture_output=True, text=True)
    name = p.stdout.strip() or subprocess.run(["hostname"], capture_output=True, text=True).stdout.strip()
    return name

  def set_hostname(name: str, add_hosts: bool = False):
    subprocess.run(["hostnamectl", "set-hostname", name], check=True)
    if add_hosts:
      entries = list_entries()
      present = any(name in e.names for e in entries)
      if not present:
        add_entry("127.0.1.1", [name])

