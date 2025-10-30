from __future__ import annotations
import socket
import re
from .utils import run_cmd

_HOST_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9\-\.]{0,62}$")

def get_hostname() -> str:
    try:
        out = run_cmd("hostnamectl --static", check=True).strip()
        return out or socket.gethostname()
    except Exception:
        return socket.gethostname()

def get_pretty_hostname() -> str:
    try:
        out = run_cmd("hostnamectl --pretty", check=True).strip()
        return out
    except Exception:
        return get_hostname()

def set_hostname(new_hostname: str) -> None:
    if not new_hostname or new_hostname.strip() == "":
        raise ValueError("Пустое имя хоста")
    if not _HOST_RE.fullmatch(new_hostname):
        raise ValueError("Недопустимое имя хоста: разрешены буквы/цифры/дефис/точка, длина ≤ 63")
    run_cmd(f"hostnamectl set-hostname {new_hostname}", sudo=True)