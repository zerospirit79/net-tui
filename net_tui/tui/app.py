from textual.app import App, ComposeResult
from textual.widgets import TextLog, Input, Button, Static, TextArea, Label
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive

from net_tui.services.hostname import get_hostname, get_pretty_hostname, set_hostname
from net_tui.services.hosts import read_hosts, write_hosts, validate_hosts
from net_tui.services.dns import resolved_status, set_dns_for_interface, set_dns_domain_for_interface

class TextAreaHosts(TextArea):
    """Многострочный редактор для /etc/hosts с базовым стилем."""
    dirty: bool = reactive(False)

    def watch_text(self, old: str, new: str) -> None:  # type: ignore[override]
        self.dirty = (new != old) or self.dirty

class NetTuiApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #row1, #row2, #row3, #row4, #row5 {
        height: auto;
    }
    TextLog {
        height: 1fr;
        border: tall;
    }
    Input, Button {
        margin: 1 1;
    }
    #hosts_panel {
        height: 12;
        border: round;
        margin: 1 1;
    }
    #hosts_actions {
        height: auto;
    }
    TextArea {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Network TUI", id="title")
        with Vertical(id="row1"):
            yield TextLog(id="log", highlight=False, wrap=True)
        with Horizontal(id="row2"):
            yield Input(placeholder="Новый hostname", id="hostname_input")
            yield Button("Применить hostname", id="apply_hostname")
        with Horizontal(id="row3"):
            yield Input(placeholder="Интерфейс (например, eth0)", id="if_input")
            yield Input(placeholder="DNS (через пробел, напр. 1.1.1.1 8.8.8.8)", id="dns_input")
            yield Button("Применить DNS", id="apply_dns")
        with Horizontal(id="row4"):
            yield Input(placeholder="Домены поиска (через пробел)", id="domain_input")
            yield Button("Применить домены", id="apply_domains")
        with Vertical(id="row5"):
            with Vertical(id="hosts_panel"):
                yield Label("Редактор /etc/hosts")
                yield TextAreaHosts(id="hosts_editor")
                with Horizontal(id="hosts_actions"):
                    yield Button("Сохранить /etc/hosts", id="hosts_save")
                    yield Button("Отмена изменений", id="hosts_reset")
                    yield Button("Обновить из файла", id="hosts_reload")

    def on_mount(self) -> None:
        log = self.query_one("#log", TextLog)
        log.write(f"Текущий hostname: {get_hostname()} (pretty: {get_pretty_hostname()})")
        log.write("Статус DNS (resolvectl):")
        log.write(resolved_status())
        self._load_hosts_into_editor(initial=True)

    def _load_hosts_into_editor(self, initial: bool = False) -> None:
        log = self.query_one("#log", TextLog)
        try:
            hosts_data = read_hosts()
            editor = self.query_one("#hosts_editor", TextAreaHosts)
            editor.text = hosts_data
            editor.dirty = False
            if initial:
                lines = hosts_data.strip().splitlines()
                preview = "\n".join(lines[:10]) + ("\n..." if len(lines) > 10 else "")
                log.write("/etc/hosts (первые строки):\n" + (preview or "<пусто>"))
        except Exception as e:
            log.write(f"Ошибка чтения /etc/hosts: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        log = self.query_one("#log", TextLog)
        bid = event.button.id

        if bid == "apply_hostname":
            new = self.query_one("#hostname_input", Input).value.strip()
            try:
                set_hostname(new)
                log.write(f"OK: hostname → {get_hostname()}")
            except Exception as e:
                log.write(f"Ошибка применения hostname: {e}")

        elif bid == "apply_dns":
            ifname = self.query_one("#if_input", Input).value.strip()
            servers = self.query_one("#dns_input", Input).value.strip().split()
            try:
                set_dns_for_interface(ifname, servers)
                log.write(f"OK: DNS для {ifname} → {' '.join(servers)}")
                log.write(resolved_status())
            except Exception as e:
                log.write(f"Ошибка применения DNS: {e}")

        elif bid == "apply_domains":
            ifname = self.query_one("#if_input", Input).value.strip()
            domains = self.query_one("#domain_input", Input).value.strip().split()
            try:
                set_dns_domain_for_interface(ifname, domains)
                log.write(f"OK: Домены для {ifname} → {' '.join(domains)}")
                log.write(resolved_status())
            except Exception as e:
                log.write(f"Ошибка применения доменов: {e}")

        elif bid == "hosts_save":
            editor = self.query_one("#hosts_editor", TextAreaHosts)
            data = editor.text
            try:
                validate_hosts(data)
                write_hosts(data)
                editor.dirty = False
                log.write("OK: /etc/hosts сохранён")
            except Exception as e:
                log.write(f"Ошибка сохранения /etc/hosts: {e}")

        elif bid == "hosts_reset":
            try:
                self._load_hosts_into_editor(initial=False)
                log.write("Изменения отменены")
            except Exception as e:
                log.write(f"Ошибка отката: {e}")

        elif bid == "hosts_reload":
            try:
                self._load_hosts_into_editor(initial=False)
                log.write("Загружено из /etc/hosts")
            except Exception as e:
                log.write(f"Ошибка обновления: {e}")

if __name__ == "__main__":
    NetTuiApp().run()