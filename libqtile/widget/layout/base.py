from ... import configurable


class _Base(configurable.Configurable):
    """
        This class is a base for every widget layout
    """
    defaults = [
        ("x", 0, "Horizontal offset absolute to bar"),
        ("y", 0, "Vertical offset absoute to bar"),
        ("width", None, "Width of a layout"),
        ("height", None, "Height of a layout"),
    ]

    @property
    def inner_width(self):
        return \
            [max(w.layout.width, w.config.get("width")) for w in self.widgets if not isinstance(w, _Base)] + \
            [l.get_inner_width() for l in self.widgets if isinstance(l, _Base)] + [0]

    @property
    def inner_height(self):
        return \
            [max(w.layout.height, w.config.get("height")) for w in self.widgets if not isinstance(w, _Base)] + \
            [l.get_inner_height() for l in self.widgets if isinstance(l, _Base)] + [0]

    def __init__(self, widgets, **config):
        self.name = self.__class__.__name__.lower()
        self.widgets = widgets
        configurable.Configurable.__init__(self, **config)
        self.add_defaults(_Base.defaults)

    def _configure(self, qtile, bar, parent=None):
        if parent is None:
            self.parent, parent = bar, self
        else:
            self.parent = parent

        # assume maximum layout size
        # it might be changed when parent does _resize
        if not self.width: self.width = self.parent.width
        if not self.height: self.height = self.parent.height

        self.bar = bar

        for i in self.widgets:
            qtile.registerWidget(i)
            i._configure(qtile, bar, self)

    def _resize(self):
        """
            Method placing widgets in desired position and setting their size
        """
        raise NotImplementedError

    def draw(self):
        self.bar.drawer.draw(self.x, self.y, self.width, self.height)
        for i in self.widgets:
            i.draw()
