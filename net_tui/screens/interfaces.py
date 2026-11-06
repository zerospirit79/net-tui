from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Select, Static, Header, Footer
from net_tui.screens.base import SettingsScreen, field
from net_tui.services.interfaces import list_interfaces
from net_tui.services.network import static_plan


class InterfacesScreen(SettingsScreen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="page"):
            yield Static("03 / ПОДКЛЮЧЕНИЕ", classes="eyebrow")
            yield Static("Статический IPv4", classes="page-title")
            yield Static("Выберите интерфейс. Приложение определит активную службу управления сетью.", classes="subtitle")
            with VerticalScroll(classes="form"):
                interfaces = [i for i in list_interfaces() if i.name != "lo"]
                yield Select([(f"{i.name} · {i.state} · {', '.join(i.ipv4) or 'без IPv4'}", i.name) for i in interfaces],
                             prompt="Сетевой интерфейс", id="interface")
                yield from field("IPv4 / префикс", "192.168.1.10/24", "address")
                yield from field("Шлюз (необязательно)", "192.168.1.1", "gateway")
                yield from field("DNS-серверы (через пробел)", "192.168.1.10 1.1.1.1", "servers")
                yield from field("Домены поиска (необязательно)", "test5.alt", "domains")
                yield Static("Применение перезапустит управляющую службу.\nТекущее сетевое или SSH-соединение может прерваться.", classes="warning")
            with Horizontal(classes="actions"):
                yield Button("Предпросмотр", variant="primary", id="save")
                yield Button("Назад", id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            selected = self.query_one(Select).value
            if selected is Select.BLANK:
                self.app.notify("Выберите интерфейс", severity="error")
                return
            try:
                values = [self.query_one(f"#{key}", Input).value.strip()
                          for key in ("address", "gateway", "servers", "domains")]
                self.preview(static_plan(str(selected), *values), "Настройка статического IPv4")
            except Exception as exc:
                self.app.notify(str(exc), severity="error", timeout=8)
