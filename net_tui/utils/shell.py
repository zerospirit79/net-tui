import logging
import os
import shlex
import subprocess

LOG_PATH = "/var/log/net-tui.log"


def _ensure_log_dir() -> None:
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        logging.basicConfig(
            filename=LOG_PATH,
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
        )
    except OSError:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


_ensure_log_dir()


def run(cmd: list[str], check=True):
    logging.info("run: %s", " ".join(shlex.quote(c) for c in cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    logging.info("stdout: %s", res.stdout.strip())
    if res.stderr:
        logging.info("stderr: %s", res.stderr.strip())
    if check and res.returncode != 0:
        raise subprocess.CalledProcessError(res.returncode, cmd, res.stdout, res.stderr)
    return res
