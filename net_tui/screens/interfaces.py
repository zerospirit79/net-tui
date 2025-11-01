from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import TextArea, Button, Static
from textual.containers import Vertical, Horizontal
from pathlib import Path
from net_tui.services.utils import read_text_safe, write_text_safe

_INTERFACES = Path("/etc/network/interfaces")

class InterfacesScreen(Screen):
    def compose(self) -> ComposeResult:
        content = read_text_safe(_INTERFACES, default="")
        with Vertical(id="if-root"):
            yield Static("/etc/network/interfaces", id="title")
            self.editor = TextArea(text=content, id="if-editor")
            yield self.editor
            with Horizontal():
                yield Button("Сохранить", id="save")
                yield Button("Назад", id="back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "save":
            try:
                write_text_safe(_INTERFACES, self.editor.value)
                self.app.notify("Сохранено", severity="information")
            except Exception as e:
                self.app.notify(str(e), severity="error")
        elif bid == "back":
            self.app.pop_screen()
