  import subprocess, logging, shlex, os

  LOG_PATH = "/var/log/net-tui.log"
  os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
  logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

  def run(cmd: list[str], check=True):
    logging.info("run: %s", " ".join(shlex.quote(c) for c in cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    logging.info("stdout: %s", res.stdout.strip())
    if res.stderr:
      logging.info("stderr: %s", res.stderr.strip())
    if check and res.returncode != 0:
      raise subprocess.CalledProcessError(res.returncode, cmd, res.stdout, res.stderr)
    return res
  

