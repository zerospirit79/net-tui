from typer import Typer
  app = Typer(help="net-tui: TUI/CLI for network settings on ALT p11")

  @app.command()
  def tui():
    from net_tui.tui.app import run_tui
    run_tui()

  @app.command("iface-list")
  def iface_list():
    from net_tui.services.interfaces import list_interfaces
    for i in list_interfaces():
      print(f"{i.name}tstate={i.state}tipv4={','.join(i.ipv4)}tmethod={'dhcp' if i.dhcp_v4 else 'static'}")

  def main():
    app()

  if __name__ == "__main__":
    main()
