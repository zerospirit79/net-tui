from __future__ import annotations
import socket
from .utils import run_cmd

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
    from .settings import hostname_plan
    from .apply import apply_plan
    plan = hostname_plan(new_hostname.strip(), get_hostname())
    if not apply_plan(plan):
        raise RuntimeError(plan.error)
