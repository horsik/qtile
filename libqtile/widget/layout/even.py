from base import _Base


class Horizontal(_Base):
    def __init__(self, widgets):
        _Base.__init__(self, widgets)

    def _resize(self):
        w = self.width / len(self.widgets)
        reminder = self.height % len(self.widgets)

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
    def __init__(self, widgets):
        _Base.__init__(self, widgets)

    def _resize(self):
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