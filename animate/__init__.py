# Unlike the hme module, this is a straight port of the version in 
# TiVo's Java SDK. (I've even kept the original comments.) As such, it's 
# a derivative work, released under the Common Public License.
#
# Original version credited authors: Adam Doppelt, Arthur van Hoff, 
# Brigham Stevens, Jonathan Payne, Steven Samorodin
# Copyright 2004, 2005 TiVo Inc.
#
# This version: William McBrine, 2008

import random

from hme import *

"""A simple demonstration of how to perform animations with View classes.
   This sample shows how to use Application.send_key() to receive a 
   notification when the animation request has completed.

"""

class Animate(Application):
    def handle_device_info(self, info):
        ver = info.get('version', '')
        if ver[:3] in ('9.1', '9.3') and not ver[-3:] in ('648', '652'):
            self.root.set_text('Sorry, this program is not compatible\n' +
                               'with this TiVo software/hardware version.')
            return

        # create a container view that will hold everything else, sized 
        # to the safe action bounds.
        content = View(self, SAFE_ACTION_H / 2, SAFE_ACTION_V / 2,
                       self.root.width - SAFE_ACTION_H,
                       self.root.height - SAFE_ACTION_V)

        # create the set of animated squares
        self.sprites = [SpriteView(content, i,
                                   random.randrange(content.width),
                                   random.randrange(content.height),
                                   random.randrange(8, 72),
                                   random.randrange(8, 72))
                        for i in xrange(16)]

    # Listen for our special "animation ended" event.

    def handle_key_press(self, keynum, index):
        if keynum == KEY_TIVO:
            self.sprites[index].animate()

    # If this ain't a screensaver, I don't know what is. -- wmcbrine

    def handle_idle(self, idle):
        return True


class SpriteView(View):
    def __init__(self, parent, index, x, y, width, height):
        View.__init__(self, parent.app, x, y, width, height, parent=parent)

        self.index = index
        self.set_color(random.randrange(0xffffff))

        # start animating
        self.animate()

    # Move the sprite and send an event when we're done.

    def animate(self):
        # Use a step of 50ms to cut down on the number of resources 
        # created. -- wmcbrine
        speed = random.randrange(250, 5250, 50) / 1000.0

        dest_x = random.randrange(self.parent.width)
        dest_y = random.randrange(self.parent.height)
        self.set_bounds(dest_x, dest_y, animtime=speed)

        # send a special event
        self.app.send_key(KEY_TIVO, self.index, animtime=speed)
