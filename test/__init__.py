# My test app for whatever. Contents will change randomly from version 
# to version. Old commented-out stuff will sometimes hang around, 
# sometimes not.

import random

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
             'KEY_OPT_TOP_MENU', 54: 'KEY_OPT_ANGLE', 56: 'KEY_OPT_A',
             57: 'KEY_OPT_B', 58: 'KEY_OPT_C', 59: 'KEY_OPT_D', 60: 
             'KEY_OPT_TV_POWER', 61: 'KEY_OPT_TV_INPUT', 62: 
             'KEY_OPT_VOD', 63: 'KEY_OPT_POWER', 65: 'KEY_BACKSPACE'}

class Test(Application):
    def startup(self):
        if self.context:
            print self.context.headers

        #self.root.set_image('test/back1.mpg')
        self.root.set_image('test/back1.jpg', flags=RSRC_IMAGE_HFIT)

        #dancer = Image(self, 'test/tapdancer.gif')
        #self.silly = []
        #for i in xrange(10):
        #    self.silly.append(self.root.child(resource=dancer))
        #    self.update_silly(i)

        safe = View(self, SAFE_TITLE_H, SAFE_TITLE_V,
                    self.root.width - SAFE_TITLE_H * 2,
                    self.root.height - SAFE_TITLE_V * 2, transparency=1)

        shade = safe.child(colornum=0, transparency=0.5)

        #TTF(self, 'test/VeraMono.ttf')
        Font(self, size=30)
        Color(self, 0xffffff)

        self.text = safe.child(text='HME for Python. r0x0r')

        safe.set_transparency(0, animtime=0.5)

        self.safe = safe

        #Sound(self, 'test/ka-ching.raw').play()
        #Stream(self, 'http://%s/test/ka-ching.mp3' % 
        #       self.context.headers['host'])

    def handle_key_release(self, keynum, rawcode):
        if keynum == KEY_LEFT:
            self.sound('left')
            self.safe.set_transparency(1, animtime=0.5)
            self.sleep(0.5)
            self.active = False

    def handle_key_press(self, keynum, rawcode=None):
        if keynum == KEY_TIVO:
            self.update_silly(rawcode)
        elif keynum != KEY_LEFT:
            self.text.resource.remove()
            if keynum == KEY_UNKNOWN:
                key = qwerty_map(rawcode)
            elif keynum in KEY_NAMES:
                key = KEY_NAMES[keynum]
            elif keynum > 0x10000:
                key = chr(keynum - 0x10000)
            else:
                key = str(keynum)
            self.text.set_text(key)
            if keynum == KEY_RIGHT:
                self.text.translate(xincrement=10)
            elif keynum == KEY_DOWN:
                self.text.translate(yincrement=10)
            elif keynum == KEY_UP:
                self.text.translate(yincrement=-10)
            self.sound()

    def handle_resolution(self):
        for res in self.resolutions:
            if res == self.current_resolution:
                print '*',
            else:
                print ' ',
            print '%4dx%d %d:%d' % res
        print
        res = (640, 480, 1, 1)
        #res = (704, 480, 40, 33)
        #res = (1280, 720, 1, 1)
        if res in self.resolutions:
            return res
        else:
            return self.current_resolution

    def handle_active(self):
        print "Receiver says we're active"
        print

    def handle_app_info(self, info):
        for key in info:
            print key, '=', info[key]
        print

    def handle_error(self, code, text):
        print code, text
        print

    def handle_device_info(self, info):
        self.handle_app_info(info)

    def handle_resource_info(self, resource, status, info):
        print resource, status
        self.handle_app_info(info)

    def update_silly(self, index):
        new_x = random.randrange(-self.root.width / 2, self.root.width / 2)
        new_y = random.randrange(-self.root.height / 2, self.root.height / 2)
        speed = random.randrange(2000, 8000, 100) / 1000.0
        self.silly[index].set_translation(new_x, new_y, animtime=speed)
        self.send_key(KEY_TIVO, index, animtime=speed)
