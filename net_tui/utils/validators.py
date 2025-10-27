import ipaddress
import re

LABEL_RE = r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)"
HOST_RE = re.compile(rf"^{LABEL_RE}(?:.{LABEL_RE})*$")

def valid_hostname(name: str) -> bool:
    if not isinstance(name, str):
        return False
    name = name.strip().rstrip(".")
    if not name:
        return False
    if len(name) > 253:
        return False
    return HOST_RE.fullmatch(name) is not None

def valid_ip(addr: str) -> bool:
    if not isinstance(addr, str):
        return False
    addr = addr.strip()
    try:
        ipaddress.ip_address(addr)
        return True
    except ValueError:
        return False

def valid_cidr(cidr: str) -> bool:
    if not isinstance(cidr, str):
        return False
    cidr = cidr.strip()
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False