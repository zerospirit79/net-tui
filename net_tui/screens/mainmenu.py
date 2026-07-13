from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Static


class MainMenuScreen(Screen):
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
