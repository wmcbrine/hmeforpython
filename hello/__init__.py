from hme import *

TITLE = 'Hello World'

class Hello(Application):
    def startup(self):
        Font(self, size=36, style=FONT_BOLD)
        self.root.set_text('Hello, world!')
