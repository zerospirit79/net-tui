  from net_tui.backends.dns_resolved import set_global_dns, query

  def set_dns(nameservers: list[str], search: list[str] | None = None):
    set_global_dns(nameservers, search)

  def test_dns(name="example.com") -> bool:
    return query(name)
  

