# HME for Python, v0.19
# Copyright 2010 William McBrine
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You didn't receive a copy of the license with this library because 
# you already have dozens of copies, don't you? If not, visit gnu.org.

""" HME for Python

    An implementation of TiVo's HME ("Home Media Extensions") Protocol
    for Python. This is based on the protocol specification, but it is
    not a port of the Java SDK, and it does things somewhat differently.
    (Starting from the spec, I did end up with a lot of similarities to
    the SDK, and I then tweaked this module to bring them closer, in
    some respects; but there are still a lot of differences.)

    Basic usage: import hme (or "from hme import *"); subclass the
    "Application" class; and override some of the stub functions that
    appear at the end of this file. (startup() and handle_key_press()
    are the most useful.) If you want to use it with the included
    hmeserver.py, then your program should be in the form of a module
    (see the included examples). Aside from the app class, you may want
    to include TITLE and/or CLASS_NAME strings; TITLE is the display
    title, and CLASS_NAME is the name of your main app class. (Both will
    be derived from the module name if absent.)

    startup() is called first, after the initial events are handled;
    then the event loop runs until either it's out of events (i.e. the
    socket closed), or you set self.active to False. Finally, cleanup()
    is called.

    Items not yet implemented from the spec:
    * Event pushing other than key presses

    Java SDK items not in the spec and not implemented here:
    * Persistent data -- you can get the tsn and Cookie from 
      self.context.headers, if using hmeserver.py, but what you do with
      them is outside the scope of this module
    * Numerous specific methods -- but some of these are unneeded; e.g., 
      set_bounds() substitutes for setLocation() as well as setBounds()

"""

__author__ = 'William McBrine <wmcbrine@gmail.com>'
__version__ = '0.19'
__license__ = 'LGPL'

import time
import string
import struct

#--- Constants --------------------------------------------------------
#
# Mostly as defined in the HME Protocol Specification.

HME_MAJOR_VERSION = 0
HME_MINOR_VERSION = 49

SAFE_ACTION_H = 32
SAFE_ACTION_V = 24
SAFE_TITLE_H = 64
SAFE_TITLE_V = 48

# Default object IDs

ID_NULL = 0
ID_ROOT_STREAM = 1
ID_ROOT_VIEW = 	2
ID_DEFAULT_TTF = 10
ID_SYSTEM_TTF = 11

ID_BONK_SOUND = 20
ID_UPDOWN_SOUND = 21
ID_THUMBSUP_SOUND = 22
ID_THUMBSDOWN_SOUND = 23
ID_SELECT_SOUND = 24
ID_TIVO_SOUND = 25
ID_LEFT_SOUND = 26
ID_RIGHT_SOUND = 27
ID_PAGEUP_SOUND = 28
ID_PAGEDOWN_SOUND = 29
ID_ALERT_SOUND = 30
ID_DESELECT_SOUND = 31
ID_ERROR_SOUND = 32
ID_SLOWDOWN1_SOUND = 33
ID_SPEEDUP1_SOUND = 34
ID_SPEEDUP2_SOUND = 35
ID_SPEEDUP3_SOUND = 36

ID_CLIENT = 2048

# Key actions

KEY_PRESS = 1
KEY_REPEAT = 2
KEY_RELEASE = 3

# Key codes

KEY_UNKNOWN = 0
KEY_TIVO = 1  # not sent
KEY_UP = 2
KEY_DOWN = 3
KEY_LEFT = 4
KEY_RIGHT = 5
KEY_SELECT = 6
KEY_PLAY = 7
KEY_PAUSE = 8
KEY_SLOW = 9
KEY_REVERSE = 10
KEY_FORWARD = 11
KEY_REPLAY = 12
KEY_ADVANCE = 13
KEY_THUMBSUP = 14
KEY_THUMBSDOWN = 15
KEY_VOLUMEUP = 16
KEY_VOLUMEDOWN = 17
KEY_CHANNELUP = 18
KEY_CHANNELDOWN = 19
KEY_MUTE = 20
KEY_RECORD = 21
KEY_OPT_WINDOW = 22
KEY_OPT_PIP = KEY_OPT_WINDOW
KEY_OPT_ASPECT = KEY_OPT_WINDOW
KEY_LIVE_TV = 23  # not sent
KEY_OPT_EXIT = 24  # not sent
KEY_INFO = 25
KEY_DISPLAY = KEY_INFO
KEY_OPT_LIST = 26  # not sent
KEY_OPT_GUIDE = 27  # not sent
KEY_CLEAR = 28
KEY_ENTER = 29
KEY_NUM0 = 40
KEY_NUM1 = 41
KEY_NUM2 = 42
KEY_NUM3 = 43
KEY_NUM4 = 44
KEY_NUM5 = 45
KEY_NUM6 = 46
KEY_NUM7 = 47
KEY_NUM8 = 48
KEY_NUM9 = 49
KEY_OPT_STOP = 51
KEY_OPT_MENU = 52
KEY_OPT_TOP_MENU = 53
KEY_OPT_ANGLE = 54
KEY_OPT_DVD = 55  # not sent
KEY_OPT_A = 56
KEY_OPT_B = 57
KEY_OPT_C = 58
KEY_OPT_D = 59
KEY_OPT_TV_POWER = 60
KEY_OPT_TV_INPUT = 61
KEY_OPT_VOD = 62
KEY_OPT_POWER = 63

KEY_BACKSPACE = 65

# Transitions

TRANSITION_FORWARD = 1
TRANSITION_BACK = 2
TRANSITION_TELEPORT = 3

