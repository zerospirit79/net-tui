import os, time, tempfile, shutil

  def read_file(path: str) -> str:
    try:
      with open(path, "r", encoding="utf-8") as f:
        return f.read()
    except FileNotFoundError:
      return ""

  def _backup_dir(base="/var/backups/net-tui") -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = os.path.join(base, ts)
    os.makedirs(path, exist_ok=True)
    return path

  def make_backup(path: str, backup_root="/var/backups/net-tui") -> str:
    if not os.path.exists(path):
      return ""
    bdir = _backup_dir(backup_root)
    target = os.path.join(bdir, os.path.basename(path))
    shutil.copy2(path, target)
    return target

  def write_atomic(path: str, data: str, mode=0o644, backup_root="/var/backups/net-tui"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    make_backup(path, backup_root)
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-net-tui-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
      f.write(data)
    os.chmod(tmp, mode)
    os.replace(tmp, path)
