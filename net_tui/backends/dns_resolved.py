  import subprocess

  def set_global_dns(servers: list[str], search: list[str] | None = None):
    cmd = ["resolvectl", "dns", "default", *servers]
    subprocess.run(cmd, check=True)
    if search:
      subprocess.run(["resolvectl", "domain", "default", *search], check=True)

  def query(name: str) -> bool:
    return subprocess.run(["resolvectl", "query", name], stdout=subprocess.DEVNULL).returncode == 0
  

