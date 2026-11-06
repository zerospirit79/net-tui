from .app import NetTuiApp


def run_tui(*, mouse: bool = True):
    NetTuiApp().run(mouse=mouse)
