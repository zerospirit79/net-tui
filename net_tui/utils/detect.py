from __future__ import annotations

import shutil
import subprocess
from typing import Optional


def _run(cmd: list[str], timeout: Optional[float] = 2.0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=cmd,
        returncode=0,
        stdout="",
        stderr="",
    ) if not cmd else subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def is_active(unit: str) -> bool:
    if not shutil.which("systemctl"):
        return False
    proc = _run(["systemctl", "is-active", unit])
    return proc.returncode == 0 and proc.stdout.strip() == "active"


def has_nmcli() -> bool:
    return shutil.which("nmcli") is not None


def has_networkctl() -> bool:
    return shutil.which("networkctl") is not None


def default_backend() -> str:
    if is_active("systemd-networkd.service"):
        return "networkd"
    if has_nmcli():
        return "nm"
    return "auto"

