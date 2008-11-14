# Unlike the hme module, this is a straight port of the version in 
# TiVo's Java SDK. (I've even kept the original comments.) As such, it's 
# a derivative work, released under the Common Public License.
#
# Original version credited author: Brigham Stevens
# Copyright 2004, 2005 TiVo Inc.
#
# This version: William McBrine, 2008

from hme import *

TITLE = 'Font Info'
CLASS_NAME = 'FontInfo'

"""Displays font metrics returned in EVT_FONT_INFO event.
   Demonstrates using the metrics to size text vertically and horizontally.

"""

class FontInfo(Application):
    def startup(self):
        # create the main view which will display the font info
        self.fv = View(self)

        # create the font and ... Use new font flags to indicate to the 
        # reciever to send back metrics for this font
        Font(self, style=FONT_BOLD, size=36,
             flags=FONT_METRICS_BASIC|FONT_METRICS_GLYPH)

    def handle_font_info(self, font):
        # change the text displayed to contain the font info
        self.fv.set_text("Font Info:  default.ttf 36 Bold\n" +
                         "height:     " + str(font.height)  + "\n" +
                         "ascent:     " + str(font.ascent)  + "\n" +
                         "descent:    " + str(font.descent) + "\n" +
                         "linegap:    " + str(font.line_gap) + "\n" +
                         "l advance:  " + str(font.glyphs['l'][0]) + "\n" +
                         "M advance:  " + str(font.glyphs['M'][0]),
                         flags=RSRC_TEXT_WRAP)

        # resize the view vertically to exactly fit the text
        new_height = int(font.height * 8)
        new_y = 240 - new_height / 2
        self.fv.set_bounds(ypos=new_y, height=new_height)

        # create a header view that is sized to the exact top area above 
        # the font info
        header = View(self, height=new_y, colornum=0x7f7f7f)
        header.child().set_text('Header', colornum=0xff)

        # create a footer view that is sized to the exact area below the 
        # font info
        footer = View(self, ypos=new_y + new_height, height=new_y,
                      colornum=0x7f7f7f)

        # create a text resource and put in a view that is sized-to-fit 
        # the width
        some_text = u'Program Your TV!\u00ae'
        some_text_w = self.measure_text_width(some_text, font)

        # set the BG color behind the text
        footer.child(width=some_text_w, colornum=0xff0000)

        # create the view that contains the text
        footer.child(width=some_text_w).set_text(some_text, colornum=0xffff)

        # position the footer to the right of the text
        footer.child(xpos=some_text_w, width=footer.width -
                     some_text_w).set_text('Footer', colornum=0xff)

    def measure_text_width(self, string, font):
        width = 0
        for c in string:
            info = font.glyphs.get(c, (0, 0))
            width += info[0]    # advance
        if info[1] > info[0]:   # bounding
            width += (info[1] - info[0])
        return int(width)
