# Unlike the hme module, this is a straight port of the version in 
# TiVo's Java SDK. (I've even kept the original comments.) As such, it's 
# a derivative work, released under the Common Public License.
#
# Original version credited authors: Adam Doppelt, Arthur van Hoff, 
# Brigham Stevens, Jonathan Payne, Steven Samorodin
# Copyright 2004, 2005 TiVo Inc.
#
# This version: William McBrine, 2008

from hme import *

TITLE = 'Tic Tac Toe'
CLASS_NAME = 'TicTacToe'

class TicTacToe(Application):
    def startup(self):
        # a View to contain all the pieces
        self.pieces_view = View(self)

        # the pieces themselves
        self.pieces = [[None] * 3, [None] * 3, [None] * 3]

        # the origin of the pieces grid on screen
        self.gridx = (self.root.width - 300) / 2
        self.gridy = 130

        # number of elapsed moves 0-9
        self.num_moves = 0

        # layout the screen
        self.root.set_image('tictactoe/bg.jpg')
        self.root.child(self.gridx - 5, self.gridy - 5, 310, 310,
                        image='tictactoe/grid.png')

        # the X and O pieces
        Font(self, size=72, style=FONT_BOLD)
        self.tokens = [Text(self, 'X'), Text(self, 'O')]

    def handle_key_press(self, keynum, rawcode):
        if KEY_NUM1 <= keynum <= KEY_NUM9:
            pos = keynum - KEY_NUM1;
            # convert pos to x/y and make a move
            self.make_move(pos % 3, pos / 3);
        elif keynum == KEY_LEFT:
            self.active = False
        else:
            self.sound('bonk')

    def make_move(self, x, y):
        # is this a valid move?
        if self.pieces[x][y] is not None:
            self.sound('bonk')
            return
        player = self.num_moves % 2
        self.num_moves += 1

        # create the piece
        self.pieces[x][y] = Piece(self.pieces_view,
                                  self.gridx + (x * 100),
                                  self.gridy + (y * 100),
                                  100, 100, player)
        # is the game over?
        victory = self.is_victory()
        draw = not victory and self.num_moves == 9
        if victory or draw:
            if victory:
                snd = 'tivo'
            else:
                snd = 'thumbsdown'
            self.sound(snd)

            self.sleep(2)

            # if this is a victory, explode the pieces
            # if this is a victory or a draw, make the pieces fade away
            anim = Animation(self, 1)
            for i in xrange(3):
                for j in xrange(3):
                    v = self.pieces[i][j]
                    if v is not None:
                        if victory:
                            v.set_bounds(v.xpos + (i - 1) * 400,
                                         v.ypos + (j - 1) * 300,
                                         animation=anim)
                        v.set_transparency(1, anim)
                        v.remove(anim)
                        self.pieces[i][j] = None

            self.num_moves = 0

    # Returns true if there is a victory on the board.

    def is_victory(self):
        for i in xrange(3):
            if (self.is_victory_run(0, i, 1, 0) or
                self.is_victory_run(i, 0, 0, 1)):
                return True

        return (self.is_victory_run(0, 0, 1, 1) or
                self.is_victory_run(0, 2, 1, -1))

    # Return true if there is a victory (three pieces in a row) starting 
    # at ox,oy and proceeding according to dx,dy. This will highlight 
    # the winning moves if there is a victory.

    def is_victory_run(self, ox, oy, dx, dy):
        x = ox
        y = oy
        for i in xrange(3):
            if self.pieces[x][y] is None:
                return False
            if (i and self.pieces[x][y].player !=
                      self.pieces[x - dx][y - dy].player):
                return False
            x += dx
            y += dy

        # yes - we win! highlight the pieces.
        x = ox
        y = oy
        for i in xrange(3):
            self.pieces[x][y].set_color(0xffa000)
            x += dx
            y += dy

        return True

# An X or O piece. Notice that the X/O is placed in a child instead of 
# in the view itself. We do this so that we can highlight the background
# of the piece later by calling set_resource().

class Piece(View):
    def __init__(self, parent, x, y, w, h, player):
        View.__init__(self, parent.app, x, y, w, h, parent=parent)
        self.player = player
        self.child(resource=self.app.tokens[player])
