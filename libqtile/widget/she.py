from textbox import TextBox
from libqtile import bar, hook

__all__ = ['She']


class She(TextBox):
    ''' Widget to display the Super Hybrid Engine status.
    can display either the mode or CPU speed on eeepc computers.'''

    defaults = [
        ('device', '/sys/devices/platform/eeepc/cpufv', 'sys path to cpufv'),
        ('format', 'speed', 'Type of info to display "speed" or "name"'),
        ('update_delay', 0.5, 'Update Time in seconds.'),
    ]

    def __init__(self, **config):
        TextBox.__init__(self, 'CPU', **config)
        self.add_defaults(She.defaults)
        self.modes = {
            '0x300': {'name': 'Performance', 'speed': '1.6GHz'},
            '0x301': {'name': 'Normal', 'speed': '1.2GHz'},
            '0x302': {'name': 'PoswerSave', 'speed': '800MHz'}
        }
        self.modes_index = self.modes.keys().sort()
        self.mode = None
        self.timeout_add(self.update_delay, self.update)

    def _get_mode(self):
        with open(self.device) as f:
            mode = f.read().strip()
        return mode

    def update(self):
        if self.configured:
            mode = self._get_mode()
            if mode != self.mode:
                self.mode = mode
                if self.mode in self.modes.keys():
                    self.text = self.modes[self.mode][self.format]
                else:
                    self.text = self.mode
                self.bar.draw()
        return True
