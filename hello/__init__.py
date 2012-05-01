import hme

TITLE = 'Hello World'

class Hello(hme.Application):
    def startup(self):
        hme.Font(self, size=36, style=hme.FONT_BOLD)
        self.root.set_text('Hello, world!')
