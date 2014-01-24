from .. import command, bar, configurable, drawer
import gobject
import logging
import threading


LEFT, RIGHT = object(), object()
TOP, BOTTOM = object(), object()
CENTER = object()


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


UNSPECIFIED = bar.Obj("UNSPECIFIED")


class _TextBox(_Widget):
    """
        Base class for widgets that are just boxes containing text.
    """
    defaults = [
        ("font", "Arial", "Default font"),
        ("fontsize", 12, "Default font size"),
        ("foreground", "ffffff", "Foreground colour"),
        (
            "fontshadow",
            None,
            "font shadow color, default is None(no shadow)"
        ),
        ("align", LEFT, "Horizontal text padding"),
        ("valign", CENTER, "Vertical text padding"),
    ]

    def __init__(self, text=" ", **config):
        self.layout = None
        self.text = text
        _Widget.__init__(self, **config)
        self.add_defaults(_TextBox.defaults)

    @property
    def inner_width(self):
        return self.layout.width + self.padding.horizontal

    @property
    def inner_height(self):
        return self.layout.height + self.padding.vertical

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
    def align(self):
        if self.width < self.text_width:
            return 0  # there's nothing to align
        elif self._align == LEFT:
            return self.padding.left
        elif self._align == CENTER:
            return (self.width - self.text_width) / 2
        elif self._align == RIGHT:
            return self.width - self.text_width - self.padding.right

    @align.setter
    def align(self, value):
        if value in (LEFT, CENTER, RIGHT):
            self._align = value
        else:
            raise command.CommandError("Invalid align value %.", value)

    @property
    def valign(self):
        if self.height < self.text_height:
            return 0  # there's nothing to align
        elif self._valign == CENTER:
            return (self.height - self.text_height) / 2
        elif self._valign == TOP:
            return self.padding.top
        elif self._valign == BOTTOM:
            return self.height - self.text_height - self.padding.bottom

    @valign.setter
    def valign(self, value):
        if value in (TOP, CENTER, BOTTOM):
            self._valign = value
        else:
            raise command.CommandError("Invalid valign value %.", value)

    def _configure(self, qtile, bar, parent):
        _Widget._configure(self, qtile, bar, parent)
        self.layout = self.drawer.textlayout(
            self.text,
            self.foreground,
            self.font,
            self.fontsize,
            self.fontshadow,
        )

    def _calculate_font_size(self):
        width = self.width - self.padding.horizontal
        height = self.height - self.padding.vertical

        if self.text_width > width > 0:
            self.fontsize = width * self.fontsize / self.text_width
        elif self.text_height > height > 0:
            self.fontsize = height * self.fontsize / self.text_height
        else:
            return True

        # widget size changed, stop drawing bar and start over
        return False

    def draw(self):
        self.text_width, self.text_height = self.layout.layout.get_pixel_size()

        self.drawer.clear(self.background or self.bar.background)
        self.layout.draw(self.align, self.valign)
        self.drawer.draw(self.x, self.y, self.width, self.height)

        return self._calculate_font_size()

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
