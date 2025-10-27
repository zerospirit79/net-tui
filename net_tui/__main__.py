from .cli import main

  @app.command()
  def tui():
    from net_tui.tui.app import run_tui
    run_tui()

  @app.command("iface-list")
  def iface_list():
    from net_tui.services.interfaces import list_interfaces
    for i in list_interfaces():
      print(f"{i.name}tstate={i.state}tipv4={','.join(i.ipv4)}tmethod={'dhcp' if i.dhcp_v4 else 'static'}")
    @app.command("hosts-add")
  def hosts_add(ip: str, names: list[str]):
    from net_tui.services.hosts import add_entry
    add_entry(ip, names)

  @app.command("hosts-del")
  def hosts_del(ip: str):
    from net_tui.services.hosts import delete_entry
    delete_entry(ip)

  @app.command("hostname-get")
  def hostname_get():
    from net_tui.services.hostname import get_hostname
    print(get_hostname())

  @app.command("hostname-set")
  def hostname_set(name: str, add_hosts: bool = False):
    from net_tui.services.hostname import set_hostname
    set_hostname(name, add_hosts)

  @app.command("dns-set")
  def dns_set(servers: list[str], search: list[str] = None):
    from net_tui.services.dns import set_dns
    set_dns(servers, search)
 
  def main():
    app()

  if __name__ == "__main__":
    import sys
    sys.exit(main())
