from typing import Any, Dict, Iterable, List, Tuple, Union

Value = Union[str, int, float]
KV = Dict[str, Any]
Cfg = Dict[str, Any]


def _iter_values(v: Any) -> Iterable[str]:
    if v is None:
        return []
    if isinstance(v, (list, tuple, set)):
        return (str(x) for x in v)
    return [str(v)]


def _render_section(name: str, kv: KV) -> str:
    lines: List[str] = [f"[{name}]"]
    for key, val in kv.items():
        if val is None:
            continue
        for item in _iter_values(val):
            lines.append(f"{key}={item}")
    return "n".join(lines)


def generate_networkd_unit(cfg: Cfg) -> str:
    """
    Генерирует содержимое .network/.netdev/.link файла systemd-networkd
    из словаря секций.

    Пример cfg:
    {
        "Match": {"Name": "eth0"},
        "Network": {"DHCP": "yes", "DNS": ["1.1.1.1", "8.8.8.8"]},
        "Address": [
            {"Address": "192.168.1.10/24"},
            {"Address": "192.168.1.11/24"},
        ],
        "Route": [
            {"Gateway": "192.168.1.1", "Destination": "0.0.0.0/0"}
        ],
        "Link": {"RequiredForOnline": "yes"},
    }
    """
    sections: List[str] = []

    for sec_name in ("Match", "Link", "Network"):
        val = cfg.get(sec_name)
        if isinstance(val, dict):
            sections.append(_render_section(sec_name, val))

    for sec_name in ("Address", "Route"):
        val = cfg.get(sec_name)
        if isinstance(val, dict):
            sections.append(_render_section(sec_name, val))
        elif isinstance(val, (list, tuple)):
            for item in val:
                if isinstance(item, dict):
                    sections.append(_render_section(sec_name, item))

    for sec_name, val in cfg.items():
        if sec_name in ("Match", "Link", "Network", "Address", "Route"):
            continue
        if isinstance(val, dict):
            sections.append(_render_section(sec_name, val))
        elif isinstance(val, (list, tuple)):
            for item in val:
                if isinstance(item, dict):
                    sections.append(_render_section(sec_name, item))

    body = "nn".join(s for s in sections if s).strip()
    if not body.endswith("n"):
        body += "n"
    return body