# Application errors

APP_ERROR_UNKNOWN = 0
APP_ERROR_BAD_ARGUMENT = 1
APP_ERROR_BAD_COMMAND = 2
APP_ERROR_RSRC_NOT_FOUND = 3
APP_ERROR_VIEW_NOT_FOUND = 4
APP_ERROR_OUT_OF_MEMORY = 5
APP_ERROR_INVALID_TRANSITION = 6
APP_ERROR_INVALID_RESOLUTION = 7
APP_ERROR_OTHER = 100

# Resource flags

RSRC_HALIGN_LEFT = 1
RSRC_HALIGN_CENTER = 2
RSRC_HALIGN_RIGHT = 4
RSRC_VALIGN_TOP = 0x10
RSRC_VALIGN_CENTER = 0x20
RSRC_VALIGN_BOTTOM = 0x40
RSRC_TEXT_WRAP = 0x0100
RSRC_IMAGE_HFIT = 0x1000
RSRC_IMAGE_VFIT = 0x2000
RSRC_IMAGE_BESTFIT = 0x4000

# Resource states

RSRC_STATUS_UNKNOWN = 0
RSRC_STATUS_CONNECTING = 1
RSRC_STATUS_CONNECTED = 2
RSRC_STATUS_LOADING = 3
RSRC_STATUS_READY = 4
RSRC_STATUS_PLAYING = 5
RSRC_STATUS_PAUSED = 6
RSRC_STATUS_SEEKING = 7
RSRC_STATUS_CLOSED = 8
RSRC_STATUS_COMPLETE = 9
RSRC_STATUS_ERROR = 10

# Resource errors

RSRC_ERROR_UNKNOWN = 0
RSRC_ERROR_BAD_DATA = 1
RSRC_ERROR_BAD_MAGIC = 2
RSRC_ERROR_BAD_VERSION = 3
RSRC_ERROR_CONNECTION_LOST = 4
RSRC_ERROR_CONNECTION_TIMEOUT = 5
RSRC_ERROR_CONNECT_FAILED = 6
RSRC_ERROR_HOST_NOT_FOUND = 7
RSRC_ERROR_INCOMPATIBLE = 8
RSRC_ERROR_NOT_SUPPORTED = 9
RSRC_ERROR_BAD_ARGUMENT = 20
RSRC_ERROR_BAD_STATE = 	21

# Font styles

FONT_PLAIN = 0
FONT_BOLD = 1
FONT_ITALIC = 2
FONT_BOLDITALIC = 3

# Bitwise flags for _CMD_RSRC_ADD_FONT: data to return in _EVT_FONT_INFO. 
# (This is not documented in the HME spec.) Without setting one or both 
# of these flags, no _EVT_FONT_INFO is returned.

FONT_METRICS_BASIC = 1
FONT_METRICS_GLYPH = 2

#--- Private constants ------------------------------------------------

# Commands

_CMD_VIEW_ADD = 1
_CMD_VIEW_SET_BOUNDS = 2
_CMD_VIEW_SET_SCALE = 3
_CMD_VIEW_SET_TRANSLATION = 4
_CMD_VIEW_SET_TRANSPARENCY = 5
_CMD_VIEW_SET_VISIBLE = 6
_CMD_VIEW_SET_PAINTING = 7
_CMD_VIEW_SET_RESOURCE = 8
_CMD_VIEW_REMOVE = 9

_CMD_RSRC_ADD_COLOR = 20
_CMD_RSRC_ADD_TTF = 21
_CMD_RSRC_ADD_FONT = 22
_CMD_RSRC_ADD_TEXT = 23
_CMD_RSRC_ADD_IMAGE = 24
_CMD_RSRC_ADD_SOUND = 25
_CMD_RSRC_ADD_STREAM = 26
_CMD_RSRC_ADD_ANIM = 27

_CMD_RSRC_SET_ACTIVE = 40
_CMD_RSRC_SET_POSITION = 41
_CMD_RSRC_SET_SPEED = 42

_CMD_RSRC_SEND_EVENT = 44
_CMD_RSRC_CLOSE = 45
_CMD_RSRC_REMOVE = 46

_CMD_RECEIVER_ACKNOWLEDGE_IDLE = 60
_CMD_RECEIVER_TRANSITION = 61
_CMD_RECEIVER_SET_RESOLUTION = 62

# Events

_EVT_DEVICE_INFO = 1
_EVT_APP_INFO = 2
_EVT_RSRC_INFO = 3
_EVT_KEY = 4
_EVT_IDLE = 5
_EVT_FONT_INFO = 6
_EVT_INIT_INFO = 7
_EVT_RESOLUTION_INFO = 8

# Characters for codes returned by QWERTY input

_QWERTY_MAP = string.uppercase + "-=[]\;',./` "

def qwerty_map(rawcode):
    try:
        key = _QWERTY_MAP[((rawcode & 0xff00) >> 8) - 0x3c]
    except:
        key = '?'
    return key

#--- Low-level stream handling ----------------------------------------

