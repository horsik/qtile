from base import _Base
from ... constants import *


class Horizontal(_Base):
    def __init__(self, widgets, **config):
        _Base.__init__(self, widgets, **config)

    @property
    def inner_width(self):
        return sum(self._calculate_children_widths())

    @property
    def inner_height(self):
        return max(self._calculate_children_heights())

    def _resize(self):
        x, y = self.x, self.y

        stretched = [w for w in self.widgets if w.config_width == STRETCH]
        fixed = set(self.widgets) - set(stretched)
        available = self.width - sum(self._get_child_width(w) for w in fixed)

        for i in self.widgets:
            i.x, i.y = x, y
            i.height = self.height

            if i.config_width == STRETCH:
                i.width = available / len(stretched) if available > 0 else 0
            else:
                i.width = self._get_child_width(i)

            x += i.width

            if isinstance(i, _Base):
                i._resize()


class Vertical(_Base):
    def __init__(self, widgets, **config):
        _Base.__init__(self, widgets, **config)

    @property
    def inner_width(self):
        return max(self._calculate_children_widths())

    @property
    def inner_height(self):
        return sum(self._calculate_children_heights())

    def _resize(self):
        x, y = self.x, self.y

        stretched = [w for w in self.widgets if w.config_height == STRETCH]
        fixed = set(self.widgets) - set(stretched)
        available = self.height - sum(self._get_child_height(w) for w in fixed)

        for i in self.widgets:
            i.x, i.y = x, y
            i.width = self.width

            if i.config_height == STRETCH:
                i.height = available / len(stretched) if available > 0 else 0
            else:
                i.height = self._get_child_height(i)

            y += i.height

            if isinstance(i, _Base):
                i._resize()

