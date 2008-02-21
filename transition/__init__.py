# Unlike the hme module, this is a fairly straight port of the version 
# in TiVo's Java SDK. (I've even kept the original comments.) As such, 
# it's a derivative work, released under the Common Public License.
#
# Original version Copyright 2004, 2005 TiVo Inc.
# No credited authors
#
# This version: William McBrine, 2008

from hme import *

""" Simple application to test new transition feature. """

class Transition(Application):

    COLORS = (0xff0000, 0xffff00, 0x00ff00, 0x0000ff)

    def startup(self):    
    	self.depth = 0
        self.entry_color = -1
        self.return_color = -1
        self.cur_color = 0

        x = SAFE_ACTION_H
        w = self.root.width - 2 * x

        Font(self, size=30)
        View(self, x, SAFE_ACTION_V, w, 40, text='HME Transition Test')

        self.depth_view = TextView(self.root, x, 70, w, 40)
        self.entry_view = TextView(self.root, x, 100, w / 2 - 10, 40)
        self.return_view = TextView(self.root, x + w / 2 + 20, 100,
                                    w / 2 - 10, 40)
        self.color_view = TextView(self.root, x, 130, w, 40)

        Font(self, size=14)
        View(self, x, 400, w, 40,
             text='Move up and down to select a color.  ' +
                  'Move left to go back, right to go forward.')

        x = SAFE_ACTION_H + 75
        w = self.root.width - 2 * x
        h = 50
        self.hilight_view = View(self, x, 175, w, h, colornum=0xffffff)
        self.update_hilight()

        x = SAFE_ACTION_H + 80
        w = self.root.width - 2 * x
        h = 40
        for c in xrange(len(self.COLORS)):
            y = 180 + c * 50
            View(self, x, y, w, h, colornum=self.COLORS[c])

        self.error_view = TextView(self.root, x, 440, w, 40)
        self.error_view.set_font(18)
        self.error_view.set_foreground(0xff0000)

    # This method handles the incoming INIT_INFO event.  Here we
    # determine if we were entered via a "forward" transition or a
    # "back" transition (or possibly no transition at all).

    def handle_init_info(self, params, memento):
        print params
        print repr(memento)

        if params:
            if 'entry' in params:
                self.entry_color = int(params['entry'][0])

            if 'return' in params:
                self.return_color = int(params['return'][0])

            if 'depth' in params:
                self.depth = int(params['depth'][0])

        self.update_inits()

        if memento:
            self.cur_color = ord(memento[0])
            self.update_hilight()

    def handle_key_press(self, code, rawcode):
        if code == KEY_UP:
            self.cur_color = (self.cur_color - 1) % len(self.COLORS)
            self.update_hilight()
        elif code == KEY_DOWN:
            self.cur_color = (self.cur_color + 1) % len(self.COLORS)
            self.update_hilight()
        elif code == KEY_RIGHT:
            mem = chr(self.cur_color)
            params = {'entry': [self.cur_color],
                      'depth': [self.depth + 1]}
            self.transition(TRANSITION_FORWARD, params,
                            'http://%s/transition/' %
                            self.context.headers['host'], mem)
        elif code == KEY_LEFT:
            params = {'return': [self.cur_color],
                      'depth': [self.depth - 1]}
            self.transition(TRANSITION_BACK, params)

    def handle_error(self, code, text):
        self.error_view.set_value(text)

    def update_inits(self):
        self.depth_view.set_value('Current depth is %d.' % self.depth)

        if self.entry_color < 0:
            self.entry_view.set_value('No entry color.', 0x7f7f7f)
        else:
            self.entry_view.set_value('%#08x' %
                                      self.COLORS[self.entry_color],
                                      self.COLORS[self.entry_color])

        if self.return_color < 0:
            self.return_view.set_value('No return color', 0x7f7f7f)
        else:
            self.return_view.set_value('%#08x' %
                                       self.COLORS[self.return_color],
                                       self.COLORS[self.return_color])

    def update_hilight(self):
        y = 180 + self.cur_color * 50 - 5
        self.hilight_view.set_bounds(ypos=y, animtime=250)
        self.color_view.set_value('The currently selected color is %#08x' %
                                  self.COLORS[self.cur_color],
                                  self.COLORS[self.cur_color])


class TextView(View):
    def __init__(self, parent, x, y, width, height):
        View.__init__(self, parent.app, x, y, width, height, parent=parent)
        self.fg = Color(self.app)
        self.font = Font(self.app, size=20)
        self.value = ''

    def set_foreground(self, fg):
        fg = Color(self.app, fg)
        if self.fg != fg:
            self.fg = fg
            self.repaint()

    def set_font(self, size=20):
        font = Font(self.app, size=size)
        if self.font != font:
            self.font = font
            self.repaint()

    def set_value(self, obj, colornum=None):
        self.value = obj
        if colornum is not None:
            self.set_foreground(colornum)
        self.repaint()

    def repaint(self):
        self.set_text(self.value, self.font, self.fg)