class _EventData:
    """ Take raw event data and allow various Python types to be 
        extracted from it.

    """
    def __init__(self, data):
        self.data = data
        self.index = 0

    def next(self):
        c = ord(self.data[self.index])
        self.index += 1
        return c

    def unpack_bool(self):
        """ HME boolean to bool """
        return bool(self.next())

    def unpack_vint(self):
        """ HME variable-length integer to int """
        value = 0
        shift = 0
        while True:
            c = self.next()
            if c & 0x80:
                break
            value += c << shift
            shift += 7
        value += (c & 0x3f) << shift
        if c & 0x40:
            value = -value
        return value

    def unpack_vuint(self):
        """ HME variable-length unsigned integer to int """
        value = 0
        shift = 0
        while True:
            c = self.next()
            if c & 0x80:
                break
            value += c << shift
            shift += 7
        value += (c & 0x7f) << shift
        return value

    def unpack_float(self):
        """ HME float to float """
        value = struct.unpack('!f', self.data[self.index:self.index + 4])[0]
        self.index += 4
        return value

    def unpack_vdata(self):
        """ HME variable-length data to str """
        length = self.unpack_vuint()
        result = self.data[self.index:self.index + length]
        self.index += length
        return result

    def unpack_string(self):
        """ HME string to unicode """
        return self.unpack_vdata().decode('utf-8')

    def unpack_dict(self):
        """ HME dict to dict (each value may be a list)
            Note that the HME dict type is referred to, but not
            documented, in the HME protocol specification.

        """
        d = {}
        while True:
            key = self.unpack_string()
            if not key:
                break
            value = []
            while True:
                c = self.next()
                if not c:
                    break
                if c == 1:
                    value.append(self.unpack_string())
                else:
                    value.append(self.unpack_dict())
            if len(value) == 1:
                value = value[0]
            d[key] = value
        return d

    def unpack(self, format):
        """ Unpack a list of types, based on a format string. """
        func = {'b': self.unpack_bool,
                'i': self.unpack_vint,
                'f': self.unpack_float,
                'v': self.unpack_vdata,
                's': self.unpack_string,
                'd': self.unpack_dict}

        return [func[i]() for i in format]

def _get_chunked(stream):
    """ Read HME-style chunked event data from the input stream. """
    data = ''
    while True:
        # Get the next chunk length
        try:
            length = struct.unpack('!H', stream.read(2))[0]
        except:
            return None

        # A zero-length chunk marks the end of the event
        if not length:
            return data

        # Otherwise, append the new chunk
        try:
            data += stream.read(length)
        except:
            return None

def _pack_bool(value):
    """ bool to HME boolean """
    return chr(value)

def _pack_vint(value):
    """ int to HME variable-length integer """
    value = int(value)
    result = ''
    is_neg = value < 0
    if is_neg:
        value = -value
    while value > 0x3f:
        result += chr(value & 0x7f)
        value >>= 7
    if is_neg:
        value |= 0x40
    result += chr(value | 0x80)
    return result

def _pack_vuint(value):
    """ int to HME variable-length unsigned integer """
    value = int(value)
    result = ''
    while value > 0x7f:
        result += chr(value & 0x7f)
        value >>= 7
    result += chr(value | 0x80)
    return result

def _pack_float(value):
    """ float to HME float """
    return struct.pack('!f', float(value))

def _pack_vdata(value):
    """ str to HME variable-length data """
    return _pack_vuint(len(value)) + value

def _pack_string(value):
    """ unicode to HME string """
    if not type(value) in (str, unicode):
        value = str(value)
    return _pack_vdata(value.encode('utf-8'))

def _pack_dict(value):
    """ dict (of lists) to HME dict """
    result = ''
    if type(value) != dict:
        raise TypeError, 'must be a dict'
    # The keys must be sorted, or the TiVo ignores the transition.
    keys = value.keys()
    keys.sort()
    for key in keys:
        result += _pack_string(key)
        items = value[key]
        if type(items) != list:
            items = [items]
        for item in items:
            if type(item) == dict:
                result += chr(2)
                result += _pack_dict(item)
            else:
                result += chr(1)
                result += _pack_string(item)
        result += chr(0)
    result += _pack_string('')
    return result

def _pack_raw(value):
    """ Return the data as-is. """
    return value

def _pack(format, *values):
    """ Pack a list of types, based on a format string. """
    func = {'b': _pack_bool,
            'i': _pack_vint,
            'f': _pack_float,
            'v': _pack_vdata,
            's': _pack_string,
            'd': _pack_dict,
            'r': _pack_raw}

    return ''.join([func[i](value) for i, value in zip(format, values)])

def _put_chunked(stream, data):
    """ Write HME-style chunked data to the output stream. """
    MAXSIZE = 0xfffe
    size = len(data)
    index = 0
    while size:
        blocksize = min(size, MAXSIZE)
        try:
            stream.write(struct.pack('!H', blocksize))
            stream.write(data[index:index + blocksize])
        except:
            return
        index += blocksize
        size -= blocksize
    try:
        stream.write('\0\0')
    except:
        pass

#--- Resource classes -------------------------------------------------

class _HMEObject:
    """ Base class for Resources and Views
        If the id is specified, it's used; otherwise the next available
        id is fetched from the app.

        The need to specify the app here results in a slew of "self"
        parameters when _HMEObjects are being constructed -- probably
        the ugliest aspect of this module.

    """
    def __init__(self, app, id=None):
        if id is None:
            self.id = app.next_resnum()
        else:
            self.id = id
        self.app = app

    def put(self, cmd, format='', *params):
        """ Send a command (cmd) with the current resource id and 
            specified parameters, if any. The parameters are packed 
            according to the format string.

        """
        _put_chunked(self.app.wfile,
                     _pack('ii' + format, cmd, self.id, *params))

