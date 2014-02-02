from base import _Base


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
        for i in self.widgets:
            i.x = x
            i.y = y

            if isinstance(i, _Base):
                i.width = i._user_config.get("width") or i.inner_width
                i.height = i._user_config.get("height") or i.inner_height

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
        for i in self.widgets:
            i.x = x
            i.y = y

            if isinstance(i, _Base):
                i.height = i._user_config.get("height") or i.inner_height
                i.width = i._user_config.get("width") or i.inner_width

            y += i.height

            if isinstance(i, _Base):
                i._resize()
