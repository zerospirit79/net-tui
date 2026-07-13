from textual.app import App

from net_tui.screens.dns import DnsScreen
from net_tui.screens.hostname import HostnameScreen
from net_tui.screens.hosts import HostsScreen
from net_tui.screens.interfaces import InterfacesScreen
from net_tui.screens.mainmenu import MainMenuScreen


class NetTuiApp(App):
    CSS = """
    #start-menu {
        padding: 1;
        height: 100%;
    }
    #menu-title {
        content-align: center middle;
        height: 3;
    }
    """

    def on_mount(self) -> None:
        self.install_screen(MainMenuScreen(), name="start")
        self.install_screen(HostsScreen(), name="hosts")
        self.install_screen(HostnameScreen(), name="hostname")
        self.install_screen(InterfacesScreen(), name="interfaces")
        self.install_screen(DnsScreen(), name="dns")
        self.push_screen("start")


if __name__ == "__main__":
    NetTuiApp().run()
