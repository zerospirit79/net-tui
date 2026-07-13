from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from net_tui.services.apply import ApplyPlan, apply_plan, show_diff


class PreviewApplyScreen(ModalScreen[bool]):
    DEFAULT_CSS = """
    PreviewApplyScreen {
        align: center middle;
    }
    #preview-root {
        width: 90%;
        height: 90%;
        border: solid $accent;
        background: $surface;
        padding: 1;
    }
    #diff-view {
        height: 1fr;
        border: solid $primary-darken-2;
        padding: 1;
    }
    #preview-actions {
        height: auto;
        align: right middle;
        padding-top: 1;
    }
    """

    def __init__(self, plan: ApplyPlan, title: str = "Предпросмотр изменений"):
        super().__init__()
        self.plan = plan
        self.title = title

    def compose(self) -> ComposeResult:
        diff_text = show_diff(self.plan) or "(нет изменений)"
        with Vertical(id="preview-root"):
            yield Static(self.title, id="preview-title")
            with ScrollableContainer(id="diff-view"):
                yield Static(diff_text, id="diff-content")
            with Horizontal(id="preview-actions"):
                yield Button("Применить", variant="primary", id="apply")
                yield Button("Отмена", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "apply":
            self.dismiss(apply_plan(self.plan))
        else:
            self.dismiss(False)
