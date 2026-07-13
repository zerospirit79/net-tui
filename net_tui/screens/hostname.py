import re
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from net_tui.screens.previewapply import PreviewApplyScreen
from net_tui.services.apply import ApplyPlan
from net_tui.services.hostname import get_hostname
from net_tui.services.utils import read_text_safe

_HOSTNAME_PATH = Path("/etc/hostname")
_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-\.]{0,252}$")


class HostnameScreen(Screen):
    def compose(self) -> ComposeResult:
        current = get_hostname()
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
            current = get_hostname()
            if name == current:
                self.app.notify("Изменений нет", severity="information")
                return
            if not name or not _RE.fullmatch(name):
                self.app.notify("Некорректный hostname", severity="error")
                return
            old = read_text_safe(_HOSTNAME_PATH, default=current + "\n")
            new = name + "\n"
            plan = ApplyPlan(
                file_changes=[(str(_HOSTNAME_PATH), old, new)],
                commands=[["hostnamectl", "set-hostname", name]],
            )
            self.app.push_screen(
                PreviewApplyScreen(plan, title=f"Изменить hostname на {name}?"),
                self._on_apply_result,
            )
        elif bid == "back":
            self.app.pop_screen()

    def _on_apply_result(self, ok: bool) -> None:
        if ok:
            self.app.notify("Сохранено", severity="information")
        else:
            self.app.notify("Не удалось применить изменения", severity="error")
