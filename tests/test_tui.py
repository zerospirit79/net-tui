import asyncio
from unittest.mock import patch

import pytest
from textual.widgets import Input, TextArea, Button

from net_tui.tui.app import NetTuiApp
from net_tui.screens.previewapply import PreviewApplyScreen
from net_tui.domain.models import InterfaceConfig


@pytest.mark.parametrize("size", [(80, 24), (120, 40)])
def test_navigation_and_forms(size):
    async def scenario():
        app = NetTuiApp()
        with patch("net_tui.screens.hostname.get_hostname", return_value="old.test.alt"), \
             patch("net_tui.screens.mainmenu.socket.gethostname", return_value="demo.test.alt"), \
             patch("net_tui.screens.hosts.read_hosts", return_value="127.0.0.1 localhost\n"), \
             patch("net_tui.screens.interfaces.list_interfaces", return_value=[InterfaceConfig("eth0", "UP", ipv4=["192.168.1.10/24"])]), \
             patch("net_tui.services.settings.read_text_safe", return_value=""), \
             patch("net_tui.screens.previewapply.os.geteuid", return_value=1000):
            async with app.run_test(size=size) as pilot:
                for number, selector in [("1", "#hosts-editor"), ("2", "#hostname-input"), ("3", "#interface"), ("4", "#servers")]:
                    await pilot.press(number)
                    await pilot.pause()
                    assert app.screen.query_one(selector).region.width > 0
                    assert app.screen.query_one("#save", Button).region.bottom <= size[1]
                    if number == "1":
                        app.screen.query_one(Input).value = "192.168.1.10 dc.test5.alt dc"
                        await pilot.click("#add")
                        assert "dc.test5.alt" in app.screen.query_one(TextArea).text
                        await pilot.click("#save")
                        await pilot.pause()
                        assert isinstance(app.screen, PreviewApplyScreen)
                        await pilot.click("#apply")
                        assert "root" in str(app.screen.query_one("#apply-status").render())
                        await pilot.press("escape")
                        assert "dc.test5.alt" in app.screen.query_one(TextArea).text
                    if number == "2":
                        app.screen.query_one(Input).value = "dc.test5.alt"
                        await pilot.click("#save")
                        assert isinstance(app.screen, PreviewApplyScreen)
                        assert app.screen.plan.commands[0] == ["hostnamectl", "set-hostname", "dc.test5.alt"]
                        await pilot.press("escape")
                        assert app.screen.query_one(Input).value == "dc.test5.alt"
                    if number == "4":
                        app.screen.query_one("#servers", Input).value = "192.168.1.10"
                        app.screen.query_one("#domains", Input).value = "test5.alt"
                        await pilot.click("#save")
                        assert isinstance(app.screen, PreviewApplyScreen)
                        assert app.screen.plan.file_changes[0][0] == "/etc/resolvconf.conf"
                        await pilot.press("escape")
                    await pilot.press("escape")
                    await pilot.pause()
                    assert app.screen.query_one("#menu-grid")
    asyncio.run(scenario())


@pytest.mark.parametrize("method", ["click", "enter", "escape", "f10"])
def test_back_returns_to_menu_once(method):
    async def scenario():
        app = NetTuiApp()
        with patch("net_tui.screens.hostname.get_hostname", return_value="old.test.alt"), \
             patch("net_tui.screens.hosts.read_hosts", return_value="127.0.0.1 localhost\n"), \
             patch("net_tui.screens.interfaces.list_interfaces", return_value=[InterfaceConfig("eth0", "UP")]), \
             patch("net_tui.services.settings.read_text_safe", return_value=""):
            async with app.run_test(size=(80, 24)) as pilot:
                menu = app.screen
                for _ in range(2):
                    for number in ("1", "2", "3", "4"):
                        await pilot.press(number)
                        await pilot.pause()
                        if method == "click":
                            await pilot.click("#back")
                        elif method == "enter":
                            app.screen.query_one("#back", Button).focus()
                            await pilot.press("enter")
                        else:
                            await pilot.press(method)
                        await pilot.pause()
                        assert app.screen is menu
                        assert len(app.screen_stack) == 2
                        assert app.screen.query_one("#menu-hosts", Button).visible
    asyncio.run(scenario())


