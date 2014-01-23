# Copyright (c) 2008, Aldo Cortesi. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import command
import confreader
import drawer
import hook
import configurable
import window

import gobject

USE_BAR_DRAW_QUEUE = True


class Gap(command.CommandObject):
    """
        A gap, placed along one of the edges of the screen. If a gap has been
        defined, Qtile will avoid covering it with windows. The most probable
        reason for configuring a gap is to make space for a third-party bar or
        other static window.
    """
    def __init__(self, **config):
        self.config = config
        self.qtile = None
        self.screen = None
        self.configured = False

    def _configure(self, qtile, screen):
        self.qtile = qtile
        self.screen = screen
        # todo(horsik) refactor
        self.width, self.height = self.config.get("width"), self.config.get("height")
        self.x, self.y = self.config.get("x"), self.config.get("y")
        self.configured = True

    def draw(self):
        pass

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if self.position == LEFT:
            self._x = self.screen.dx
        elif self.position == RIGHT:
            self._x = self.screen.width - self.screen.bars_whole_width(RIGHT) - self.width
        elif self.position == FLOATING:
            self._x = value
        else:
            self._x = self.screen.dx

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if self.position == TOP:
            self._y = self.screen.dy
        elif self.position == BOTTOM:
            self._y = self.screen.height - self.screen.bars_whole_height(BOTTOM) - self.height
        elif self.position == FLOATING:
            self._y = value
        else:
            self._y = self.screen.dy

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if self.position in [TOP, BOTTOM]:
            self._width = self.screen.dwidth
        else:
            self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if self.position in [LEFT, RIGHT]:
            self._height = self.screen.dheight
        else:
            self._height = value

    @property
    def position(self):
        return self.config.get("position")

    def geometry(self):
        return (self.x, self.y, self.width, self.height)

    def _items(self, name):
        if name == "screen":
            return (True, None)

    def _select(self, name, sel):
        if name == "screen":
            return self.screen

    def info(self):
        return dict(position=self.position)

    def cmd_info(self):
        """
            Info for this object.
        """
        return self.info()


class Obj:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

constants = [
    "STRETCH", "CALCULATED", "STATIC",
    "TOP", "LEFT", "BOTTOM", "RIGHT", "FLOATING"
]

for name in constants:
    vars()[name] = Obj(name)


class Bar(Gap, configurable.Configurable):
    """
        A bar, which can contain widgets. Note that bars can only be placed at
        the top or bottom of the screen.
    """
    defaults = [
        ("background", "#000000", "Background colour."),
        ("opacity",  1, "Bar window opacity.")
    ]

    def __init__(self, layout, **config):
        """
            layout - A layout used as a container for widgets.
            **config - dictionary describing bar configuration keys:
                position - specifies bar position, valid values: TOP, RIGHT, BOTTOM, LEFT
                width - width of the bar (required for position TOP and BOTTOM)
                height - height of the bar (required for position TOP and BOTTOM)
        """
        import widget
        if not isinstance(layout, widget.layout._Base):
            raise confreader.ConfigError("Bar object only accepts a layout instance as an argument.")

        Gap.__init__(self, **config)
        configurable.Configurable.__init__(self, **config)
        self.add_defaults(Bar.defaults)
        self.layout = layout
        self.saved_focus = None

        self.queued_draws = 0

    def _configure(self, qtile, screen):
        Gap._configure(self, qtile, screen)
        self.window = window.Internal.create(
            self.qtile,
            self.x, self.y, self.width, self.height,
            self.opacity
        )

        self.drawer = drawer.Drawer(
            self.qtile,
            self.window.window.wid,
            self.width,
            self.height
        )
        self.drawer.clear(self.background)

        self.window.handle_Expose = self.handle_Expose
        self.window.handle_ButtonPress = self.layout.handle_ButtonPress
        self.window.handle_ButtonRelease = self.layout.handle_ButtonRelease
        qtile.windowMap[self.window.window.wid] = self.window
        self.window.unhide()

        qtile.registerWidget(self.layout)
        self.layout._configure(qtile, self)

        # FIXME: These should be targeted better.
        hook.subscribe.setgroup(self.draw)
        hook.subscribe.changegroup(self.draw)

    def handle_Expose(self, e):
        self.draw()

    def widget_grab_keyboard(self, widget):
        """
            A widget can call this method to grab the keyboard focus
            and receive keyboard messages. When done,
            widget_ungrab_keyboard() must be called.
        """
        self.window.handle_KeyPress = widget.handle_KeyPress
        self.saved_focus = self.qtile.currentWindow
        self.window.window.set_input_focus()

    def widget_ungrab_keyboard(self):
        """
            Removes the widget's keyboard handler.
        """
        del self.window.handle_KeyPress
        if not self.saved_focus is None:
            self.saved_focus.window.set_input_focus()

    def draw(self):
        if USE_BAR_DRAW_QUEUE:
            if self.queued_draws == 0:
                gobject.idle_add(self._actual_draw)
            self.queued_draws += 1
        else:
            self._actual_draw()

    def _actual_draw(self):
        self.layout._resize()
        self.layout.draw()
        self.queued_draws = 0

        # have to return False here to avoid getting called again
        return False

    def info(self):
        return dict(
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height,
            position=self.position,
            layout=self.layout,
            window=self.window.window.wid
        )

    # todo(horsik) should be adapted
    def cmd_fake_button_press(self, screen, position, x, y, button=1):
        """
            Fake a mouse-button-press on the bar. Co-ordinates are relative
            to the top-left corner of the bar.

            :screen The integer screen offset
            :position One of "top", "bottom", "left", or "right"
        """
        class _fake:
            pass
        fake = _fake()
        fake.event_x = x
        fake.event_y = y
        fake.detail = button
        self.handle_ButtonPress(fake)
