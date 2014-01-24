import os
import cairo

import base
from .. import bar

class Image(base._Widget):

    defaults = [
        ("scale", True, "Enable/Disable image scaling"),
        ("filename", None, "PNG Image filename. Can contain '~'"),
    ]

    def __init__(self, **config):
        base._Widget.__init__(self, **config)
        self.add_defaults(Image.defaults)

    @property
    def inner_width(self):
        return self.image.get_width() + self.padding.horizontal

    @property
    def inner_height(self):
        return self.image.get_height() + self.padding.vertical

    def _configure(self, qtile, bar, parent):
        base._Widget._configure(self, qtile, bar, parent)

        if not self.filename:
            raise ValueError("Filename not set!")

        self.filename = os.path.expanduser(self.filename)

        try:
            self.image = cairo.ImageSurface.create_from_png(self.filename)
        except MemoryError:
            raise ValueError("The image '%s' doesn't seem to be a valid PNG"
                % (self.filename))

        self.pattern = cairo.SurfacePattern(self.image)

    def draw(self):
        width = self.width - self.padding.horizontal
        height = self.height - self.padding.vertical

        if width <= 0 or height <= 0:
            raise ValueError("Padding cannot be bigger than image size")

        scaler = cairo.Matrix()
        sw = self.image.get_width() / float(width)
        sh = self.image.get_height() / float(height)
        scaler.scale(sw, sh)
        self.pattern.set_matrix(scaler)

        self.drawer.clear(self.background or self.bar.background)
        self.drawer.ctx.save()
        self.drawer.ctx.translate(self.padding.left, self.padding.top)
        self.drawer.ctx.set_source(self.pattern)
        self.drawer.ctx.paint()
        self.drawer.ctx.restore()

        self.drawer.draw(self.x, self.y, self.width, self.height)

