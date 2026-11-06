from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import Button


class SettingsScreen(Screen):
    AUTO_FOCUS = "Input, Select, TextArea"
    BINDINGS = [
        Binding("tab", "next_field", "Поля"),
        Binding("shift+tab", "previous_field", "Предыдущее поле", show=False),
        Binding("f2", "preview_changes", "Предпросмотр", priority=True),
        Binding("f10", "back", "Назад", priority=True),
        Binding("escape", "back", "Назад", show=False),
    ]

    def action_next_field(self) -> None:
        self.focus_next()

    def action_previous_field(self) -> None:
        self.focus_previous()

    def action_preview_changes(self) -> None:
        self.query_one("#save", Button).press()

    def action_back(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Textual dispatches handlers along the class hierarchy automatically.
        # Forms must not call this handler explicitly with super().
        if event.button.id == "back":
            event.stop()
            self.action_back()

    def preview(self, plan, title: str) -> None:
        from net_tui.screens.previewapply import PreviewApplyScreen
        self.app.push_screen(PreviewApplyScreen(plan, title), self._on_apply_result)

    def _on_apply_result(self, ok: bool | None) -> None:
        if ok:
            self.app.notify("Настройки успешно применены", title="Готово")


def field(label, placeholder, id, value=""):
    from textual.widgets import Input, Label
    yield Label(label)
    yield Input(value=value, placeholder=placeholder, id=id)
