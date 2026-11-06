import asyncio
import os
from rich.syntax import Syntax
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Button, Static
from net_tui.services.apply import ApplyPlan, apply_plan, show_diff


class PreviewApplyScreen(ModalScreen[bool | None]):
    BINDINGS = [Binding("escape", "cancel", "Отмена"),
                Binding("f10", "cancel", "Отмена", priority=True),
                Binding("f2", "apply_changes", "Применить", priority=True)]
    DEFAULT_CSS = """
    PreviewApplyScreen { align: center middle; background: #0b1120 80%; }
    #preview-root { width: 94%; height: 92%; border: round #65dcdf; background: #101b2d; padding: 1 2; }
    #preview-title { height: auto; color: #65dcdf; text-style: bold; margin-bottom: 1; }
    #diff-view { height: 1fr; border: round #30425e; padding: 1; }
    #preview-actions { height: auto; margin-top: 1; }
    #preview-actions Button { margin-right: 2; }
    #apply-status { height: auto; color: #ffcb7d; }
    """

    def __init__(self, plan: ApplyPlan, title: str = "Предпросмотр изменений"):
        super().__init__()
        self.plan = plan
        self.preview_title = title
        self.busy = False

    def compose(self) -> ComposeResult:
        with Vertical(id="preview-root"):
            yield Static(self.preview_title, id="preview-title", markup=False)
            with ScrollableContainer(id="diff-view"):
                yield Static(Syntax(show_diff(self.plan) or "Нет изменений", "diff", theme="monokai", word_wrap=True))
            yield Static("Проверьте изменения. F2 — применить · F10 / Esc — отмена.", id="apply-status")
            with Horizontal(id="preview-actions"):
                yield Button("Применить", variant="primary", id="apply")
                yield Button("Отмена", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.busy:
            return
        if event.button.id != "apply":
            self.dismiss(None)
            return
        if os.geteuid() != 0:
            self.query_one("#apply-status", Static).update("Нужны права root. Запустите sudo net-tui tui.")
            return
        self.busy = True
        for button in self.query(Button):
            button.disabled = True
        self.query_one("#apply-status", Static).update("Применение настроек…")
        self.run_worker(self._apply(), exclusive=True)

    async def _apply(self) -> None:
        ok = await asyncio.to_thread(apply_plan, self.plan)
        self.busy = False
        if ok:
            self.dismiss(True)
        else:
            self.query_one("#apply-status", Static).update(self.plan.error)
            self.query_one("#cancel", Button).disabled = False

    def action_apply_changes(self) -> None:
        if not self.busy:
            self.query_one("#apply", Button).press()

    def action_cancel(self) -> None:
        if not self.busy:
            self.dismiss(None)
