from .. import bar
from .. constants import *
import base


class TextBox(base._Widget):
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
        base._Widget.__init__(self, **config)
        self.add_defaults(TextBox.defaults)

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
            self.draw()

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, value):
        self._background = value
        if self.layout:
            self.drawer.clear(TRANSPARENT)
            self.draw()

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
        base._Widget._configure(self, qtile, bar, parent)
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

    def draw(self):
        self.text_width, self.text_height = self.layout.layout.get_pixel_size()

        self.drawer.clear(self.background or self.parent.background)
        self.layout.draw(self.align, self.valign)

        if self._calculate_font_size():
            self.drawer.draw(self.x, self.y, self.width, self.height)

    def update(self, text):
        self.text = text

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

    def cmd_update(self, text):
        """
            Update the text in a TextBox widget.
        """
        self.update(text)

    def cmd_get(self):
        """
            Retrieve the text in a TextBox widget.
        """
        return self.text
