from textual.app import App, ComposeResult
  from textual.widgets import Header, Footer, ListView, ListItem, Static

  class MainApp(App):
    CSS = ""
    def compose(self) -> ComposeResult:
      yield Header()
      yield ListView(
        ListItem(Static("Interfaces")),
        ListItem(Static("/etc/hosts")),
        ListItem(Static("Hostname")),
        ListItem(Static("DNS (systemd-resolved)")),
        ListItem(Static("Preview & Apply"))
      )
      yield Footer()

  def run_tui():
    MainApp().run()
