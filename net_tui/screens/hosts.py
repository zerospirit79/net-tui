from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static, TextArea

from net_tui.screens.previewapply import PreviewApplyScreen
from net_tui.services.apply import ApplyPlan
from net_tui.services.hosts import read_hosts, validate_hosts

HOSTS_PATH = "/etc/hosts"


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
            except Exception as e:
                self.app.notify(str(e), severity="error")
                return
            old = read_hosts()
            if data == old:
                self.app.notify("Изменений нет", severity="information")
                return
            plan = ApplyPlan(file_changes=[(str(HOSTS_PATH), old, data)])
            self.app.push_screen(
                PreviewApplyScreen(plan, title="Применить изменения /etc/hosts?"),
                self._on_apply_result,
            )
        elif bid == "back":
            self.app.pop_screen()

    def _on_apply_result(self, ok: bool) -> None:
        if ok:
            self.app.notify("Сохранено", severity="information")
        else:
            self.app.notify("Не удалось применить изменения", severity="error")
