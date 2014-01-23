from base import _Base


class Horizontal(_Base):
    def __init__(self, widgets, **config):
        _Base.__init__(self, widgets, **config)

    @property
    def inner_width(self):
        widths = self._calculate_children_widths()
        return max(widths) * (len(widths) - 1)

    @property
    def inner_height(self):
        return max(self._calculate_children_heights())

    def _resize(self):
        if not self.widgets:
            return

        w = self.width / len(self.widgets)
        reminder = self.width % len(self.widgets)

        x, y = self.x, self.y
        for i in self.widgets:
            i.x, i.y = x, y
            i.width, i.height = w, self.height
            if reminder:
                i.width += 1
                reminder -= 1
                x += 1

            x += w

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
        heights = self._calculate_children_heights()
        return max(heights) * (len(heights) - 1)

    def _resize(self):
        if not self.widgets:
            return

        h = self.height / len(self.widgets)
        reminder = self.height % len(self.widgets)

        x, y = self.x, self.y
        for i in self.widgets:
            i.x, i.y = x, y
            i.width, i.height = self.width, h
            if reminder:
                i.height += 1
                reminder -= 1
                y += 1

            y += h

            if isinstance(i, _Base):
                i._resize()
