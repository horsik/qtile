from .. import command, bar, configurable, drawer
import gobject
import logging
import threading


LEFT = object()
CENTER = object()


class _Widget(command.CommandObject, configurable.Configurable):
    offset = None
    defaults = [("background", None, "Widget background color")]

    def __init__(self, **config):
        command.CommandObject.__init__(self)
        self.name = self.__class__.__name__.lower()
        if "name" in config:
            self.name = config["name"]

        self.log = logging.getLogger('qtile')

        configurable.Configurable.__init__(self, **config)
        self.add_defaults(_Widget.defaults)

        self.x, self.y = config.get("x"), config.get("y")
        self.width, self.height = config.get("width"), config.get("height")

        self.configured = False

    @property
    def width(self):
        if self._width is None:
            return self.layout.width + self.actual_padding * 2
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        if self._height is None:
            return self.layout.height + self.actual_padding * 2
        else:
            return self._height

    @height.setter
    def height(self, value):
        self._height = value

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
            self.parent.width,
            self.parent.height
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


UNSPECIFIED = bar.Obj("UNSPECIFIED")


class _TextBox(_Widget):
    """
        Base class for widgets that are just boxes containing text.
    """
    defaults = [
        ("font", "Arial", "Default font"),
        ("fontsize", 0x1fff, "Font size. Calculated if 0x1fffff."),
        ("padding", None, "Padding. Calculated if None."),
        ("foreground", "ffffff", "Foreground colour"),
        (
            "fontshadow",
            None,
            "font shadow color, default is None(no shadow)"
        ),
    ]

    def __init__(self, text=" ", **config):
        self.layout = None
        _Widget.__init__(self, **config)
        self.text = text
        self.add_defaults(_TextBox.defaults)
        self.calculate = config.get("font_size") is None

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        if self.layout:
            self.layout.text = value

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        self._font = value
        if self.layout:
            self.layout.font = value

    @property
    def fontshadow(self):
        return self._fontshadow

    @fontshadow.setter
    def fontshadow(self, value):
        self._fontshadow = value
        if self.layout:
            self.layout.font_shadow = value

    @property
    def fontsize(self):
        return self._fontsize

    @fontsize.setter
    def fontsize(self, value):
        self._fontsize = value
        if self.layout:
            self.layout.font_size = value

    @property
    def actual_padding(self):
        if self.padding is None:
            # todo(horsik) this needs refactoring, it's only left-right padding
            return 0
        else:
            return self.padding

    def _configure(self, qtile, bar, parent):
        _Widget._configure(self, qtile, bar, parent)
        self.layout = self.drawer.textlayout(
            self.text,
            self.foreground,
            self.font,
            self.fontsize,
            self.fontshadow,
        )

    def draw(self):
        self.drawer.clear(self.background or self.bar.background)
        self.layout.draw(
            self.actual_padding or 0,
            int(self.height / 2.0 - self.layout.height / 2.0)
        )
        self.drawer.draw(self.x, self.y, self.width, self.height)

        if self.calculate:
            size = self.layout.layout.get_pixel_size()
            if size[0] > self.width:
                self.fontsize = self.width * self.fontsize / size[0]
                self.draw()
            elif size[1] > self.height:
                self.fontsize = self.height * self.fontsize / size[1]
                self.draw()


    def cmd_set_font(self, font=UNSPECIFIED, fontsize=UNSPECIFIED,
                     fontshadow=UNSPECIFIED):
        """
            Change the font used by this widget. If font is None, the current
            font is used.
        """
        if font is not UNSPECIFIED:
            self.font = font
        if fontsize is not UNSPECIFIED:
            self.fontsize = fontsize
        if fontshadow is not UNSPECIFIED:
            self.fontshadow = fontshadow
        self.draw()