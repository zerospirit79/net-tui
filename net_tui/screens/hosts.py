from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import TextArea, Button, Static
from textual.containers import Vertical, Horizontal
from net_tui.services.hosts import read_hosts, write_hosts, validate_hosts

class HostsScreen(Screen):
    def compose(self) -> ComposeResult:
        content = read_hosts()
        with Vertical(id="hosts-root"):
            yield Static("/etc/hosts", id="title")
            self.editor = TextArea(text=content, id="hosts-editor")
            yield self.editor
            with Horizontal():
                yield Button("Сохранить", id="save")
                yield Button("Назад", id="back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "save":
            data = self.editor.text
            try:
                validate_hosts(data)
                write_hosts(data)
                self.app.notify("Сохранено", severity="information")
            except Exception as e:
                self.app.notify(str(e), severity="error")
        elif bid == "back":
            self.app.pop_screen()