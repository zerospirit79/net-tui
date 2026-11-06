from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Static, Header, Footer
from net_tui.screens.base import SettingsScreen, field
from net_tui.services.hostname import get_hostname
from net_tui.services.settings import hostname_plan


class HostnameScreen(SettingsScreen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="page"):
            yield Static("02 / ИДЕНТИФИКАЦИЯ", classes="eyebrow")
            yield Static("Имя узла", classes="page-title")
            yield Static("Полное доменное имя компьютера, например dc.test5.alt.", classes="subtitle")
            with VerticalScroll(classes="form"):
                yield from field("Новое имя узла", "dc.test5.alt", "hostname-input", get_hostname())
                yield Static("Будут обновлены /etc/hostname, HOSTNAME в /etc/sysconfig/network\nи системное имя через hostnamectl set-hostname.", classes="subtitle")
            with Horizontal(classes="actions"):
                yield Button("Предпросмотр", variant="primary", id="save")
                yield Button("Назад", id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            try:
                plan = hostname_plan(self.query_one(Input).value.strip(), get_hostname())
                self.preview(plan, "Изменение имени узла")
            except (ValueError, OSError) as exc:
                self.app.notify(str(exc), severity="error")
