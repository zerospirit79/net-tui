rom __future__ import annotations
from pathlib import Path
import re
from .utils import read_text_safe, write_text_safe

HOSTS_PATH = Path("/etc/hosts")
_HOST_RE = re.compile(r"[A-Za-z0-9\-\.]{1,253}$")

def read_hosts() -> str:
    return read_text_safe(HOSTS_PATH, default="")

def write_hosts(content: str) -> None:
    validate_hosts(content)
    write_text_safe(HOSTS_PATH, content)

def validate_hosts(content: str) -> None:
    lines = content.splitlines()
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) < 2:
            raise ValueError(f"/etc/hosts: строка {i}: ожидается 'IP host [alias...]'")
        ip = parts[0]
        if not (is_ipv4(ip) or is_ipv6(ip)):
            raise ValueError(f"/etc/hosts: строка {i}: некорректный IP '{ip}'")
        for h in parts[1:]:
            if not _HOST_RE.fullmatch(h):
                raise ValueError(f"/etc/hosts: строка {i}: некорректное имя '{h}'")

def is_ipv4(ip: str) -> bool:
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False

def is_ipv6(ip: str) -> bool:
  return ":" in ip