class Resource(_HMEObject):
    """ Base class for Resources
        Note that in this implementation, resources are never removed 
        automatically; you have to call the remove() method.

    """
    def __init__(self, app, id=None):
        _HMEObject.__init__(self, app, id)
        self.speed = 0

    def set_active(self, make_active=True):
        self.put(_CMD_RSRC_SET_ACTIVE, 'b', make_active)

    def set_position(self, position):
        self.put(_CMD_RSRC_SET_POSITION, 'i', position)

    def set_speed(self, speed):
        self.put(_CMD_RSRC_SET_SPEED, 'f', speed)
        self.speed = speed
        try:
            self.app.wfile.flush()
        except:
            pass

    def close(self):
        self.put(_CMD_RSRC_CLOSE)

    def remove(self):
        if self.id >= ID_CLIENT:
            self.put(_CMD_RSRC_REMOVE)
            self.id = -1

    def play(self):
        self.set_speed(1)

    def pause(self):
        self.set_speed(0)

class Color(Resource):
    """ Color resource
        The colornum is specified as an integer in standard web R/G/B 
        format (most convenient as hex). If none is given, white (the 
        typical font color for the TiVo interface) is used. Color 
        objects are cached in the app.colors dict, and the last one set 
        is also stored in app.last_color.

        You can include an alpha value as the MSB. Zero is treated as
        0xff (fully opacity) by this library; otherwise, lower numbers
        mean greater transparency.

    """
    def __init__(self, app, colornum=None):
        if colornum is None:
            colornum = 0xffffffff
        if not (colornum & 0xff000000):
            colornum |= 0xff000000
        self.colornum = colornum
        if colornum in app.colors:
            Resource.__init__(self, app, app.colors[colornum].id)
        else:
            Resource.__init__(self, app)
            self.put(_CMD_RSRC_ADD_COLOR, 'r', struct.pack('!I', colornum))
            app.colors[colornum] = self
        app.last_color = self

    def remove(self):
        Resource.remove(self)
        self.app.colors.pop(self.colornum)
        if self.app.last_color == self:
            self.app.last_color = None

class TTF(Resource):
    """ TrueType font file resource
        Specified by data, file object, file name or id. If none is
        given, ID_DEFAULT_TTF is used. TTF objects specified by name are
        cached in the app.ttfs dict, and the last TTF set is stored in
        app.last_ttf.

    """
    def __init__(self, app, name=None, f=None, data=None, id=None):
        if name is None and f is None and data is None and id is None:
            id = ID_DEFAULT_TTF
        self.name = name
        if name and name in app.ttfs:
            Resource.__init__(self, app, app.ttfs[name].id)
        else:
            Resource.__init__(self, app, id)
            if id is None:
                if data is None:
                    if f is None:
                        f = open(name, 'rb')
                    data = f.read()
                self.put(_CMD_RSRC_ADD_TTF, 'r', data)
                if name:
                    app.ttfs[name] = self
        app.last_ttf = self

    def remove(self):
        if self.name:
            Resource.remove(self)
            self.app.ttfs.pop(self.name)
            if self.app.last_ttf == self:
                self.app.last_ttf = None

    def __del__(self):
        if not self.name:
            Resource.remove(self)

class Font(Resource):
    """ Font resource (with chosen point size and style)
        ttf specifies an object of the TTF class, and defaults to the 
        ID_DEFAULT_TTF object. style can be FONT_ITALIC, FONT_BOLD, or 
        FONT_BOLDITALIC, and defaults to FONT_PLAIN. Font objects are 
        cached in the app.fonts dict, and the last Font set is stored in 
        app.last_font.

    """
    def __init__(self, app, ttf=None, style=FONT_PLAIN, size=24, flags=0):
        if ttf is None:
            ttf = app.last_ttf
            if ttf is None:
                ttf = app.default_ttf
        self.key = (ttf, style, size, flags)
        if self.key in app.fonts:
            Resource.__init__(self, app, app.fonts[self.key].id)
        else:
            Resource.__init__(self, app)
            self.put(_CMD_RSRC_ADD_FONT, 'iifi', ttf.id, style, size, flags)
            app.fonts[self.key] = self
        app.last_font = self

    def remove(self):
        Resource.remove(self)
        self.app.fonts.pop(self.key)
        if self.app.last_font == self:
            self.app.last_font = None

class Text(Resource):
    """ Text resource (with chosen Color and Font)
        If either the color or font is unspecified, the last ones set in 
        the app are used. The color can be specified by number (using 
        colornum=), or as an object of the Color class (color=). The 
        font can only be specified as an object of the Font class.

    """
    def __init__(self, app, text, font=None, color=None, colornum=None):
        Resource.__init__(self, app)
        if color is None:
            if colornum is not None:
                color = Color(app, colornum)
            else:
                color = app.last_color
                if color is None:
                    color = Color(app)
        if font is None:
            font = app.last_font
            if font is None:
                font = Font(app)
        self.put(_CMD_RSRC_ADD_TEXT, 'iis', font.id, color.id, text)

    def __del__(self):
        Resource.remove(self)

class Image(Resource):
    """ Image resource
        Specified by data, file object or file name, one of which must 
        be given. Image objects specified by name are cached in the 
        app.images dict.

    """
    def __init__(self, app, name=None, f=None, data=None):
        self.name = name
        if name is None and f is None and data is None:
            raise Exception, 'No image specified for Image resource'
        if name and name in app.images:
            Resource.__init__(self, app, app.images[name].id)
        else:
            Resource.__init__(self, app)
            if data is None:
                if f is None:
                    f = open(name, 'rb')
                data = f.read()
            self.put(_CMD_RSRC_ADD_IMAGE, 'r', data)
            if name:
                app.images[name] = self

    def remove(self):
        Resource.remove(self)
        if self.name:
            self.app.images.pop(self.name)

    def __del__(self):
        if not self.name:
            Resource.remove(self)

