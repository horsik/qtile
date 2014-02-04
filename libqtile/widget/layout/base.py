from ... import configurable


class _Base(configurable.Configurable):
    """
        This class is a base for every widget layout
    """
    def __init__(self, widgets, **config):
        self.name = self.__class__.__name__.lower()
        self.widgets = widgets
        configurable.Configurable.__init__(self, **config)

    @property
    def config_width(self):
        return self._user_config.get("width")

    @property
    def config_height(self):
        return self._user_config.get("height")

    def _configure(self, qtile, bar, parent=None):
        """
            Configures the layout

            Initial width and height is set to parent's dimmensions.
            All of the widgets being direct children of this layout
            will use these to create drawers ensuring that canvas
            is the same size as its parent
        """
        self.parent = parent if parent else bar
        self.bar = bar

        defaults = [
            ("x", 0, "Horizontal offset absolute to bar"),
            ("y", 0, "Vertical offset absoute to bar"),
            ("width", self.parent.width, "Width of a layout"),
            ("height", self.parent.height, "Height of a layout"),
            ("background", self.parent.background, "Widget background color"),
        ]

        self.add_defaults(defaults)

        for i in self.widgets:
            qtile.registerWidget(i)
            i._configure(qtile, bar, self)

    def _resize(self):
        """
            Method placing widgets in desired position and setting their size
        """
        raise NotImplementedError

    def _get_child_width(self, i):
        return i.config_width or i.inner_width

    def _get_child_height(self, i):
        return i.config_height or i.inner_height

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
                widgets.append(max(w.inner_width, w.config_width))

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
                widgets.append(max(w.inner_height, w.config_height))

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

