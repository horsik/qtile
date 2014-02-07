from .. constants import *
from .. import configurable, hook
from textbox import TextBox
import layout
import types

class _GroupBox(configurable.Configurable):
    """
        A widget that graphically displays the current group.
    """
    defaults = [
        ("active", "FFFFFF", "Active group font colour"),
        ("inactive", "404040", "Inactive group font colour"),
        ("urgent_text", "FF0000", "Urgent group font color"),
        (
            "highlight_method",
            "border",
            "Method of highlighting (one of 'border' or 'block') "
            "Uses *_border color settings"
        ),
        ("rounded", True, "To round or not to round borders"),
        (
            "this_current_screen_border",
            "215578",
            "Border colour for group on this screen when focused."
        ),
        (
            "urgent_alert_method",
            "border",
            "Method for alerting you of WM urgent "
            "hints (one of 'border', 'text' or 'block')"
        ),
        (
            "disable_drag",
            False,
            "Disable dragging and dropping of group names on widget"
        ),
        (
            "this_screen_border",
            "215578",
            "Border colour for group on this screen."
        ),
        (
            "other_screen_border",
            "404040",
            "Border colour for group on other screen."
        ),
        ("urgent_border", "FF0000", "Urgent border color"),
        ("borderwidth", 3, "Current group border width"),
        ("padding", 3, "Border padding"),
    ]

    def __init__(self, **config): 
        self.name = self.__class__.__name__.lower()

        configurable.Configurable.__init__(self, **config)
        self.add_defaults(self.defaults)

        hook.subscribe.addgroup(self.addgroup)
        hook.subscribe.delgroup(self.delgroup)

    def addgroup(self, qtile, name):
        widget = TextBox(name, align=CENTER)

        def button_press(self, x, y, button):
            self.bar.screen.setGroup(qtile.groupMap.get(name))

        widget.button_press = types.MethodType(button_press, widget, TextBox) 
        self.widgets.append(widget)

    def delgroup(self, qtile, name):
        for i, v in enumerate(self.widgets):
            if v.text == name:
                del self.widgets[i]
                break

    def draw(self):
        for i in self.widgets:
            if self.bar.screen.group.name == i.text:
                if self.bar.qtile.currentScreen == self.bar.screen:
                    border = self.this_current_screen_border
                else:
                    border = self.this_screen_border
            else:
                border = self.other_screen_border

            i.framed = i.layout.framed(self.borderwidth, border,
                                       self.padding, self.padding)
            i.framed.draw(0, 0, i.width, i.height, self.rounded)
            i.drawer.draw(i.x, i.y, i.width, i.height)


class Horizontal(layout.even.Horizontal, _GroupBox):
    def __init__(self, **config):
        layout.even.Horizontal.__init__(self, [], **config)
        _GroupBox.__init__(self, **config)

    def draw(self):
        layout.even.Horizontal.draw(self)
        _GroupBox.draw(self)

class Vertical(layout.even.Vertical, _GroupBox):
    def __init__(self, **config):
        layout.even.Vertical.__init__(self, [], **config)
        _GroupBox.__init__(self, **config)

    def draw(self):
        layout.even.Vertical.draw(self)
        _GroupBox.draw(self)


