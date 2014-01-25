from time import time
from datetime import datetime

from .. import bar
from textbox import TextBox

import gobject


class Clock(TextBox):
    """
        A simple but flexible text-based clock.
    """
    def __init__(self, fmt="%H:%M", **config):
        """
            - fmt: A Python datetime format string.

            - width: A fixed width, or bar.CALCULATED to calculate the width
            automatically (which is recommended).
        """
        TextBox.__init__(self, " ", **config)
        self.fmt = fmt
        self.configured = False

    def _configure(self, qtile, bar, parent):
        if not self.configured:
            self.configured = True
            gobject.idle_add(self.update)
        TextBox._configure(self, qtile, bar, parent)

    def update(self):

        ts = time()

        self.timeout_add(1. - ts % 1., self.update)

        # adding .5 to get a proper seconds value because glib could
        # theoreticaly call our method too early and we could get something
        # like (x-1).999 instead of x.000
        self.text = datetime.fromtimestamp(int(ts + .5)).strftime(self.fmt)
        self.bar.draw()

        return False
