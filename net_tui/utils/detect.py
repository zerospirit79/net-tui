from __future__ import annotations

import subprocess
from typing import Optional


def _run(cmd: list[str], timeout: Optional[float] = 2.0) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def is_active(unit: str) -> bool:
    try:
        proc = _run(["systemctl", "is-active", unit])
    except FileNotFoundError:
        return False
    return proc.returncode == 0 and proc.stdout.strip() == "active"


def has_nmcli() -> bool:
    try:
        proc = _run(["nmcli", "--version"])
    except FileNotFoundError:
        return False
    return proc.returncode == 0


def has_networkctl() -> bool:
    try:
        proc = _run(["networkctl", "--version"])
    except FileNotFoundError:
        return False
    return proc.returncode == 0


def has_systemd() -> bool:
    try:
        proc = _run(["systemctl", "--version"])
    except FileNotFoundError:
        return False
    return proc.returncode == 0


def default_backend() -> str:
    if is_active("systemd-networkd.service"):
        return "networkd"
    if has_nmcli():
        return "nm"
    return "auto"
