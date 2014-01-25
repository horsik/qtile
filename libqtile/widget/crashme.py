# -*- coding: utf-8 -*-
from .. import bar
from textbox import TextBox


class _CrashMe(TextBox):
    """
        A developper widget to force a crash in qtile
    """
    def __init__(self, width=bar.CALCULATED, **config):
        """
            - width: A fixed width, or bar.CALCULATED to calculate the width
            automatically (which is recommended).
        """
        TextBox.__init__(self, "Crash me !", width, **config)

    def _configure(self, qtile, bar):
        base._Widget._configure(self, qtile, bar)
        self.layout = self.drawer.textlayout(
            self.text,
            self.foreground,
            self.font,
            self.fontsize,
            self.fontshadow,
            markup=True
        )

    def button_press(self, x, y, button):
        if button == 1:
            1 / 0
        elif button == 3:
            self.text = '<span>\xC3GError'
            self.bar.draw()
