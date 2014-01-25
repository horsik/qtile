from .. import hook, bar
from textbox import TextBox


class WindowName(TextBox):
    """
        Displays the name of the window that currently has focus.
    """
    def __init__(self, **config):
        TextBox.__init__(self, **config)

    def _configure(self, qtile, bar, parent):
        TextBox._configure(self, qtile, bar, parent)
        hook.subscribe.window_name_change(self.update)
        hook.subscribe.focus_change(self.update)
        hook.subscribe.float_change(self.update)

    def update(self):
        w = self.bar.screen.group.currentWindow
        state = ''
        if w is None:
            pass
        elif w.maximized:
            state = '[] '
        elif w.minimized:
            state = '_ '
        elif w.floating:
            state = 'V '
        self.text = "%s%s" % (state,  w.name if w and w.name else " ")
        self.bar.draw()
