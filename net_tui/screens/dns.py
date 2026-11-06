from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Static, Header, Footer
from net_tui.screens.base import SettingsScreen, field
from net_tui.services.settings import read_resolvconf, resolvconf_plan


class DnsScreen(SettingsScreen):
    def compose(self) -> ComposeResult:
        values = read_resolvconf()
        yield Header()
        with Vertical(classes="page"):
            yield Static("04 / РАЗРЕШЕНИЕ ИМЁН", classes="eyebrow")
            yield Static("DNS и домен Samba", classes="page-title")
            yield Static("Постоянные настройки resolvconf. Несколько значений разделяйте пробелами.", classes="subtitle")
            with VerticalScroll(classes="form"):
                yield from field("DNS-серверы / SERVERIP", "192.168.1.10", "servers", values.get("name_servers", ""))
                yield from field("Домены поиска / DOMAINNAME", "test5.alt", "domains", values.get("search_domains", ""))
                yield Static("Запишет name_servers и search_domains в /etc/resolvconf.conf\nи обновит конфигурацию командой resolvconf -u.", classes="subtitle")
            with Horizontal(classes="actions"):
                yield Button("Предпросмотр", variant="primary", id="save")
                yield Button("Назад", id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            try:
                self.preview(resolvconf_plan(self.query_one("#servers", Input).value,
                                            self.query_one("#domains", Input).value), "DNS и домен поиска")
            except (ValueError, OSError) as exc:
                self.app.notify(str(exc), severity="error")
