from typing import Any, Dict, Iterable, List, Union

Value = Union[str, int, float]
KV = Dict[str, Any]
Cfg = Dict[str, Any]

SECTION_CANON = {
    "match": "Match",
    "network": "Network",
    "address": "Address",
    "route": "Route",
    "link": "Link",
}

def _canon_section(name: str) -> str:
    if not isinstance(name, str) or not name:
        return str(name)
    lower = name.lower()
    return SECTION_CANON.get(lower, name[:1].upper() + name[1:])

def _iter_values(v: Any) -> Iterable[str]:
    if v is None:
        return []
    if isinstance(v, (list, tuple, set)):
        for item in v:
            if item is None:
                continue
            yield str(item)
        return
    yield str(v)

def _render_section(name: str, kv: KV) -> str:
    lines: List[str] = [f"[{_canon_section(name)}]"]
    for key, val in kv.items():
        if val is None:
            continue
        for item in _iter_values(val):
            lines.append(f"{key}={item}")
    return "n".join(lines)

def generate_networkd_unit(cfg: Cfg) -> str:
    sections: List[str] = []

    for sec in ("match", "link", "network"):
        val = cfg.get(sec)
        if val is None:
            val = cfg.get(sec.capitalize())
        if isinstance(val, dict):
            sections.append(_render_section(sec, val))

    for sec in ("address", "route"):
        val = cfg.get(sec) or cfg.get(sec.capitalize())
        if isinstance(val, dict):
            sections.append(_render_section(sec, val))
        elif isinstance(val, (list, tuple)):
            for item in val:
                if isinstance(item, dict):
                    sections.append(_render_section(sec, item))

    handled = {"match", "link", "network", "address", "route",
               "Match", "Link", "Network", "Address", "Route"}
    for sec_name, val in cfg.items():
        if sec_name in handled or sec_name.lower() in handled:
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