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

    def _calculate_children_widths(self):
        """
            Internal method used only by fixed layout

            Returns an array of widths of items inside a layout
        """
        widgets, layouts = [], []

        for w in self.widgets:
            if isinstance(w, _Base):
                layouts.append(w.inner_width)
            else:
                widgets.append(max(w.inner_width, w._user_config.get("width")))

        return widgets + layouts + [0]

    def _calculate_children_heights(self):
        """
            Internal method used only by fixed layout

            Returns an array of heights of items inside a layout
        """
        widgets, layouts = [], []

        for w in self.widgets:
            if isinstance(w, _Base):
                layouts.append(w.inner_height)
            else:
                widgets.append(max(w.inner_height,
                                   w._user_config.get("height")))

        return widgets + layouts + [0]

    def draw(self):
        self.bar.drawer.draw(self.x, self.y, self.width, self.height)
        for i in self.widgets:
            if i.draw() == False:
                # one of children changed size, stop drawing bar and start over
                return False

        return True

    def get_widget_in_position(self, e):
        for i in self.widgets:
            if i.x < e.event_x < i.x + i.width and \
               i.y < e.event_y < i.y + i.height:
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
