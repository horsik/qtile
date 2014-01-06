from base import _Base


class Horizontal(_Base):
    def __init__(self, widgets, **config):
        _Base.__init__(self, widgets, **config)

    def _resize(self):
        x, y = self.x, self.y
        for i in self.widgets:
            i.x = x
            i.y = y

            if isinstance(i, _Base):
                i.width = i.get_inner_width()

            x += i.width

            if isinstance(i, _Base):
                i._resize()

    def get_inner_width(self):
        return sum(self.inner_width)

    def get_inner_height(self):
        return max(self.inner_height)
        

class Vertical(_Base):
    def __init__(self, widgets, **config):
        _Base.__init__(self, widgets, **config)

    def _resize(self):
        x, y = self.x, self.y
        for i in self.widgets:
            i.x = x
            i.y = y

            if isinstance(i, _Base):
                i.height = i.get_inner_height()

            y += i.height

            if isinstance(i, _Base):
                i._resize()

    def get_inner_width(self):
        return max(self.inner_width)

    def get_inner_height(self):
        return sum(self.inner_height)
