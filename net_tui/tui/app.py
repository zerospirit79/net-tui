from textual.app import App, ComposeResult
from textual.widgets import Button, Static
from textual.containers import Vertical
from textual.screen import Screen

from net_tui.screens.hosts import HostsScreen
from net_tui.screens.hostname import HostnameScreen
from net_tui.screens.interfaces import InterfacesScreen
from net_tui.screens.dns import DnsScreen


class StartScreen(Screen):
    BINDINGS = [
        ("1", "open_hosts", "Hosts"),
        ("2", "open_hostname", "Hostname"),
        ("3", "open_interfaces", "Interfaces"),
        ("4", "open_dns", "DNS"),
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="start-menu"):
            yield Static("Выберите действие:", id="menu-title")
            yield Button("1. Внесение изменений в /etc/hosts", id="menu-hosts")
            yield Button("2. Изменение hostname", id="menu-hostname")
            yield Button("3. Настройка сетевых интерфейсов", id="menu-interfaces")
            yield Button("4. Настройка DNS", id="menu-dns")
            yield Button("Выход", id="menu-exit")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self._route(event.button.id)

    def action_open_hosts(self) -> None:
        self.app.push_screen("hosts")

    def action_open_hostname(self) -> None:
        self.app.push_screen("hostname")

    def action_open_interfaces(self) -> None:
        self.app.push_screen("interfaces")

    def action_open_dns(self) -> None:
        self.app.push_screen("dns")

    def action_quit(self) -> None:
        self.app.exit(0)

    def _route(self, bid: str) -> None:
        if bid == "menu-hosts":
            self.app.push_screen("hosts")
        elif bid == "menu-hostname":
            self.app.push_screen("hostname")
        elif bid == "menu-interfaces":
            self.app.push_screen("interfaces")
        elif bid == "menu-dns":
            self.app.push_screen("dns")
        elif bid == "menu-exit":
            self.app.exit(0)


class NetTuiApp(App):
    CSS = """
    #start-menu {
        padding: 1;
        height: 100%;
    }
    #menu-title {
        content-align: center middle;
        height: 3;
    }
    """

    def on_mount(self) -> None:
      self.install_screen(StartScreen(), name="start")
      self.install_screen(HostsScreen(), name="hosts")
      self.install_screen(HostnameScreen(), name="hostname")
      self.install_screen(InterfacesScreen(), name="interfaces")
      self.install_screen(DnsScreen(), name="dns")
      self.push_screen("start")
    

if __name__ == "__main__":
    NetTuiApp().run()
