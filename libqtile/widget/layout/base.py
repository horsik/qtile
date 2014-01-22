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
            [max(w.layout.width, w._user_config.get("width")) for w in self.widgets if not isinstance(w, _Base)] + \
            [l.get_inner_width() for l in self.widgets if isinstance(l, _Base)] + [0]

    @property
    def inner_height(self):
        return \
            [max(w.layout.height, w._user_config.get("height")) for w in self.widgets if not isinstance(w, _Base)] + \
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

    def get_widget_in_position(self, e):
        for i in self.widgets:
            if i.x < e.event_x < i.x + i.width and i.y < e.event_y < i.y + i.height:
                return i

    def handle_ButtonPress(self, e):
        widget = self.get_widget_in_position(e)
        if isinstance(widget, _Base):
            widget.handle_ButtonPress(e)
        elif widget:
            widget.button_press(
                e.event_x - widget.x,
                e.event_y - widget.y,
                e.detail
            )

    def handle_ButtonRelease(self, e):
        widget = self.get_widget_in_position(e)
        if isinstance(widget, _Base):
            widget.handle_ButtonRelease(e)
        elif widget:
            widget.button_release(
                e.event_x - widget.x,
                e.event_y - widget.y,
                e.detail
            )
