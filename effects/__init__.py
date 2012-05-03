# Unlike the hme module, this is a straight port of the version in 
# TiVo's Java SDK. (I've even kept the original comments.) As such, it's 
# a derivative work, released under the Common Public License.
#
# Original version credited authors: Adam Doppelt, Arthur van Hoff, 
# Brigham Stevens, Jonathan Payne, Steven Samorodin
# Copyright 2004, 2005 TiVo Inc.
#
# This version: William McBrine, 2008-2012

import thread

import hme

"""Illustrates animation effects with ease on Views.

   When changing many properties of a view the change can be animated
   instead of instant, with the change happening incrementally over a 
   specified period.
 
   The reciever will perform the animation with linear interpolation 
   when ease is set to 0 (or no ease at all). Adjusting the ease allows 
   you to animate with acceleration and deceleration.
 
   This sample shows how to use animation when changing the following 
   properties of a view:

   bounds
   translate
   transparency
   scale
   visible
   translation
   remove from parent view

"""

class Effects(hme.Application):
    def handle_device_info(self, info):
        ver = info.get('version', '')
        if ver[:3] in ('9.1', '9.3') and not ver[-3:] in ('648', '652'):
            self.root.set_text('Sorry, this program is not compatible\n' +
                               'with this TiVo software/hardware version.')
            self.sleep(5)
            self.active = False
            return

        # Prepare our view & container
        self.root.set_color()

        hme.Font(self, size=17)

        # Container for everything inset to title-safe
        self.content = hme.View(self, hme.SAFE_TITLE_H, hme.SAFE_TITLE_V,
                                self.root.width - hme.SAFE_TITLE_H * 2,
                                self.root.height - hme.SAFE_TITLE_V * 2)

        # The current ease value
        self.ease = 0

        # Animation time
        self.anim_time = 1

        # Create the views for each demonstration -- each view is used 
        # for demonstrating a different property.

        # Displays the current ease value
        self.ease_text = self.content.child(300, 0, 190, 20)

        # Displays current animation animTime
        self.time_text = self.content.child(300, 20, 190, 20)

        self.transparency = Square(self.content, 0, 0, 90, 90, 'Transparency')
        self.visible = Square(self.content, 100, 0, 90, 90, 'Visible')
        self.bounds = Square(self.content, 300, 100, 90, 90, 'Bounds')
        self.translate = self.content.child(0, 100, 290, 90)
        Square(self.translate, -300, 0, 600, 90, bg=hme.Color(self, 0x00ff00))
        Square(self.translate, 0, 0, 90, 90, 'Translate')
        self.scale = Square(self.content, 0, 200, 90, 90, 'Scale')

        # Kick off the thread to update the effects animation
        thread.start_new_thread(self.update, ())

    # Arrow keys control the ease.  The animation resource is updated 
    # with the new ease. The value of ease and animTime are updated on 
    # screen, but since the settings don't take effect until the current 
    # animation ends they are displayed in Red.

    def handle_key_press(self, code, rawcode):
        deltaD = 0
        deltaE = 0

        if code == hme.KEY_UP:
            deltaD = 0.25
        elif code == hme.KEY_DOWN:
            deltaD = -0.25
        elif code == hme.KEY_RIGHT:
            deltaE = 0.1
        elif code == hme.KEY_LEFT:
            deltaE = -0.1
        elif code in (hme.KEY_CLEAR, hme.KEY_PAUSE):
            self.sound('left')
            self.active = False

        if deltaD or deltaE:
            self.ease = max(min(self.ease + deltaE, 1.0), -1.0)
            self.anim_time = max(min(self.anim_time + deltaD, 9.75), 1.0)
            self.show_settings(0xff0000)

    # Update the demo view animations and sleep until they are finished.
    # Then reverse the animations and do it again.

    def update(self):
        parity = False
        while self.active:
            parity = not parity

            # Create the animation resource from current settings. This 
            # method of creating the resource is the most efficient 
            # because the receiver will use a cached resource if it has 
            # one already.
            anim = hme.Animation(self, self.anim_time, self.ease)

            # Update the animations for each property, alternating. All 
            # of these animations use the shared animation resource.
            self.transparency.set_transparency(int(parity), anim)
            self.visible.set_visible(int(not parity), anim)
            self.translate.set_translation(200 * int(parity), 0, anim)
            if parity:
                newscale = 1.5
            else:
                newscale = 1
            self.scale.set_scale(newscale, newscale, anim)

            if parity:
                # add and remove this square in the future specified by 
                # the animation
                Square(self.content, 200, 0, 90, 90, 'Remove').remove(anim)
                self.bounds.set_bounds(300, 150, 190, 190, anim)
            else:
                self.bounds.set_bounds(300, 100, 90, 90, anim)

            # Display the current animTime & ease in black to indicate 
            # it has taken effect.
            self.show_settings(0)
            self.sleep(self.anim_time)

    # Display the value of the ease and animTime in the given color.

    def show_settings(self, color):
        hme.Color(self, color)
        self.ease_text.set_text('Ease (use left/right) : %.1f' % self.ease,
                                flags=hme.RSRC_HALIGN_LEFT)
        self.time_text.set_text('Time (use up/down) : %.2f' % self.anim_time,
                                flags=hme.RSRC_HALIGN_LEFT)


# This class handles the animated squares with text.

class Square(hme.View):
    def __init__(self, parent, x, y, w, h, title='', bg=None):
        hme.View.__init__(self, parent.app, x, y, w, h, parent=parent)
        if bg is None:
            bg = hme.Color(self.app, 0xff00ff)  # magenta
        self.set_resource(bg)
        self.label = self.child()
        if title:
            self.label.set_text(title, color=hme.Color(self.app))