class Sound(Resource):
    """ Sound resource
        Specified by data, file object, file name or id. If none is
        given, ID_UPDOWN_SOUND is used.

        Note that, on a real TiVo, only the predefined sounds seem to
        work. Use a Stream to play your own sounds.

    """
    def __init__(self, app, name=None, f=None, data=None, id=None):
        if data is None and f is None and name is None and id is None:
            id = ID_UPDOWN_SOUND
        Resource.__init__(self, app, id)
        if id is None:
            if data is None:
                if f is None:
                    f = open(name, 'rb')
                data = f.read()
            self.put(_CMD_RSRC_ADD_SOUND, 'r', data)

class Stream(Resource):
    """ Stream resource
        Specified by url. You can also provide the MIME type here, but 
        it doesn't seem to be used. The default is to play the stream 
        automatically when the event is sent; you can change this by 
        specifying "play=False". However, streams seem to be playable 
        only once.

    """
    def __init__(self, app, url, mime='', play=True, params={}):
        Resource.__init__(self, app)
        self.put(_CMD_RSRC_ADD_STREAM, 'ssbd', url, mime, play, params)
        self.speed = int(play)

    def __del__(self):
        Resource.remove(self)

class Animation(Resource):
    """ Animation resource
        Specified by duration in seconds, with optional ease and id.
        (The id is used to initalize a zero-duration object for
        ID_NULL.) Animation objects are cached in the app.anims dict.

    """
    def __init__(self, app, duration, ease=0, id=None):
        self.key = (duration, ease)
        if id is None:
            if self.key in app.anims:
                Resource.__init__(self, app, app.anims[self.key].id)
            else:
                Resource.__init__(self, app)
                self.put(_CMD_RSRC_ADD_ANIM, 'if', duration * 1000, ease)
                app.anims[self.key] = self
        else:
            Resource.__init__(self, app, id)

    def remove(self):
        Resource.remove(self)
        self.app.anims.pop(self.key)

#--- The View class ---------------------------------------------------

