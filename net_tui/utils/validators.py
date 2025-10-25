import ipaddress, re

  HOST_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")

  def valid_ip(s: str) -> bool:
    try:
      ipaddress.ip_address(s)
      return True
    except ValueError:
      return False

  def valid_cidr(s: str) -> bool:
    try:
      ipaddress.ip_network(s, strict=False)
      return True
    except ValueError:
      return False

  def valid_hostname(s: str) -> bool:
    if len(s) > 253:
      return False
    return bool(HOST_RE.match(s))
