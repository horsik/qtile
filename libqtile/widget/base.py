from .. import command, bar, configurable, drawer
import gobject
import logging
import threading


class _Widget(command.CommandObject, configurable.Configurable):
    defaults = [
        ("background", None, "Widget background color"),
        ("width", None, "Width of a widget, calculated if None"),
        ("height", None, "Height of a widget, calculated if None"),
        ("padding", None, "Widget padding in pixels"),
    ]

    def __init__(self, **config):
        command.CommandObject.__init__(self)
        self.name = self.__class__.__name__.lower()

        self.log = logging.getLogger('qtile')

        configurable.Configurable.__init__(self, **config)
        self.add_defaults(_Widget.defaults)

        self.configured = False

    @property
    def width(self):
        if self._width is None:
            return self.inner_width
        else:
            return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        if self._height is None:
            return self.inner_height
        else:
            return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, value):
        if type(value) == int:
            value = (value,) * 4
        elif type(value) == tuple:
            value += (0,) * (4 - len(value))
        else:
            value = (0, 0, 0, 0)

        self._padding = type('padding', (object,), {
            "top": value[0],
            "right": value[1],
            "bottom": value[2],
            "left": value[3],
            "vertical": value[0] + value[2],
            "horizontal": value[1] + value[3],
        })

    @property
    def win(self):
        return self.bar.window.window

    def _configure(self, qtile, bar, parent):
        self.qtile = qtile
        self.bar = bar
        self.parent = parent
        self.drawer = drawer.Drawer(
            qtile,
            self.win.wid,
            self.bar.width,
            self.bar.height
        )

        self.configured = True

    def clear(self):
        self.drawer.set_source_rgb(self.bar.background)
        self.drawer.fillrect(self.x, self.y, self.width, self.height)

    def info(self):
        return dict(
            name=self.__class__.__name__,
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height,
        )

    def button_press(self, x, y, button):
        pass

    def button_release(self, x, y, button):
        pass

    def get(self, q, name):
        """
            Utility function for quick retrieval of a widget by name.
        """
        w = q.widgetMap.get(name)
        if not w:
            raise command.CommandError("No such widget: %s" % name)
        return w

    def _items(self, name):
        if name == "bar":
            return (True, None)

    def _select(self, name, sel):
        if name == "bar":
            return self.bar

    def cmd_info(self):
        """
            Info for this object.
        """
        return dict(name=self.name)

    def draw(self):
        """
            Method that draws the widget. You may call this explicitly to
            redraw the widget, but only if the width of the widget hasn't
            changed. If it has, you must call bar.draw instead.
        """
        raise NotImplementedError

    def timeout_add(self, seconds, method, method_args=(),
                    callback=None, callback_args=()):
        """
            This method calls either ``gobject.timeout_add`` or
            ``gobject.timeout_add_seconds`` with same arguments. Latter is
            better for battery usage, but works only with integer timeouts.

            If callback is supplied, it runs method in a separate thread
            and then a callback at the end.
            *_args should be a tuple of arguments to supply to appropriate
            functions.
            !Callback function should return False, otherwise it would be
            re-run forever!
        """
        self.log.debug('Adding timer for %r in %.2fs', method, seconds)
        if int(seconds) == seconds:
            return gobject.timeout_add_seconds(
                int(seconds), method, *method_args
            )
        else:
            return gobject.timeout_add(
                int(seconds * 1000), method, *method_args
            )

