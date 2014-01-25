from textbox import TextBox
from .. import bar, hook


class CurrentLayout(TextBox):
    def __init__(self, **config):
        TextBox.__init__(self, "", **config)

    def _configure(self, qtile, bar, parent):
        TextBox._configure(self, qtile, bar, parent)
        self.setup_hooks()

    def setup_hooks(self):
        def hook_response(layout, group):
            if group.screen is not None and group.screen == self.bar.screen:
                self.text = layout.name
                self.bar.draw()
        hook.subscribe.layout_change(hook_response)

    def button_press(self, x, y, button):
        if button == 1:
            self.qtile.cmd_nextlayout()
        elif button == 2:
            self.qtile.cmd_prevlayout()
