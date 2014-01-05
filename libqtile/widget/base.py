from .. import command, bar, configurable, drawer
import gobject
import logging
import threading
from operator import itemgetter


LEFT, RIGHT = object(), object()
TOP, BOTTOM = object(), object()
CENTER = object()


class _Widget(command.CommandObject, configurable.Configurable):
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
            return self.layout.width
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        if self._height is None:
            return self.layout.height
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
        ("fontsize", 0x1fff, "Font size. Calculated if 0x1fff."),
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
        self.padding = config.get("padding")
        self.align = config.get("align")
        self.valign = config.get("valign")
        self.calculate = config.get("font_size") is None
        self.add_defaults(_TextBox.defaults)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        if self.layout:
            # todo(horsik) resize parent if width changed
            self.layout.text = value
            self.draw()

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        self._font = value
        if self.layout:
            self.layout.font = value
            self.draw()

    @property
    def fontshadow(self):
        return self._fontshadow

    @fontshadow.setter
    def fontshadow(self, value):
        self._fontshadow = value
        if self.layout:
            self.layout.font_shadow = value
            self.draw()

    @property
    def fontsize(self):
        return self._fontsize

    @fontsize.setter
    def fontsize(self, value):
        self._fontsize = value
        if self.layout:
            self.layout.font_size = value
            self.draw()

    @property
    def padding(self):
        if self._padding is None:
            return (0, 0, 0, 0)
        else:
            return self._padding

    @padding.setter
    def padding(self, value):
        if type(value) == int:
            self._padding = (value,) * 4
        elif type(value) == tuple:
            if len(value) < 4:
                self._padding = value + (0,) * (4 - len(value))
            elif len(value) > 4:
                self._padding = value[:4]
            else:
                self._padding = value
        else:
            self._padding = value

    @property
    def align(self):
        if self.width < self.text_width:
            return 0  # there's nothing to align, let me decrease the font size
        elif self._align == LEFT or self._align is None:
            return self.padding[3]
        elif self._align == CENTER:
            return (self.width - self.text_width) / 2
        elif self._align == RIGHT:
            return self.width - self.text_width - self.padding[1]

    @align.setter
    def align(self, value):
        if value in (LEFT, CENTER, RIGHT, None):
            self._align = value
        else:
            raise command.CommandError("Invalid align value %.", value)

    @property
    def valign(self):
        if self.height < self.text_height:
            return 0  # there's nothing to align, let me decrease the font size
        elif self._valign == CENTER or self._valign is None:
            return (self.height - self.text_height) / 2
        elif self._valign == TOP:
            return self.padding[0]
        elif self._valign == BOTTOM:
            return self.height - self.text_height - self.padding[2]

    @valign.setter
    def valign(self, value):
        if value in (TOP, CENTER, BOTTOM, None):
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
        valid_width = self.width - sum(itemgetter(1, 3)(self.padding))
        valid_height = self.height - sum(itemgetter(0, 2)(self.padding))

        if valid_width < 0 or valid_height < 0:
            raise command.CommandError("Padding values have to be smaller than widget dimensions.")

        if self.text_width > valid_width:
            self.fontsize = valid_width * self.fontsize / self.text_width
        elif self.text_height > valid_height:
            self.fontsize = valid_height * self.fontsize / self.text_height

    def draw(self):
        self.text_width, self.text_height = self.layout.layout.get_pixel_size()

        self.drawer.clear(self.background or self.bar.background)
        self.layout.draw(self.align, self.valign)
        self.drawer.draw(self.x, self.y, self.width, self.height)

        if self.calculate:
            self._calculate_font_size()

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
