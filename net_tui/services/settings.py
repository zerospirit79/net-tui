"""Build reviewable system changes without modifying the running machine."""
import re
import shlex

from net_tui.services.apply import ApplyPlan
from net_tui.services.utils import read_text_safe
from net_tui.utils.validators import valid_hostname, valid_ip


def update_assignments(content: str, values: dict[str, str]) -> str:
    """Replace active shell assignments, preserving comments and unrelated settings."""
    pending = dict(values)
    lines = []
    for line in content.splitlines():
        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=", line)
        key = match.group(1) if match else None
        if key in values:
            if key in pending:
                lines.append(f"{key}={shlex.quote(pending.pop(key))}")
        else:
            lines.append(line)
    lines.extend(f"{key}={shlex.quote(value)}" for key, value in pending.items())
    return "\n".join(lines) + "\n"


def file_change(path: str, new: str) -> tuple[str, str, str]:
    return path, read_text_safe(path), new


def hostname_plan(name: str, current: str) -> ApplyPlan:
    if not valid_hostname(name) or len(name) > 64 or name.endswith('.'):
        raise ValueError("Введите корректное имя узла (до 64 символов), например dc.test5.alt")
    path = "/etc/sysconfig/network"
    return ApplyPlan(
        file_changes=[file_change("/etc/hostname", name + "\n"),
                      file_change(path, update_assignments(read_text_safe(path), {"HOSTNAME": name}))],
        commands=[["hostnamectl", "set-hostname", name]],
        rollback_commands=[["hostnamectl", "set-hostname", current]],
    )


def resolvconf_plan(servers: str, domains: str) -> ApplyPlan:
    ips, names = servers.split(), domains.split()
    if not ips or not all(valid_ip(ip) for ip in ips):
        raise ValueError("Укажите IP-адрес DNS-сервера; несколько адресов разделяйте пробелами")
    if not names or not all(valid_hostname(name) for name in names):
        raise ValueError("Укажите домен поиска, например test5.alt")
    path = "/etc/resolvconf.conf"
    text = update_assignments(read_text_safe(path), {
        "name_servers": " ".join(ips), "search_domains": " ".join(names),
    })
    return ApplyPlan(file_changes=[file_change(path, text)], commands=[["resolvconf", "-u"]],
                     rollback_commands=[["resolvconf", "-u"]])


def read_resolvconf() -> dict[str, str]:
    values = {}
    for line in read_text_safe("/etc/resolvconf.conf").splitlines():
        try:
            parts = shlex.split(line, comments=True)
        except ValueError:
            continue
        if len(parts) == 1 and "=" in parts[0]:
            key, value = parts[0].split("=", 1)
            values[key] = value
    return values
