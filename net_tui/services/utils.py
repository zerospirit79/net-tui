from __future__ import annotations
import subprocess
import shlex
from pathlib import Path

class CmdError(RuntimeError):
    def __init__(self, cmd: str, code: int, stdout: str, stderr: str):
        super().__init__(f"Команда завершилась с ошибкой ({code}): {cmd}\n{stderr.strip()}")
        self.cmd = cmd
        self.code = code
        self.stdout = stdout
        self.stderr = stderr

def run_cmd(cmd: str, check: bool = True, timeout: int | None = None, sudo: bool = False) -> str:
    full_cmd = f"sudo {cmd}" if sudo else cmd
    proc = subprocess.run(
        shlex.split(full_cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout
    )
    if check and proc.returncode != 0:
        raise CmdError(full_cmd, proc.returncode, proc.stdout, proc.stderr)
    return proc.stdout

def read_text_safe(path: str | Path, default: str = "") -> str:
    p = Path(path)
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return default

def write_text_safe(path: str | Path, data: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data, encoding="utf-8")