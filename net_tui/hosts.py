from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Iterable, List, Dict, Tuple, Optional

@dataclass
class HostEntry:
    ip: str
    hosts: list[str] = field(default_factory=list)
    comment: Optional[str] = None
    raw: Optional[str] = None

def _strip_inline_comment(line: str) -> Tuple[str, Optional[str]]:
    if "#" not in line:
        return line, None
    before, _, after = line.partition("#")
    return before.rstrip(), (after.strip() or None)

def parse_hosts(text: str):
    entries = []
    for line in text.splitlines():
        raw = line
        line = line.rstrip("r")
        comment = None
        if "#" in line:
            left, right = line.split("#", 1)
            comment = right.strip() or None
        else:
            left = line
        left = left.strip()
        if not left:
            continue
        tokens = left.split()
        if not tokens:
            continue
        ip, *hosts = tokens
        entries.append({
            "ip": ip,
            "hosts": hosts,
            "comment": comment,
            "raw": raw,
        })
    return entries

def render_hosts(entries):
    lines = []
    for e in entries:
        parts = [e["ip"]]
        if e.get("hosts"):
            parts.append(" ".join(e["hosts"]))
        line = " ".join([p for p in parts if p])
        if e.get("comment"):
            line = f"{line} # {e['comment']}"
        lines.append(line)
    return "n".join(lines)
    
format_hosts = render_hosts
