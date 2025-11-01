from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Input, Button, Static
from textual.containers import Vertical, Horizontal
from net_tui.services.utils import read_text_safe, write_text_safe
from pathlib import Path
import re

_HOSTNAME_PATH = Path("/etc/hostname")
_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-\.]{0,252}$")

class HostnameScreen(Screen):
    def compose(self) -> ComposeResult:
        current = read_text_safe(_HOSTNAME_PATH, default="").strip()
        with Vertical(id="hostname-root"):
            yield Static("Hostname", id="title")
            self.input = Input(value=current, placeholder="новый hostname", id="hostname-input")
            yield self.input
            with Horizontal():
                yield Button("Сохранить", id="save")
                yield Button("Назад", id="back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "save":
            name = self.input.value.strip()
            if not name or not _RE.fullmatch(name):
                self.app.notify("Некорректный hostname", severity="error")
                return
            try:
                write_text_safe(_HOSTNAME_PATH, name + "\n")
                self.app.notify("Сохранено", severity="information")
            except Exception as e:
                self.app.notify(str(e), severity="error")
        elif bid == "back":
            self.app.pop_screen()
