class _Base(object):
    """
        This class is a base for every widget layout
    """
    def __init__(self, widgets):
        self.name = self.__class__.__name__.lower()
        self.widgets = widgets

    def _configure(self, qtile, bar, parent=None):
        if parent is None:
            self.parent, parent = bar, self
            self.width, self.height = bar.width, bar.height
            self.x, self.y = 0, 0
        else:
            self.parent = parent
        for i in self.widgets:
            qtile.registerWidget(i)
            i._configure(qtile, bar, parent)

    def _resize(self):
        """
            Method placing widgets in desired position and setting their size
            If layout is fluid you have to call this method every time your
            widget changes dimensions.
        """
        raise NotImplementedError

    def draw(self):
        for i in self.widgets:
            i.draw()