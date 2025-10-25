from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Iterable, List, Dict


@dataclass
class HostEntry:
    ip: str
    hosts: list[str] = field(default_factory=list)  
    comment: str | None = None
    raw: str | None = None


def _strip_inline_comment(line: str) -> tuple[str, str | None]:
    if "#" not in line:
        return line, None
    before, _, after = line.partition("#")
    return before.rstrip(), (after.strip() or None)


def parse_hosts(text: str) -> list[dict]:
    entries: List[Dict] = []
    for raw in text.splitlines():    
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue

        no_comment, comment = _strip_inline_comment(raw)
        parts = no_comment.split()
        if len(parts) < 2:
            continue

        ip, *hosts = parts
        if not hosts:
            continue

        entry = HostEntry(ip=ip, hosts=hosts, comment=comment, raw=raw)
        entries.append(asdict(entry))

    return entries


def format_hosts(entries: Iterable[dict]) -> str:
    lines: list[str] = []
    for e in entries:
        ip = e.get("ip")
        hosts = e.get("hosts") or []
        comment = e.get("comment")
        if not ip or not hosts:
            continue
        base = f"{ip}t{' '.join(hosts)}"
        if comment:
            base = f"{base}  # {comment}"
        lines.append(base)
    return "n".join(lines) + ("n" if lines else "")