class View(_HMEObject):
    """ The View class
        A view is the basic unit of the HME display. It has a size,
        position, and can have an associated resource, which is either a
        Color (i.e., a background color for the entire area), an Image,
        or Text. It can also have children -- views within views. For
        example, the parent view might be set to a background color,
        with its child displaying text.

        For this class, position, size, visibility, parent, and an
        associated resource can be set on initialization; all have
        default values. Each View maintains a list of child Views,
        scale, transparency and translation.

    """
    def __init__(self, app, xpos=0, ypos=0, width=None, height=None,
                 visible=True, parent=None, id=None, resource=None, 
                 text=None, colornum=None, image=None, flags=0,
                 transparency=0):
        _HMEObject.__init__(self, app, id)
        self.children = []
        self.resource = None
        self.xscale = 1
        self.yscale = 1
        self.painting = True
        self.transparency = 0
        self.xtranslation = 0
        self.ytranslation = 0
        if id is None and parent is None:
            parent = app.root
        if parent:
            if app is None:
                app = parent.app
            if width is None:
                width = parent.width - xpos
            if height is None:
                height = parent.height - ypos
        else:
            width, height = app.current_resolution[:2]
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.height = height
        if parent:
            self.put(_CMD_VIEW_ADD, 'iiiiib', parent.id, xpos, ypos,
                     width, height, visible)
            parent.children.append(self)
        else:
            visible = False  # root view starts out not visible
        self.parent = parent
        self.visible = visible
        if transparency:
            self.set_transparency(transparency)
        if resource:
            self.set_resource(resource, flags)
        elif text:
            self.set_text(text, flags=flags)
        elif image:
            self.set_image(image, flags=flags)
        elif colornum is not None:
            self.set_color(colornum)

    def set_bounds(self, xpos=None, ypos=None, width=None, height=None, 
                   animation=None, animtime=0):
        """ Change the size and/or shape of the view, optionally over a
            period of time. The interval can be specified either in
            number of seconds (animtime=), or as an Animation object
            (animation=).

        """
        if xpos is None:
            xpos = self.xpos
        if ypos is None:
            ypos = self.ypos
        if width is None:
            width = self.width
        if height is None:
            height = self.height
        if animation is None:
            if animtime:
                animation = Animation(self.app, animtime)
            else:
                animation = self.app.immediate
        self.put(_CMD_VIEW_SET_BOUNDS, 'iiiii', xpos, ypos, width, height,
                 animation.id)
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.height = height

    def set_scale(self, xscale=None, yscale=None, animation=None,
                  animtime=0):
        """ Scale the view up or down, optionally over a period of time.

        """
        if xscale is None:
            xscale = self.xscale
        if yscale is None:
            yscale = self.yscale
        if animation is None:
            if animtime:
                animation = Animation(self.app, animtime)
            else:
                animation = self.app.immediate
        self.put(_CMD_VIEW_SET_SCALE, 'ffi', xscale, yscale,
                 animation.id)
        self.xscale = xscale
        self.yscale = yscale

    def set_translation(self, xtranslation=0, ytranslation=0, 
                        animation=None, animtime=0):
        """ Set the "translation" of the view, optionally over a period
            of time. What this does is move the contents within the 
            view, while the view itself stays in the same place.

        """
        if (self.xtranslation != xtranslation or
            self.ytranslation != ytranslation):
            if animation is None:
                if animtime:
                    animation = Animation(self.app, animtime)
                else:
                    animation = self.app.immediate
            self.put(_CMD_VIEW_SET_TRANSLATION, 'iii',
                     xtranslation, ytranslation, animation.id)
            self.xtranslation = xtranslation
            self.ytranslation = ytranslation

    def translate(self, xincrement=0, yincrement=0, animation=None,
                  animtime=0):
        """ Translate with relative coordinates, vs. the absolute 
            coordinates used in set_translation().

        """
        self.set_translation(self.xtranslation + xincrement,
                             self.ytranslation + yincrement,
                             animation, animtime)

    def set_transparency(self, transparency, animation=None, animtime=0):
        """ Change the transparency of the view, optionally over a 
            period of time (i.e., fade in/fade out).

        """
        if self.transparency != transparency:
            if animation is None:
                if animtime:
                    animation = Animation(self.app, animtime)
                else:
                    animation = self.app.immediate
            self.put(_CMD_VIEW_SET_TRANSPARENCY, 'fi',
                     transparency, animation.id)
            self.transparency = transparency

    def set_visible(self, visible=True, animation=None, animtime=0):
        """ Make the view visible or invisible, optionally after a 
            period of time.

        """
        if self.visible != visible:
            if animation is None:
                if animtime:
                    animation = Animation(self.app, animtime)
                else:
                    animation = self.app.immediate
            self.put(_CMD_VIEW_SET_VISIBLE, 'bi',
                     visible, animation.id)
            self.visible = visible

    def set_painting(self, painting=True):
        """ Set the view to update on screen (painting=True) or not.
            Use this to perform a series of changes, then make them
            visible all at once. (painting=False differs from
            invisibility in that the old contents of the view remain on
            screen.)

        """
        if self.painting != painting:
            self.put(_CMD_VIEW_SET_PAINTING, 'b', painting)
            self.painting = painting

    def set_resource(self, resource, flags=0):
        """ Set the view's associated resource to a Text, Color or Image 
            object.

        """
        if self.resource is not resource:
            self.put(_CMD_VIEW_SET_RESOURCE, 'ii', resource.id, flags)
            self.resource = resource

    def clear_resource(self):
        """ Disassociate the view from its resource. Does not remove
            the resource.

        """
        if self.resource:
            self.put(_CMD_VIEW_SET_RESOURCE, 'ii', ID_NULL, 0)
            self.resource = None

    def remove_resource(self):
        """ Remove the view's associated resource. """
        if self.resource:
            self.resource.remove()
            self.resource = None

    def remove(self, animation=None, animtime=0):
        """ Remove the view, optionally after a period of time. """
        if animation is None:
            if animtime:
                animation = Animation(self.app, animtime)
            else:
                animation = self.app.immediate
        self.put(_CMD_VIEW_REMOVE, 'i', animation.id)
        if self.parent:
            self.parent.children.remove(self)

    def set_text(self, message, font=None, color=None, colornum=None, flags=0):
        """ Set the view's associated resource to the given message
            text. Font, Color (or colornum) and flags can also be
            specified, but need not be.

        """
        self.set_resource(Text(self.app, message, font, color, colornum), flags)

    def set_image(self, name=None, f=None, data=None, flags=0):
        """ Set the view's associated resource to the given image data,
            file object or file name. Flags can be optionally specified.

        """
        self.set_resource(Image(self.app, name, f, data), flags)

    def set_color(self, colornum=None):
        """ Set the view's associated resource to the given color 
            number.

        """
        self.set_resource(Color(self.app, colornum))

    def child(self, *args, **kwargs):
        """ Create a child View of this one. This is just slightly
            easier to use than calling the View constructor directly:

            aview.child(text='Hello')

            vs.

            View(self, parent=aview, text='Hello')

            with the exception of children of the root View, which is
            the default parent.

        """
        return View(self.app, parent=self, *args, **kwargs)

#--- The Application class --------------------------------------------

