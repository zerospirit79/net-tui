  import psutil
  from net_tui.domain.models import InterfaceConfig
  from .utils.detect import has_nm, has_networkd

  def list_interfaces() -> list[InterfaceConfig]:
    out = []
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    for name in addrs.keys():
      state = "UP" if stats.get(name) and stats[name].isup else "DOWN"
      ipv4 = []
      for a in addrs[name]:
        if a.family.name == "AF_INET":
          mask_bits = 24 if a.netmask is None else sum(bin(int(x)).count("1") for x in a.netmask.split("."))
          ipv4.append(f"{a.address}/{mask_bits}")
      out.append(InterfaceConfig(name=name, state=state, ipv4=ipv4))
    return out

  def backend_for_config() -> str:
    if has_nm():
      return "nm"
    if has_networkd():
      return "networkd"
    return "unknown"
  

