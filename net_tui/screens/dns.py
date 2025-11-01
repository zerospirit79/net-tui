from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import TextArea, Button, Static
from textual.containers import Vertical, Horizontal
from pathlib import Path
from net_tui.services.utils import read_text_safe, write_text_safe

_RESOLV = Path("/etc/resolv.conf")

class DnsScreen(Screen):
    def compose(self) -> ComposeResult:
        content = read_text_safe(_RESOLV, default="")
        with Vertical(id="dns-root"):
            yield Static("/etc/resolv.conf", id="title")
            self.editor = TextArea(text=content, id="dns-editor")
            yield self.editor
            with Horizontal():
                yield Button("Сохранить", id="save")
                yield Button("Назад", id="back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "save":
            try:
                write_text_safe(_RESOLV, self.editor.text)
                self.app.notify("Сохранено", severity="information")
            except Exception as e:
                self.app.notify(str(e), severity="error")
        elif bid == "back":
            self.app.pop_screen()
