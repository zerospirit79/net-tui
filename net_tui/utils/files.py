import os
import shutil
import tempfile
import time
import stat


def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def _backup_dir(base="/var/backups/net-tui") -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    os.makedirs(base, exist_ok=True)
    return tempfile.mkdtemp(prefix=ts + "-", dir=base)


def make_backup(path: str, backup_root="/var/backups/net-tui") -> str:
    if not os.path.exists(path):
        return ""
    bdir = _backup_dir(backup_root)
    target = os.path.join(bdir, os.path.basename(path))
    shutil.copy2(path, target)
    return target


def write_atomic(path: str, data: str, mode=0o644, backup_root="/var/backups/net-tui") -> str:
    if os.path.islink(path):
        raise ValueError(f"Отказ от замены символической ссылки: {path}")
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    original = os.stat(path) if os.path.exists(path) else None
    backup = make_backup(path, backup_root)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-net-tui-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, stat.S_IMODE(original.st_mode) if original else mode)
        if original:
            os.chown(tmp, original.st_uid, original.st_gid)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return backup


def restore_backup(path: str, backup_path: str) -> None:
    if backup_path and os.path.exists(backup_path):
        shutil.copy2(backup_path, path)
