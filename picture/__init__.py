# This one is NOT ported from the Java SDK. But portions are based on my 
# Photo module for pyTivo.
#
# Set ROOT to the directory you want to view. Yeah, if this were a 
# full-blown app, you'd want a better way to do that. But this is just a 
# demo.

import os
import random
import time
from cStringIO import StringIO

import Image

import hme

TITLE = 'Picture Viewer'
ROOT = '/home/wmcbrine/pictures'

""" Simple slideshow picture viewer. Automatically uses high-def mode
    when available and appropriate, based on the TiVo's notion of the
    optimal resolution. Requires the Python Imaging Library. Loops
    forever, but any key breaks the loop (Play restarts it); Fast
    Forward and Rewind allow simple manual navigation.

"""

if not os.path.isdir(ROOT):
    raise ImportError, 'Please set ROOT to a valid directory'

class Picture(hme.Application):
    def handle_resolution(self):
        """ Choose the 'optimal' resolution. """
        return self.resolutions[0]

    def handle_active(self):
        """ Build the list of pictures, and start the slideshow. """
        goodexts = ('.jpg', '.gif', '.png', '.bmp', '.tif', '.xbm',
                    '.xpm', '.pgm', '.pbm', '.ppm', '.pcx', '.tga',
                    '.fpx', '.ico', '.pcd', '.jpeg', '.tiff')

        self.files = []
        for base, dirs, files in os.walk(ROOT):
            self.files.extend([os.path.join(base, x) for x in files 
                               if os.path.splitext(x)[1].lower() in goodexts])

        random.shuffle(self.files)

        self.old = None
        self.count = -1
        self.start_slideshow()

    def handle_key_press(self, code, rawcode):
        """ Handle a real keypress OR the pseudo-key that's sent five 
            seconds after the last slide.

        """
        if code == hme.KEY_TIVO and self.in_slideshow:
            self.next_slide()
        elif code == hme.KEY_PLAY:
            if self.in_slideshow:
                self.exit_slideshow()
            else:
                self.sound(hme.ID_SELECT_SOUND)
                self.start_slideshow()
        else:
            if self.in_slideshow:
                self.exit_slideshow()
            if code == hme.KEY_FORWARD:
                self.sound(hme.ID_RIGHT_SOUND)
                self.newpic(1)
            elif code == hme.KEY_REVERSE:
                self.sound(hme.ID_LEFT_SOUND)
                self.newpic(-1)

    def handle_idle(self, idle):
        if idle:
            # If entering idle mode during a slideshow, ignore it;
            # if on a still frame, exit the app...
            return self.in_slideshow
        else:
            # ...but we can always handle exiting idle mode.
            return True

    def handle_error(self, code, text):
        print code, text
        self.active = False

    def makepic(self):
        """ Re-encode the picture at self.count to fit the screen. """
        width, height, pixw, pixh = self.current_resolution
        width -= hme.SAFE_TITLE_H
        height -= hme.SAFE_TITLE_V

        pic = Image.open(self.files[self.count])
        pic.draft('RGB', (width, height))
        if pic.mode == 'P':
            pic = pic.convert()
        oldw, oldh = pic.size
        oldw *= pixh
        oldh *= pixw
        ratio = float(oldw) / oldh
        if float(width) / height < ratio:
             height = int(width / ratio)
        else:
             width = int(height * ratio)
        pic = pic.resize((width, height), Image.ANTIALIAS)
        out = StringIO()
        pic.save(out, 'JPEG')
        encoded = out.getvalue()
        out.close()
        return encoded

    def newpic(self, direction):
        """ Show the next (or previous) pic from self.files. """
        new = self.root.child()

        # Loop until a valid picture is found
        while True:
            self.count += direction
            self.count %= len(self.files)
            try:
                encoded = self.makepic()
            except Exception, msg:
                print 'Skipping %s: %s' % (self.files[self.count], msg)
            else:
                break

        # Fade in the new pic
        new.set_transparency(1)
        new.set_image(data=encoded)
        new.set_transparency(0, animtime=0.5)

        # Fade out the old
        if self.old:
            self.old.set_transparency(1, animtime=0.5)
            self.old.remove(animtime=0.5)
            self.wfile.flush()
            time.sleep(0.75)
            self.old.resource.remove()
        self.old = new

    def start_slideshow(self):
        self.in_slideshow = True
        self.next_slide()

    def next_slide(self):
        self.newpic(1)
        self.send_key(hme.KEY_TIVO, animtime=5)

    def exit_slideshow(self):
        self.sound(hme.ID_SLOWDOWN1_SOUND)
        self.in_slideshow = False
