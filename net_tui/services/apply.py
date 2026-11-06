from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable
import shlex
import subprocess

from net_tui.utils.files import restore_backup, write_atomic
from net_tui.utils.diff import unified_diff


@dataclass
class ApplyPlan:
    file_changes: list[tuple[str, str, str]] = field(default_factory=list)
    commands: list[list[str]] = field(default_factory=list)
    restart_units: list[str] = field(default_factory=list)
    verify_steps: list[Callable[[], bool]] = field(default_factory=list)
    rollback_commands: list[list[str]] = field(default_factory=list)
    error: str = ""


def show_diff(plan: ApplyPlan) -> str:
    chunks = []
    for path, old, new in plan.file_changes:
        chunks.append(f"=== {path} ===\n" + unified_diff(old, new, fromfile=path + ":old", tofile=path + ":new"))
    commands = plan.commands + [["systemctl", "restart", unit] for unit in plan.restart_units]
    if commands:
        chunks.append("Команды:\n" + "\n".join("$ " + shlex.join(cmd) for cmd in commands))
    return "\n".join(chunks)


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)


def apply_plan(plan: ApplyPlan) -> bool:
    backups: list[tuple[str, str]] = []
    plan.error = ""
    runtime_started = False
    try:
        for path, old, _new in plan.file_changes:
            current = Path(path).read_text() if Path(path).exists() else ""
            if current != old:
                raise RuntimeError(f"{path} изменился после предпросмотра. Откройте форму заново.")
        for path, _old, new in plan.file_changes:
            backup = write_atomic(path, new)
            backups.append((path, backup))
        runtime_started = True
        for cmd in plan.commands:
            _run(cmd)
        for unit in plan.restart_units:
            _run(["systemctl", "restart", unit])
        if not all(step() for step in plan.verify_steps):
            raise RuntimeError("Проверка после применения не пройдена")
        return True
    except Exception as exc:
        plan.error = str(exc)
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            plan.error += "\n" + exc.stderr.strip()
        errors = []
        for path, backup in reversed(backups):
            try:
                if backup:
                    restore_backup(path, backup)
                else:
                    Path(path).unlink(missing_ok=True)
            except Exception as restore_error:
                errors.append(str(restore_error))
        if runtime_started:
            for cmd in plan.rollback_commands + [["systemctl", "restart", unit] for unit in plan.restart_units]:
                try:
                    _run(cmd)
                except Exception as restore_error:
                    errors.append(str(restore_error))
        if errors:
            plan.error += "\nНе удалось полностью восстановить настройки: " + "; ".join(errors)
        return False
