import os
import socket
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static, Header, Footer


class MainMenuScreen(Screen):
    BINDINGS = [("1", "open_hosts", "Hosts"), ("2", "open_hostname", "Имя узла"),
                ("3", "open_interfaces", "IPv4"), ("4", "open_dns", "DNS"), ("q", "quit", "Выход"),
                Binding("down", "next_item", "Выбор", key_display="↑↓"),
                Binding("up", "previous_item", "Выбор", show=False),
                Binding("right", "next_item", "Выбор", show=False),
                Binding("left", "previous_item", "Выбор", show=False),
                Binding("f10", "quit", "Выход", show=False)]

    def on_screen_resume(self) -> None:
        if self.focused is None:
            self.query_one("#menu-hosts", Button).focus()

    def action_next_item(self) -> None:
        self.focus_next()

    def action_previous_item(self) -> None:
        self.focus_previous()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="start-menu"):
            yield Static("NETWORK WORKSPACE  /  ALT LINUX", classes="eyebrow")
            yield Static("Вся сеть. В одном месте.", classes="page-title")
            yield Static("↑↓ / Tab — выбор · Enter — открыть · 1–4 — разделы", classes="subtitle")
            mode = "root · изменения доступны" if os.geteuid() == 0 else "просмотр · для применения запустите через sudo"
            yield Static(f"{socket.gethostname()}  /  {mode}", id="status", markup=False)
            with Grid(id="menu-grid"):
                for key, title, description in (
                    ("hosts", "1   Хосты и адреса", "Локальные имена и псевдонимы\n/etc/hosts"),
                    ("hostname", "2   Имя узла", "Hostname и FQDN компьютера\nhostnamectl + sysconfig"),
                    ("interfaces", "3   Статический IP", "Адрес, шлюз и DNS интерфейса\nNetworkManager · network · networkd"),
                    ("dns", "4   DNS и домен", "DNS-сервер и домен поиска для Samba\n/etc/resolvconf.conf"),
                ):
                    with Vertical(classes="card"):
                        yield Button(title, id=f"menu-{key}")
                        yield Static(description)
            yield Button("Выйти  /  Q", id="menu-exit")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        target = event.button.id.removeprefix("menu-")
        if target == "exit":
            self.app.exit()
        else:
            self.app.push_screen(target)

    def action_open_hosts(self):
        self.app.push_screen("hosts")

    def action_open_hostname(self):
        self.app.push_screen("hostname")

    def action_open_interfaces(self):
        self.app.push_screen("interfaces")

    def action_open_dns(self):
        self.app.push_screen("dns")

    def action_quit(self):
        self.app.exit()
