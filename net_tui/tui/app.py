from textual.app import App

from net_tui.screens.dns import DnsScreen
from net_tui.screens.hostname import HostnameScreen
from net_tui.screens.hosts import HostsScreen
from net_tui.screens.interfaces import InterfacesScreen
from net_tui.screens.mainmenu import MainMenuScreen


class NetTuiApp(App):
    TITLE = "NET / TUI"
    SUB_TITLE = "Сетевые инструменты ALT Linux"
    CSS = """
    Screen { background: #0b1120; color: #dbe7f5; }
    Header { background: #172238; color: #65dcdf; }
    Footer { background: #172238; }
    #start-menu, .page { margin: 1 2; padding: 1 2; border: round #30425e; background: #101b2d; }
    #start-menu { height: 1fr; overflow-y: auto; }
    .page { height: 1fr; }
    .eyebrow { color: #65dcdf; text-style: bold; height: auto; margin-bottom: 1; }
    .page-title { text-style: bold; color: #f1f6ff; height: auto; margin-bottom: 1; }
    .subtitle { color: #9aafc9; height: auto; margin-bottom: 1; }
    #menu-grid { layout: grid; grid-size: 2 2; grid-gutter: 1 2; height: 1fr; min-height: 18; }
    .card { border: round #30425e; background: #172238; padding: 1 2; height: 1fr; }
    .card:hover { border: round #65dcdf; background: #1b2e45; }
    .card Button { width: 100%; margin-bottom: 1; text-style: bold; }
    .card Static { color: #9aafc9; height: auto; }
    #menu-hosts { color: #65dcdf; }
    #menu-hostname { color: #b8a0ff; }
    #menu-interfaces { color: #82e6b2; }
    #menu-dns { color: #ffcb7d; }
    #status { color: #82e6b2; height: auto; margin-bottom: 1; }
    #menu-exit { margin-top: 1; }
    Label { color: #9aafc9; margin-top: 1; height: auto; }
    Input, Select { margin-bottom: 1; }
    Input { border: tall #30425e; background: #0b1120; }
    Input:focus { border: tall #65dcdf; }
    TextArea { height: 1fr; min-height: 3; border: round #30425e; background: #0b1120; }
    TextArea:focus { border: round #65dcdf; }
    .form { height: 1fr; }
    .actions { height: auto; margin-top: 1; }
    .actions Button { margin-right: 2; }
    Button { background: #21324b; border: none; }
    Button:hover { background: #304967; }
    Button:focus { text-style: bold; background: #304967; }
    Button.-primary { background: #147d87; color: #ffffff; }
    .warning { color: #ffcb7d; height: auto; margin-top: 1; }
    """

    def on_mount(self) -> None:
        for name, screen in (("start", MainMenuScreen()), ("hosts", HostsScreen()),
                             ("hostname", HostnameScreen()), ("interfaces", InterfacesScreen()),
                             ("dns", DnsScreen())):
            self.install_screen(screen, name=name)
        self.push_screen("start")


if __name__ == "__main__":
    NetTuiApp().run()
