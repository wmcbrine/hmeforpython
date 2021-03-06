HME for Python
==============

:Author:  William McBrine <wmcbrine@gmail.com>
:Version: 0.20
:Date:    May 6, 2012

An implementation of TiVo's HME (Home Media Extensions) protocol for
Python, as a module (hme.py), a simple server (start.py), and examples
(mostly ported from TiVo's Java HME SDK). Everything is released under
the LGPL 2.1+, except where noted. (Most of the examples are Common
Public License.)

Tested on multiple platforms with Python 2.5 through 2.7 (not compatible
with Python 3.x). Requires only the standard library.


Quick Start
-----------

In Linux, Mac OS X, etc.:

  ./start.py

In Windows:

  python start.py

This will serve the example apps. The default port is 9042 (NOT TiVo's
default of 7288). To see more options, run "./start.py --help".


Quick Stop
----------

In Linux, Mac OS X, etc., Ctrl-C does an orderly shutdown, un-announcing
the apps before closing. (The equivalent is SIGINT, or "kill -2".)

In Windows, with older versions of Python, you're stuck with either
Ctrl-Break, or closing the command window, neither of which does an
orderly shutdown. This may have been fixed with Python 2.7.


Config
------

You can optionally create a file named "config.ini" to specify the same
kind of options as on the command line. The contents also become part of
the context passed on to each app, so apps can store their own
preferences there. See the picture viewer for an example -- it now
checks the config for optional root path, delay and extension list
options. (You'll almost certainly want to change the path.)

Here's an example config.ini, showing all the possible keywords for the
server and the picture app. (The values shown here are purely for
illustrative purposes.)

::

 [hmeserver]
 port=7288
 address=192.168.1.1
 zeroconf=False
 beacon=255.255.255.255
 basepath=c:\hme
 datapath=c:\
 apps=picture clock

 [picture]
 path=c:\pictures
 delay=2
 exts=.jpg .png


Direct Text Input
-----------------

TiVo has extended HME to allow direct input of ASCII text via key 
events, instead of requiring the "Ouija board" input method. This is 
intended primarily for use with the Slide remote, but it also works with 
other USB keyboards, as well as the network remote control interface. 
TiVo has not documented it publicly, so I'll describe it here.

There are two types of direct text key events. The first type returns a 
key code of KEY_UNKNOWN (0), with the value of the key encoded in the 
rawcode. (To convert this rawcode to ASCII, you can use HME for Python's 
new top-level function qwerty_map().) This type of event is used for 
KEY_PRESS events generated by the IRCODE command from the network 
interface, and is used for all KEY_RELEASE events. Case is not 
distinguished (HME for Python decodes the values as uppercase), and for 
symbolic values that appear on the upper half of a key, the value on the 
lower half is reported.

The second type of direct text key event returns the ASCII code, plus 
0x10000, as the key code. Case is preserved, and symbols are reported 
exactly. This type of event is used for KEY_PRESS events generated by 
USB keyboards, as well as by the KEYBOARD command from the network 
interface, which currently works only on the Premiere. This second type 
of event is only returned if the HME app reports that it implements 
version 0.49 of the HME protocol or later; otherwise, the TiVo drops 
these events, while still reporting events of the first type. (This 
means that a pre-0.49 app will receive only KEY_RELEASE events for most 
keys on a USB keyboard.)

After going back and forth on this, I decided to pass the codes for both 
event types through unchanged, so that the app could handle them as 
needed. (In my own Reversi, for events of the second type, the existing 
case is respected, while it's adjusted automatically for events of the 
first type.)


More Info
---------

The main documentation is in the hme module itself, as docstrings. (Open 
a Python shell; "import hme"; "help(hme)".) And be sure to look over the 
example apps.

You may also want to consult the HME Protocol Specification, from TiVo's 
Java SDK. And the rest of the documentation from that package may be 
helpful in a general way, but it can also be misleading, because (apart 
from the example apps) this is NOT a port of the Java SDK; it's based on 
the protocol spec.


Notes
-----

As of TiVo software version 20.2, at least, the HDUI no longer requests 
the app icons. (The SDUI works as always.) Also in 20.2, there's a bug 
in transparency rendering that sometimes causes black to be substituted 
for white in text that's not fully opaque.

The last TiVo software revision for the Series 2, 9.3b, still has fatal 
bugs in its HME engine under certain conditions, where the text 
disappears from the menus (outside HME), or the entire machine locks up. 
As a result, the "animate" and "effects" demos now have code to keep 
them from running in that environment. You can see the same bugs with 
the original versions from the Java SDK.


Changes
-------

0.20
    UTF-8 strings can now be passed directly to HME commands --
    previously only ASCII and Unicode strings were accepted. Note that
    HME for Python isn't checking for valid UTF-8, so in fact you can
    pass anything, and it's up to the TiVo to handle it.

    Automatic flush after send_key().

    Added KEY_OPT_ZOOM as another alias for KEY_OPT_WINDOW.

    Check for existing instances of a title before announcing it, to
    avoid stepping on them; append "[2]" etc. as needed. After the Java
    SDK.

    Added the ability to back out to most sample apps (all that didn't
    have it except "hello"), using Left, Clear and/or Pause, depending
    on the app. This deviates (further) from the apps being exact clones
    of the Java versions, but who cares.

    Use the alternate (modern) method of loading PIL's Image module;
    prefer "import hme" over "from hme import *" for examples; minor
    style cleanups for examples.

    In Zeroconf, use the same method of getting the default IP as in
    start.py, instead of gethostbyname(gethostname()); minor style
    cleanups and code tightening for Zeroconf.

    Documentation cleanup.

0.19
    HME for Python now reports itself as implementing version 0.49 of
    the HME protocol. This version has not been publicly documented by
    TiVo, but the change is necessary in order to properly support
    direct text input (including from the Slide remote). In addition to
    the new keyboard handling (see above), there's an added parameter
    for stream creation: a dict called "params". None of its possible
    values are known.

    New top-level function, qwerty_map(), to convert the rawcode from an
    IRCODE-style keyboard event to its ASCII equivalent.

    More key names reported by the test app, with keyboard text reported
    from either kind of input.

    Initialize MIMETYPES from mimetypes.types_map -- allows HME/VLC to
    continue using it.

    Flush after a change in stream speed -- gets sounds to play
    immediately, even when not immediately followed by an event check.

0.18
    More automatic removal of some resources when they go out of scope:
    nameless Image, TTF (named ones are cached, and may be duplicate
    references to the same TiVo-side resource -- should probably rework
    this), Text and Stream resources. (Other resources are still
    cached.) As part of these changes, app.resources has been removed.

    "Test" app: Add KEY_OPT_A, B, C, and D button names; for key codes
    that aren't in the list of names, print the number.

    Stupid bug: extra colon in Content-Length header. Revealed by the
    new HD UI on the TiVo Premiere.

    Use the mimetypes module instead of hardwiring quite so many MIME
    types in start.py.

    Various minor fixes for Zeroconf (mainly cosmetic).

    Icons resaved as RGB for the sake of the new UI on the Premiere,
    which can't handle indexed or greyscale PNGs.

0.17
    Set up a 64K output buffer before initializing. This will cut down
    on the number of packets sent, as well as forestalling any potential
    "#3-5-6"-style errors, as in pyTivo (though I haven't observed those
    in HME). But it also means that you have to flush the output to be
    sure all commands are sent. The buffer is flushed automatically when
    waiting for events; the only time this is an issue is when
    sleep()ing instead of returning from the event handler. To deal with
    this, I've added a sleep() method to the Application class; just use
    it in place of time.sleep(). All it does is flush the output, then
    sleep. You could also do this manually. The example programs have
    been modified to use the new method.

    When unpacking an HME dict, if a list contains only a single item,
    take it out of list form. This makes it more symmetrical with what
    was done for packing in 0.8, although if any actual one-item lists
    were packed, the list will be lost in that case, too.

    Added MIME types for .tivo files, and some other video types.

    When the address isn't specified, to find it, skip gethostbyname(),
    and just use the default route method; use port 123 instead of 0
    (the Mac doesn't like 0).

    Supress Zeroconf.py's useless "NonLocalNameException".

0.16
    Support for alpha values in colors -- apparently this was fixed in
    TiVo software 9.3. (?) Reported by TCF user "Allanon". The way this
    works is, wherever you previously could specify a color number in
    RGB form, you can now do it as ARGB, where "A" (alpha), the most
    significant byte, represents the opacity -- _except_ that an alpha
    value of 0 is treated as full opacity (equivalent to 0xff), for the
    sake of simplicity and backwards compatibility. (So, if you don't
    want to mess with alpha values, you can continue using plain RGB
    values.) Otherwise, the higher the number, the more opaque.

    Removed the note about limits on the size of color resources --
    fixed in 9.4 (or earlier?). A color assigned to an HD view will now
    fill the whole view.

    hmeserver (start.py) now responds to requests for robots.txt, with
    no permission. (No good can come of trying to crawl an HME app.)

    Taiwanese TiVos append "?width=704&height=480" to their app
    requests. Previously, this would make hmeserver send back a 403.
    Now, it ignores these parameters, so the app will work. (And perhaps
    in the future, hmeserver will actually support this undocumented
    feature of TiVo's SDK.)

    Added MIME type for WMV video.

    Minor changes to demo apps: made a few bits more Pythonic, and fixed
    some erroneous spacing that was only apparent with Python 3.0.

    Minor changes to the Zeroconf module: untabbed, and removed the
    deprecated has_key().

0.15
    Added clear_resource() and remove_resource() methods for Views.
    clear_resource() disassociates the View from its resource, without
    removing the resource. remove_resource() is kind of trivial --
    equivalent to "resource.remove(); resource = None" -- but is
    included for completeness.

    Optional config file parsing for hmeserver -- see above.

    Moved check for application class from Handler to startup.

    Slightly more robust path handling for hmeserver -- works better in
    Windows, and the disallowed-directory check is less kludgy.

    Renamed hmeserver.py to start.py. But note that it's still
    "hmeserver" for purposes of config.ini.

    Support for Python < 2.3 is dropped.

0.14
    hmeserver now separates the app and data roots, to allow keeping
    icons etc. together with their apps, while having data elsewhere.
    The new command-line option "--datapath" specifies the data root,
    while "--basepath" still sets the app root. Files outside of app
    directories (including those in the app root, which had previously
    been allowed) are now forbidden unless the datapath is set.

    The initial transparency of a View can now be set via the
    "transparency" keyword parameter when creating it, instead of being
    settable only by a call to set_transparency().

0.13
    Added a new method for specifying sounds, by name. (The old method,
    by number, will also still work.) The symbolic names were a bit
    cumbersome, but I didn't feel that I could shorten them... hence,
    this. It's similar to how it works in the Java SDK, but without the
    fake ".snd" extension. See examples.

    Added a "speed" attribute to the Resource class -- only meaningful
    for Streams.

    In hmeserver, send size information with regular files where
    available; catch and report socket errors on sending regular files;
    use log_error() and log_message() instead of print where
    appropriate.

    Added MIME types for video, since it can now be Streamed.

    Added port number to logged address, for help in debugging.

    Startup banner for hmeserver; "help" and "version" options.

    Removed "sorted()" for compatibility with older versions of Python
    (or Jython).

    Some new command-line options for hmeserver, to set host, port,
    path, and/or zeroconf off, and to allow specific modules to be
    named. (See "./hmeserver.py --help".)

    The HME server classes now depend only on the values passed to
    __init__(), not the globals. In principle, you can import hmeserver
    and use the classes from another program.

    Skip Zeroconf functions if the module is missing.

0.12
    Barred effects and animate from all non-S3/HD TiVos running 9.1 or
    9.3. This may be overbroad, but I can't confirm that any S2's can
    handle these apps with 9.x.

    Made some things "private", so they won't be imported by "from hme
    import *".

    Added ".pyo" to the list of file types not to send.

    In the picture viewer, shuffle the pictures instead of sorting them;
    also, check not only for a valid directory, but for one containing
    pictures.

    Miscellaneous internal reworking and simplification.

    Tested under more versions.

    Typo: had "LPGL" instead of "LGPL".

0.11
    Added a simple slideshow Picture Viewer to the included apps. It
    depends on the Python Imaging Library, and you'll have to edit
    picture/__init__.py to set ROOT to an appropriate directory. The app
    automatically uses hi-def mode when available.

    Changed the Animation class (and all the "animtime" parameters of
    various functions) to take seconds instead of milliseconds, to make
    it more consistent with general Python usage.

    Small tweak to the put_chunked() function.

0.10
    Sending data larger than 64K was broken since 0.3. Argh.

    Images without names are not cached, but Image.remove() was still
    trying to remove them from the cache.

0.9
    Added a separate set_resolution() function.

    Changing the resolution with an already-visible root view (which is
    always the situation, since 0.2) requires a set_bounds() call on the
    root view.

0.8
    The dict items for transition() no longer have to be in list form,
    although they still _can_ be. (The values returned to
    handle_init_info() are still lists, though.)

    Simplified the transition demo and added an icon for it.

    Print the skipped directories in hmeserver, along with the
    reasons they were skipped.

0.7
    Added support for app transitions -- the last unimplemented part of
    the HME specification. (But I still have more to do to match the
    Java SDK.) This also entailed support for the HME "dict" type, which
    although mentioned in the specification is not documented. A sample
    app is included.

0.6
    Added set_focus() to use when changing focus, instead of setting
    self.focus directly. Define a handle_focus() method for an object if
    you want it to do something special on a focus change;
    handle_focus() should take a single boolean parameter, which will be
    False when losing focus and True when gaining it.

    Shorter form for sound calls -- because in practice, they're always 
    ID-based.

    Exit (event loop) on receiving an EVT_APP_INFO of active=false.

    Flush the sent handshake; exit mainloop() if no valid handshake is
    received.

0.5
    Focus support -- set self.focus to the object you want to handle
    events. It need not be a View; it can be any object. Just add the
    appropriate handler as an attribute. If a handler isn't present in
    the self.focus object, the app's handler is used. But if you want to
    pass events on from the object's handler, you'll have to call the
    app's handler explicitly.

    Default key repeat event behavior is now to call the key press 
    handler.

    Unspecified width and height in a child window need to default to
    that of the parent window _minus_ the position.

0.4
    Narrow the list of exceptions handled when importing -- this covers
    non-module directories without masking real errors.

    One more event handler -- handle_active(). This can be used where
    startup() used to be, i.e., after the startup events.

0.3
    Absorb all exceptions during reading or writing, allowing orderly
    shutdown even if the socket is abrubtly cut off; also, the use of
    the term "chunk" was not appropriate -- it should be reserved for
    the components of the chunked stream.

    Removed self.app_info and self.device_info; added handle_app_info()
    and handle_device_info(). With the new structure (startup(),
    activate, then start handling events), something like this is
    necessary.

    Prevent animate and effects from being run on the broken 9.1
    software (the others seem OK); print more info about events in the
    test app.

0.2
    Moved root view activation to after startup(), but before event
    handling; flush output before checking for input; flush input after
    close. This should bring it a little closer to the Java SDK's
    behavior, and makes it work under TiVo software 7.2.

    hmeserver now prints app names as they're published/unregistered.

0.1.3
    Skip reverse lookup in hmeserver (thanks armooo).

    Include the app name in the Starting/Stopping HME line.

0.1.2
    The mechanism for skipping non-app directories was broken.

0.1.1
    Changed default port.