@pytest.mark.parametrize("size", [(80, 24), (120, 40)])
def test_keyboard_only_workflow(size):
    from textual.widgets import Select
    from net_tui.services.apply import ApplyPlan

    async def type_text(pilot, text):
        await pilot.press(*text)

    async def apply_in_test(function, *args):
        # System effects are mocked; keep the UI test independent of executor shutdown.
        return function(*args)

    async def scenario():
        app = NetTuiApp()
        with patch("net_tui.screens.hostname.get_hostname", return_value="old.test.alt"), \
             patch("net_tui.screens.hosts.read_hosts", return_value="127.0.0.1 localhost\n"), \
             patch("net_tui.screens.interfaces.list_interfaces", return_value=[InterfaceConfig("eth0", "UP")]), \
             patch("net_tui.services.settings.read_text_safe", return_value=""), \
             patch("net_tui.screens.previewapply.os.geteuid", return_value=0), \
             patch("net_tui.screens.previewapply.apply_plan", return_value=True) as apply, \
             patch.object(app, "notify") as notify, \
             patch("net_tui.screens.previewapply.asyncio.to_thread", side_effect=apply_in_test), \
             patch("net_tui.screens.interfaces.static_plan", return_value=ApplyPlan()) as network:
            async with app.run_test(size=size) as pilot:
                menu = app.screen
                # Arrow selection and Enter work without clicking or setting focus.
                await pilot.press("down", "enter")
                assert app.screen.query_one("#hostname-input", Input).has_focus
                await pilot.press("home", "ctrl+k")
                await type_text(pilot, "dc.test5.alt")
                await pilot.press("f2")
                assert isinstance(app.screen, PreviewApplyScreen)
                await pilot.press("f10")
                assert app.screen.query_one(Input).value == "dc.test5.alt"
                await pilot.press("f10")
                assert app.screen is menu

                await pilot.press("1")
                await type_text(pilot, "192.168.1.10 dc.test5.alt dc")
                await pilot.press("f3")
                await pilot.pause()
                assert "dc.test5.alt" in app.screen.query_one(TextArea).text
                await pilot.press("tab", "tab")
                assert app.screen.query_one(TextArea).has_focus
                await pilot.press("tab")
                assert app.screen.query_one("#save", Button).has_focus
                await pilot.press("enter")
                assert isinstance(app.screen, PreviewApplyScreen)
                await pilot.press("escape", "f10")
                assert app.screen is menu

                await pilot.press("3", "enter", "down", "enter")
                assert app.screen.query_one(Select).value == "eth0"
                for value in ("192.168.1.10/24", "192.168.1.1", "192.168.1.10", "test5.alt"):
                    await pilot.press("tab")
                    await type_text(pilot, value)
                await pilot.press("f2")
                network.assert_called_once_with("eth0", "192.168.1.10/24", "192.168.1.1", "192.168.1.10", "test5.alt")
                assert isinstance(app.screen, PreviewApplyScreen)
                await pilot.press("f10", "f10")
                assert app.screen is menu

                await pilot.press("4")
                await type_text(pilot, "192.168.1.10")
                await pilot.press("tab")
                await type_text(pilot, "test5.alt")
                await pilot.press("f2")
                assert isinstance(app.screen, PreviewApplyScreen)
                await pilot.press("f2")
                await app.workers.wait_for_complete()
                await pilot.pause()
                apply.assert_called_once()
                notify.assert_called_once_with("Настройки успешно применены", title="Готово")
                assert app.screen.query_one("#servers", Input).value == "192.168.1.10"
                await pilot.press("f10")
                assert app.screen is menu
                await pilot.pause()
    asyncio.run(scenario())


def test_server_cli_disables_mouse():
    from typer.testing import CliRunner
    from net_tui.cli import app
    with patch("net_tui.tui.NetTuiApp.run") as run:
        result = CliRunner().invoke(app, ["tui", "--no-mouse"])
    assert result.exit_code == 0, result.output
    run.assert_called_once_with(mouse=False)
