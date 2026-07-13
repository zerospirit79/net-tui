from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static, TextArea

from net_tui.screens.previewapply import PreviewApplyScreen
from net_tui.services.apply import ApplyPlan
from net_tui.services.utils import read_text_safe

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
            data = self.editor.text
            old = read_text_safe(_RESOLV, default="")
            if data == old:
                self.app.notify("Изменений нет", severity="information")
                return
            plan = ApplyPlan(file_changes=[(str(_RESOLV), old, data)])
            self.app.push_screen(
                PreviewApplyScreen(plan, title="Применить изменения /etc/resolv.conf?"),
                self._on_apply_result,
            )
        elif bid == "back":
            self.app.pop_screen()

    def _on_apply_result(self, ok: bool) -> None:
        if ok:
            self.app.notify("Сохранено", severity="information")
        else:
            self.app.notify("Не удалось применить изменения", severity="error")
