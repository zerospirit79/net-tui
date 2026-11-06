from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Static, TextArea, Header, Footer
from net_tui.screens.base import SettingsScreen
from net_tui.services.apply import ApplyPlan
from net_tui.services.hosts import read_hosts, validate_hosts


class HostsScreen(SettingsScreen):
    BINDINGS = [Binding("f3", "add_entry", "Добавить хост", priority=True)]

    def action_add_entry(self) -> None:
        self.query_one("#add", Button).press()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="page"):
            yield Static("01 / ЛОКАЛЬНЫЕ ИМЕНА", classes="eyebrow")
            yield Static("Хосты и адреса", classes="page-title")
            yield Static("Добавьте запись: IP-адрес, имя и псевдонимы через пробел.", classes="subtitle")
            yield Input(placeholder="192.168.1.10 dc.test5.alt dc", id="entry")
            yield Button("Добавить запись", id="add")
            yield TextArea(text=read_hosts(), id="hosts-editor", show_line_numbers=True, tab_behavior="focus")
            with Horizontal(classes="actions"):
                yield Button("Предпросмотр", variant="primary", id="save")
                yield Button("Назад", id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        editor = self.query_one(TextArea)
        if event.button.id == "add":
            entry = self.query_one(Input).value.strip()
            try:
                if not entry or entry.startswith("#"):
                    raise ValueError("Введите IP-адрес и имя хоста")
                validate_hosts(entry)
                editor.load_text(editor.text.rstrip("\n") + "\n" + entry + "\n")
                self.query_one(Input).value = ""
            except ValueError as exc:
                self.app.notify(str(exc), severity="error")
        elif event.button.id == "save":
            try:
                validate_hosts(editor.text)
                old = read_hosts()
                if old == editor.text:
                    self.app.notify("Изменений нет")
                    return
                self.preview(ApplyPlan(file_changes=[("/etc/hosts", old, editor.text)]), "Изменения /etc/hosts")
            except ValueError as exc:
                self.app.notify(str(exc), severity="error")
