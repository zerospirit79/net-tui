from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, List, Dict


@dataclass
class HostEntry:
    ip: str
    names: list[str]
    comment: str | None = None
    raw: str | None = None


def _strip_inline_comment(line: str) -> tuple[str, str | None]:
    if "#" not in line:
        return line, None
    before, _, after = line.partition("#")
    return before.rstrip(), after.strip() or None


def parse_hosts(text: str) -> list[dict]:
    entries: List[Dict] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        no_comment, comment = _strip_inline_comment(raw)
        parts = no_comment.split()
        if len(parts) < 2:
            # Строка без имён — пропускаем
            continue

        ip, *names = parts
        if not names:
            continue

        entry = HostEntry(ip=ip, names=names, comment=comment, raw=raw)
        entries.append(asdict(entry))

    return entries


def format_hosts(entries: Iterable[dict]) -> str:
    lines: list[str] = []
    for e in entries:
        ip = e.get("ip")
        names = e.get("names") or []
        comment = e.get("comment")
        if not ip or not names:
            continue
        base = f"{ip}t{' '.join(names)}"
        if comment:
            base = f"{base}  # {comment}"
        lines.append(base)
    return "n".join(lines) + ("n" if lines else "")
