from __future__ import annotations
from .utils import run_cmd

def resolved_status() -> str:
    try:
        return run_cmd("resolvectl status", check=True)
    except Exception as e:
        return f"Не удалось получить статус resolvectl: {e}"

def set_dns_for_interface(ifname: str, servers: list[str] | tuple[str, ...]) -> None:
    if not ifname:
        raise ValueError("Не указано имя интерфейса")
    servers = [s for s in servers if s and s.strip()]
    if not servers:
        raise ValueError("Не указаны DNS-серверы")
    cmd = "resolvectl dns " + ifname + " " + " ".join(servers)
    run_cmd(cmd, sudo=True)

def set_dns_domain_for_interface(ifname: str, domains: list[str] | tuple[str, ...]) -> None:
    domains = [d for d in domains if d and d.strip()]
    if not ifname or not domains:
        return
    cmd = "resolvectl domain " + ifname + " " + " ".join(domains)
    run_cmd(cmd, sudo=True)