class Application(Resource):
    """ The Application class
        Your apps should subclass this. It takes over just after the
        HTTP connection is established, does the HME handshake, sets up
        some default resources and caches for new ones, and handles the
        startup events. (After initialization, you should call the
        mainloop() method to continue handling events.)

        When started from hmeserver.py, the server's handler is passed 
        as context; alternatively, you can pass infile and outfile, and 
        (potentially) start the app from the command line.

    """
    def __init__(self, infile=None, outfile=None, context=None):
        Resource.__init__(self, self, ID_ROOT_STREAM)

        self.resnum = ID_CLIENT

        self.context = context
        if context is not None:
            self.rfile = context.rfile
            self.wfile = context.wfile
        else:
            self.rfile = infile
            self.wfile = outfile

        # Resource caches
        self.colors = {}
        self.ttfs = {}
        self.fonts = {}
        self.images = {}
        self.anims = {}

        # Default resources
        self.default_ttf = TTF(self)
        self.system_ttf = TTF(self, id=ID_SYSTEM_TTF)
        self.immediate = Animation(self, 0, id=ID_NULL)

        self.last_color = None
        self.last_ttf = None
        self.last_font = None
        self.focus = None

        self.current_resolution = (640, 480, 1, 1)
        self.resolutions = [self.current_resolution]
        self.active = False

        # The HME handshake
        self.wfile.write('SBTV\0\0%c%c' % (chr(HME_MAJOR_VERSION),
                                           chr(HME_MINOR_VERSION)))
        self.wfile.flush()
        self.answer = self.rfile.read(8)
        # self.answer[-2:] contains the reciever's supported HME 
        # version, if you care. (I get 0.45 with TiVo 9.2.)

        # The root view object
        self.root = View(self, id=ID_ROOT_VIEW)

    def mainloop(self):
        """ The main loop -- startup, handle events, cleanup, exit. 
            hmeserver.py calls this after initializing the app object.

        """
        if not self.answer.startswith('SBTV'):
            return

        self.active = True
        self.startup()
        self.root.set_visible()

        # Run events until there are no more, or until self.active is 
        # set to False.
        while self.active and self.get_event():
            pass

        self.active = False
        self.cleanup()
        self.set_active(False)

        # Discard any pending events
        while self.get_event():
            pass

    def next_resnum(self):
        """ Return the next available resource ID number, starting from 
            ID_CLIENT.

        """
        x = self.resnum
        self.resnum += 1
        return x

    def get_event(self):
        """ The main event handler/dispatcher. Attempts to get one 
            event; returns False if it can't. Otherwise, unpacks the 
            event data, calls the handler function (see below), 
            processes the return value (in the case of _EVT_IDLE or 
            _EVT_RESOLUTION_INFO), and returns True.

        """
        try:
            self.wfile.flush()
        except:
            return False

        data = _get_chunked(self.rfile)
        if not data:
            return False

        ev = _EventData(data)

        evnum, resource = ev.unpack('ii')

        if evnum == _EVT_KEY:
            action, keynum, rawcode = ev.unpack('iii')

            if action == KEY_PRESS:
                handle = getattr(self.focus, 'handle_key_press',
                                 self.handle_key_press)
            elif action == KEY_REPEAT:
                handle = getattr(self.focus, 'handle_key_repeat',
                                 self.handle_key_repeat)
            elif action == KEY_RELEASE:
                handle = getattr(self.focus, 'handle_key_release',
                                 self.handle_key_release)
            handle(keynum, rawcode)

        elif evnum == _EVT_DEVICE_INFO:
            info = {}
            count = ev.unpack('i')[0]
            for i in xrange(count):
                key, value = ev.unpack('ss')
                info[key] = value
            handle = getattr(self.focus, 'handle_device_info',
                             self.handle_device_info)
            handle(info)

        elif evnum == _EVT_APP_INFO:
            info = {}
            count = ev.unpack('i')[0]
            for i in xrange(count):
                key, value = ev.unpack('ss')
                info[key] = value
            if 'error.code' in info:
                code = info['error.code']
                text = info.get('error.text', '')
                handle = getattr(self.focus, 'handle_error',
                                 self.handle_error)
                handle(code, text)
            elif 'active' in info:
                if info['active'] == 'true':
                    handle = getattr(self.focus, 'handle_active',
                                     self.handle_active)
                    handle()
                else:
                    return False
            else:
                handle = getattr(self.focus, 'handle_app_info',
                                 self.handle_app_info)
                handle(info)

        elif evnum == _EVT_RSRC_INFO:
            info = {}
            status, count = ev.unpack('ii')
            for i in xrange(count):
                key, value = ev.unpack('ss')
                info[key] = value
            handle = getattr(self.focus, 'handle_resource_info',
                             self.handle_resource_info)
            handle(resource, status, info)

        elif evnum == _EVT_IDLE:
            idle = ev.unpack('b')[0]
            handle = getattr(self.focus, 'handle_idle', self.handle_idle)
            handled = handle(idle)
            self.put(_CMD_RECEIVER_ACKNOWLEDGE_IDLE, 'b', handled)

        elif evnum == _EVT_FONT_INFO:
            for font in self.fonts.values():
                if font.id == resource:
                    break
            (font.ascent, font.descent, font.height, font.line_gap,
                extras, count) = ev.unpack('ffffii')
            extras -= 3
            font.glyphs = {}
            for i in xrange(count):
                id, advance, bounding = ev.unpack('iff')
                ev.index += 4 * extras
                font.glyphs[unichr(id)] = (advance, bounding)
            handle = getattr(self.focus, 'handle_font_info',
                             self.handle_font_info)
            handle(font)

        elif evnum == _EVT_INIT_INFO:
            params, memento = ev.unpack('dv')
            handle = getattr(self.focus, 'handle_init_info',
                             self.handle_init_info)
            handle(params, memento)

        elif evnum == _EVT_RESOLUTION_INFO:
            def unpack_res(ev, field_count):
                resolution = tuple(ev.unpack('iiii'))
                if field_count > 4:
                    ev.unpack('i' * (field_count - 4))
                return resolution

            field_count = ev.unpack('i')[0]
            self.current_resolution = unpack_res(ev, field_count)
            res_count = ev.unpack('i')[0]
            self.resolutions = [unpack_res(ev, field_count)
                                for i in xrange(res_count)]
            handle = getattr(self.focus, 'handle_resolution',
                             self.handle_resolution)
            self.set_resolution(handle())

        return True

    def send_key(self, keynum, rawcode=0, animation=None, animtime=0):
        """ Send a key event to the TiVo, for it to send back to us 
            later.

        """
        if animation is None:
            if animtime:
                animation = Animation(self, animtime)
            else:
                animation = self.immediate
        self.put(_CMD_RSRC_SEND_EVENT, 'iiiiii', animation.id, _EVT_KEY,
                 self.id, KEY_PRESS, keynum, rawcode)

    def set_focus(self, focus):
        """ Set the focus to a new object, and notify both the old and
            newly focused objects of the change. Define a handle_focus()
            method for an object if you want it to do something special
            on a focus change; handle_focus() should take a single
            boolean parameter, which will be False when losing focus and 
            True when gaining it.

        """
        if focus != self.focus:
            if hasattr(self.focus, 'handle_focus'):
                getattr(self.focus, 'handle_focus')(False)
            self.focus = focus
            if hasattr(focus, 'handle_focus'):
                getattr(focus, 'handle_focus')(True)

    def sleep(self, interval):
        """ Flush the write buffer, then sleep for interval seconds. """
        try:
            self.wfile.flush()
        except:
            self.active = False
        time.sleep(interval)

    def sound(self, id=None):
        """ Shorter form for playing sounds based on the id (the only
            ones that actually work). Can be specified by name or by
            number.

        """
        names = {'bonk': ID_BONK_SOUND,
                 'updown': ID_UPDOWN_SOUND,
                 'thumbsup': ID_THUMBSUP_SOUND,
                 'thumbsdown': ID_THUMBSDOWN_SOUND,
                 'select': ID_SELECT_SOUND,
                 'tivo': ID_TIVO_SOUND,
                 'left': ID_LEFT_SOUND,
                 'right': ID_RIGHT_SOUND,
                 'pageup': ID_PAGEUP_SOUND,
                 'pagedown': ID_PAGEDOWN_SOUND,
                 'alert': ID_ALERT_SOUND,
                 'deselect': ID_DESELECT_SOUND,
                 'error': ID_ERROR_SOUND,
                 'slowdown1': ID_SLOWDOWN1_SOUND,
                 'speedup1': ID_SPEEDUP1_SOUND,
                 'speedup2': ID_SPEEDUP2_SOUND,
                 'speedup3': ID_SPEEDUP3_SOUND}

        if type(id) == str:
            id = names[id]
        Sound(self, id=id).play()

    def transition(self, direction, params, url='', memento=''):
        """ Switch to another HME app.
            direction is TRANSITION_FORWARD or TRANSITION_BACK. params
            is a dict of lists -- see pack_dict(). url is the address of
            the new app -- leave it blank for a backwards transition.
            memento is a blob of data in unspecified format, limited to
            10K. params is meant to pass parameters, while memento is
            supposed to record the current state of the app, and is
            passed back unchanged after a TRANSITION_BACK.

        """
        if len(memento) > 10240:
            raise Exception, 'memento too large'
        self.put(_CMD_RECEIVER_TRANSITION, 'sidv',
                 url, direction, params, memento)

    def set_resolution(self, resolution):
        """ Change the screen resolution.
            This is called from get_event() after handle_resolution()
            (see there for more about resolution), but can also be used 
            directly.

        """
        if (resolution in self.resolutions and
            resolution != self.current_resolution):
            self.put(_CMD_RECEIVER_SET_RESOLUTION, 'iiii', *resolution)
            self.current_resolution = resolution
            self.root.set_bounds(width=resolution[0],
                                 height=resolution[1])

    # Stubs for apps to override.

    def startup(self):
        """ Override this to do any setup of your app before the main 
            event loop.

        """
        pass

    def handle_key_press(self, keynum, rawcode=None):
        """ Override this to handle key presses. (_EVT_KEY, KEY_PRESS) """
        pass

    def handle_key_repeat(self, keynum, rawcode=None):
        """ Override this to handle key repeats. (_EVT_KEY, KEY_REPEAT) """
        self.handle_key_press(keynum, rawcode)

    def handle_key_release(self, keynum, rawcode=None):
        """ Override this to handle key releases. (_EVT_KEY, KEY_RELEASE) """
        pass

    def handle_active(self):
        """ Override this to handle "active = true" from _EVT_APP_INFO. """
        pass

    def handle_error(self, code, text):
        """ Override this to handle errors from _EVT_APP_INFO. """
        pass

    def handle_app_info(self, info):
        """ Override this to handle anything else from _EVT_APP_INFO. """
        pass

    def handle_device_info(self, info):
        """ Override this to handle _EVT_DEVICE_INFO. """
        pass

    def handle_resource_info(self, resource, status, info):
        """ Override this if you want to handle _EVT_RSRC_INFO. resource 
            is the resource id number, status is the status code, and 
            info is a dict with whatever else the event returned.

        """
        pass

    def handle_font_info(self, font):
        """ Override this if you want to do something on getting an 
            _EVT_FONT_INFO event. font is the Font object, with the new 
            details (ascent, descent, height, line_gap, and a glyphs 
            dict) added.

        """
        pass

    def handle_idle(self, idle):
        """ If you can handle an idle event, override this, and return 
            True. The idle parameter is True when entering idle mode, 
            and False when leaving.

        """
        return False

    def handle_init_info(self, params, memento):
        """ Override this to handle _EVT_INIT_INFO. params and memento 
            are as created by the transition() method in the parent app.

        """
        pass

    def handle_resolution(self):
        """ Override this if you want to be able to change the screen 
            resolution from its default of 640x480; return the desired 
            resolution (which must be from the allowed list). The 
            allowed resolutions are given in self.resolutions; the 
            current in self.current_resolution. They're in the form of a 
            tuple: (width, height, px, py), where px:py is the pixel 
            aspect ratio.

        """
        return self.current_resolution

    def cleanup(self):
        """ If you need to do any cleanup after you're done handling 
            events, override this and do it here.

        """
        pass
