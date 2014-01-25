from .. import hook, bar
from textbox import TextBox
from pythonwifi.iwlibs import Wireless, Iwstats


class Wlan(TextBox):
    """
        Displays Wifi ssid and quality.
    """
    def __init__(self, interface="wlan0", **config):
        """
            - interface: Wlan interface name.

            - width: A fixed width, or bar.CALCULATED to calculate the width
            automatically (which is recommended).
        """
        self.interface = interface
        TextBox.__init__(self, " ", width, **config)
        self.timeout_add(1, self.update)

    def _configure(self, qtile, bar, parent):
        TextBox._configure(self, qtile, bar, parent)

    def update(self):
        if self.configured:
            interface = Wireless(self.interface)
            stats = Iwstats(self.interface)
            quality = stats.qual.quality
            essid = interface.getEssid()
            text = "{} {}/70".format(essid, quality)
            if self.text != text:
                self.text = text
                self.bar.draw()
        return True
