import time

from hme import *

TITLE = 'HME for Python'

KEY_NAMES = {0: 'KEY_UNKNOWN', 2: 'KEY_UP', 3: 'KEY_DOWN', 4: 
             'KEY_LEFT', 5: 'KEY_RIGHT', 6: 'KEY_SELECT', 7: 'KEY_PLAY', 8: 
             'KEY_PAUSE', 9: 'KEY_SLOW', 10: 'KEY_REVERSE', 11: 
             'KEY_FORWARD', 12: 'KEY_REPLAY', 13: 'KEY_ADVANCE', 14: 
             'KEY_THUMBSUP', 15: 'KEY_THUMBSDOWN', 16: 'KEY_VOLUMEUP', 
             17: 'KEY_VOLUMEDOWN', 18: 'KEY_CHANNELUP', 19: 
             'KEY_CHANNELDOWN', 20: 'KEY_MUTE', 21: 'KEY_RECORD', 22: 
             'KEY_OPT_WINDOW', 25: 'KEY_INFO', 28: 'KEY_CLEAR', 29: 
             'KEY_ENTER', 40: 'KEY_NUM0', 41: 'KEY_NUM1', 42: 
             'KEY_NUM2', 43: 'KEY_NUM3', 44: 'KEY_NUM4', 45: 'KEY_NUM5', 
             46: 'KEY_NUM6', 47: 'KEY_NUM7', 48: 'KEY_NUM8', 49: 
             'KEY_NUM9', 51: 'KEY_OPT_STOP', 52: 'KEY_OPT_MENU', 53: 
             'KEY_OPT_TOP_MENU', 54: 'KEY_OPT_ANGLE'}

class Test(Application):
    def startup(self):
        if self.context:
            print self.context.headers

        #self.root.set_image('test/back1.mpg')
        self.root.set_image('test/back1.jpg', flags=RSRC_IMAGE_HFIT)

        safe = View(self, SAFE_TITLE_H, SAFE_TITLE_V,
                    self.root.width - SAFE_TITLE_H * 2,
                    self.root.height - SAFE_TITLE_V * 2)
        safe.set_transparency(1)

        shade = safe.child(colornum=0)
        shade.set_transparency(0.5)

        #TTF(self, 'test/VeraMono.ttf')
        Font(self, size=30)
        Color(self, 0xffffff)

        self.text = safe.child(text='HME for Python. r0x0r')

        safe.set_transparency(0, animtime=500)

        self.safe = safe

        #Sound(self, 'test/ka-ching.raw').play()
        #Stream(self, 'http://%s/test/ka-ching.mp3' % 
        #       self.context.headers['host'])

    def handle_key_release(self, keynum, rawcode):
        if keynum == KEY_LEFT:
            Sound(self, id=ID_LEFT_SOUND).play()
            self.safe.set_transparency(1, animtime=500)
            time.sleep(0.5)
            self.active = False

    def handle_key_press(self, keynum, rawcode=None):
        if keynum != KEY_LEFT:
            self.text.resource.remove()
            self.text.set_text(KEY_NAMES[keynum])
            if keynum == KEY_RIGHT:
                self.text.translate(xincrement=10)
            elif keynum == KEY_DOWN:
                self.text.translate(yincrement=10)
            elif keynum == KEY_UP:
                self.text.translate(yincrement=-10)
            Sound(self).play()

    def handle_key_repeat(self, keynum, rawcode):
        self.handle_key_press(keynum)

    def handle_resolution(self):
        for res in self.resolutions:
            if res == self.current_resolution:
                print '*',
            else:
                print ' ',
            print '%4dx%d %d:%d' % res
        res = (640, 480, 1, 1)
        #res = (704, 480, 40, 33)
        #res = (1280, 720, 1, 1)
        if res in self.resolutions:
            return res
        else:
            return self.current_resolution
