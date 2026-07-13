from dataclasses import dataclass, field
from typing import Callable, List, Tuple
import subprocess
import time

from net_tui.utils.files import restore_backup, write_atomic
from net_tui.utils.diff import unified_diff


@dataclass
class ApplyPlan:
    file_changes: List[Tuple[str, str, str]] = field(default_factory=list)  # (path, old, new)
    commands: List[List[str]] = field(default_factory=list)
    restart_units: List[str] = field(default_factory=list)
    verify_steps: List[Callable[[], bool]] = field(default_factory=list)
    rollback_timer_sec: int = 45


def show_diff(plan: ApplyPlan) -> str:
    chunks = []
    for path, old, new in plan.file_changes:
        chunks.append(
            f"=== {path} ===\n"
            + unified_diff(old, new, fromfile=path + ":old", tofile=path + ":new")
        )
    return "\n".join(chunks)


def apply_plan(plan: ApplyPlan) -> bool:
    backups: List[Tuple[str, str]] = []
    try:
        for path, _old, new in plan.file_changes:
            backup = write_atomic(path, new)
            if backup:
                backups.append((path, backup))
        for cmd in plan.commands:
            subprocess.run(cmd, check=True)
        for unit in plan.restart_units:
            subprocess.run(["systemctl", "restart", unit], check=True)
        ok = True
        for step in plan.verify_steps:
            if not step():
                ok = False
                break
        if not ok:
            rollback(backups)
            return False
        time.sleep(0.1)
        return True
    except Exception:
        rollback(backups)
        return False


def rollback(backups: List[Tuple[str, str]]) -> None:
    for path, backup in reversed(backups):
        restore_backup(path, backup)


def verify_connectivity() -> bool:
    if subprocess.run(
        ["ping", "-c", "1", "-W", "1", "8.8.8.8"],
        stdout=subprocess.DEVNULL,
    ).returncode != 0:
        return False
    if subprocess.run(
        ["resolvectl", "query", "example.com"],
        stdout=subprocess.DEVNULL,
    ).returncode != 0:
        return False
    return True
