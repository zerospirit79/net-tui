"""Static IPv4 plans for the network managers available on ALT Linux."""
import ipaddress
from pathlib import Path
import re

from net_tui.services.apply import ApplyPlan
from net_tui.services.settings import file_change, update_assignments
from net_tui.services.utils import read_text_safe, run_cmd
from net_tui.backends.systemd_networkd import render_network
from net_tui.utils.detect import is_active
from net_tui.utils.validators import valid_hostname, valid_ip


def active_backend(ifname: str = "") -> str:
    if is_active("NetworkManager"):
        if ifname:
            managed = run_cmd(f"nmcli -g GENERAL.NM-MANAGED device show {ifname}").strip()
            if managed != "yes":
                raise ValueError("Интерфейс не управляется NetworkManager")
        return "nm"
    if is_active("network"):
        return "etcnet"
    if is_active("systemd-networkd"):
        return "networkd"
    raise ValueError("Не найден активный NetworkManager, network или systemd-networkd")


def static_plan(ifname: str, address: str, gateway: str, servers: str, domains: str,
                backend: str = "auto") -> ApplyPlan:
    if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,15}", ifname) or ifname in {".", "..", "lo"}:
        raise ValueError("Выберите сетевой интерфейс, отличный от lo")
    if "/" not in address:
        raise ValueError("Укажите IPv4 с префиксом, например 192.168.1.10/24")
    try:
        ip = ipaddress.IPv4Interface(address)
        gw = ipaddress.IPv4Address(gateway) if gateway else None
    except ValueError as exc:
        raise ValueError("Некорректный IPv4, префикс или шлюз") from exc
    if gw and gw not in ip.network:
        raise ValueError("Шлюз должен находиться в подсети интерфейса")
    dns, search = servers.split(), domains.split()
    if not all(valid_ip(value) for value in dns):
        raise ValueError("Некорректный DNS-сервер")
    if not all(valid_hostname(value) for value in search):
        raise ValueError("Некорректный домен поиска")
    backend = active_backend(ifname) if backend == "auto" else backend
    if backend == "nm":
        uuid = run_cmd(f"nmcli -g GENERAL.CON-UUID device show {ifname}").strip()
        if not re.fullmatch(r"[a-fA-F0-9-]{36}", uuid):
            raise ValueError("Для интерфейса не найден активный профиль NetworkManager")
        values = {"ipv4.method": "manual", "ipv4.addresses": str(ip),
                  "ipv4.gateway": gateway, "ipv4.dns": ",".join(dns),
                  "ipv4.dns-search": ",".join(search), "ipv4.ignore-auto-dns": "yes"}
        command, restore = ["nmcli", "con", "mod", uuid], ["nmcli", "con", "mod", uuid]
        for key, value in values.items():
            old = run_cmd(f"nmcli --escape no -g {key} con show {uuid}").strip()
            command.extend([key, value])
            restore.extend([key, old])
        return ApplyPlan(commands=[command, ["nmcli", "con", "up", uuid]],
                         rollback_commands=[restore, ["nmcli", "con", "up", uuid]],
                         restart_units=["NetworkManager"])
    if backend == "etcnet":
        root = f"/etc/net/ifaces/{ifname}"
        old_options = read_text_safe(root + "/options")
        if not old_options.strip():
            raise ValueError("Не найден профиль etcnet. Сначала создайте интерфейс в /etc/net/ifaces")
        options = update_assignments(old_options, {
            "BOOTPROTO": "static", "NM_CONTROLLED": "no", "SYSTEMD_CONTROLLED": "no",
            "DISABLED": "no", "CONFIG_IPV4": "yes",
        })
        changes = [file_change(root + "/options", options),
                   file_change(root + "/ipv4address", str(ip) + "\n"),
                   file_change(root + "/ipv4route", f"default via {gw}\n" if gw else "")]
        resolv = "".join(f"nameserver {server}\n" for server in dns)
        if search:
            resolv += "search " + " ".join(search) + "\n"
        changes.append(file_change(root + "/resolv.conf", resolv))
        return ApplyPlan(file_changes=changes, restart_units=["network"])
    if backend == "networkd":
        path = f"/etc/systemd/network/10-net-tui-{ifname}.network"
        # Earlier matching units would silently shadow this configuration.
        for directory in ("/etc/systemd/network", "/run/systemd/network", "/usr/lib/systemd/network"):
            for unit in Path(directory).glob("*.network"):
                if unit.name <= Path(path).name and str(unit) != path:
                    raise ValueError(f"Проверьте приоритет существующего профиля {unit} перед настройкой networkd")
        return ApplyPlan(file_changes=[file_change(path, render_network(
            ifname, False, [str(ip)], gateway or None, dns, search))],
            restart_units=["systemd-networkd"])
    raise ValueError("Неизвестный сетевой backend")
