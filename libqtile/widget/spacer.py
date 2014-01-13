from textbox import TextBox
from .. constants import *

class Spacer(TextBox):
    """
        Just an empty space on the bar. Often used with width equal to
        STRETCH to push bar widgets to the right edge of the screen.
    """
    def __init__(self, width=STRETCH, **config):
        """
            - width: STRETCH, or a pixel width.
        """
        TextBox.__init__(self, "", width=width, **config)

