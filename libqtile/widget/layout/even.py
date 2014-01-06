from base import _Base


class Horizontal(_Base):
    def __init__(self, widgets, **config):
        _Base.__init__(self, widgets, **config)

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

    def get_inner_width(self):
        return max(self.inner_width) * (len(self.inner_width) - 1)

    def get_inner_height(self):
        return max(self.inner_height)


class Vertical(_Base):
    def __init__(self, widgets, **config):
        _Base.__init__(self, widgets, **config)

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

    def get_inner_width(self):
        return max(self.inner_width)

    def get_inner_height(self):
        return max(self.inner_height) * (len(self.inner_height) - 1)
