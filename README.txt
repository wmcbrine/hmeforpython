HME for Python, v0.15
by William McBrine <wmcbrine@gmail.com>
September 25, 2008

An implementation of TiVo's HME (Home Media Extensions) protocol for 
Python, as a module (hme.py), a simple server (start.py), and examples 
(mostly ported from TiVo's Java HME SDK). Everything is released under 
the LGPL 2.1+, except where noted. (Most of the examples are Common 
Public License.)

I developed this in Python 2.5.2, and tested it in Linux, Mac OS X, and 
Windows XP, and with Python 2.4.5 and 2.3.5. The requirements are 
minimal. (hme.py depends only on the struct module. start.py is a bit 
more demanding, but uses only the standard library.)


Quick Start
-----------

In Linux, Mac OS X, etc.:

  ./start.py

In Windows:

  python start.py

This will serve the example apps. The default port is 9042 (not TiVo's 
7288). To see more options, run "./start.py --help".


Quick Stop
----------

In Linux, Mac OS X, etc., Ctrl-C does an orderly shutdown, un-announcing 
the apps before closing.

In Windows, you're stuck with either Ctrl-Break, or closing the command 
window, neither of which does an orderly shutdown.


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

[hmeserver]
port=7288
address=192.168.1.1
zeroconf=False
basepath=c:\hme
datapath=c:\
apps=picture clock

[picture]
path=c:\pictures
delay=2
exts=.jpg .png


Changes
-------

0.15 --  Added clear_resource() and remove_resource() methods for Views.
         clear_resource() disassociates the View from its resource,
         without removing the resource. remove_resource() is kind of
         trivial -- equivalent to "resource.remove(); resource = None" --
         but is included for completeness.

         Optional config file parsing for hmeserver -- see above.

         Moved check for application class from Handler to startup.

         Slightly more robust path handling for hmeserver -- works
         better in Windows, and the disallowed-directory check is less
         kludgy.

         Renamed hmeserver.py to start.py. But note that it's still
         "hmeserver" for purposes of config.ini.

         Support for Python < 2.3 is dropped.

0.14 --  hmeserver now separates the app and data roots, to allow
         keeping icons etc. together with their apps, while having data
         elsewhere. The new command-line option "--datapath" specifies
         the data root, while "--basepath" still sets the app root.
         Files outside of app directories (including those in the app
         root, which had previously been allowed) are now forbidden
         unless the datapath is set.

         The initial transparency of a View can now be set via the
         "transparency" keyword parameter when creating it, instead of
         being settable only by a call to set_transparency().

0.13  -- Added a new method for specifying sounds, by name. (The old
         method, by number, will also still work.) The symbolic names
         were a bit cumbersome, but I didn't feel that I could shorten
         them... hence, this. It's similar to how it works in the Java
         SDK, but without the fake ".snd" extension. See examples.

         Added a "speed" attribute for to the Resource class -- only
         meaningful for Streams.

         In hmeserver, send size information with regular files where
         available; catch and report socket errors on sending regular
         files; use log_error() and log_message() instead of print where
         appropriate.

         Added MIME types for video, since it can now be Streamed.

         Added port number to logged address, for help in debugging.

         Startup banner for hmeserver; "help" and "version" options.

         Removed "sorted()" for compatibility with older versions of
         Python (or Jython).

         Some new command-line options for hmeserver, to set host, port,
         path, and/or zeroconf off, and to allow specific modules to be 
         named. (See "./hmeserver.py --help".)

         The HME server classes now depend only on the values passed
         to __init__(), not the globals. In principle, you can import
         hmeserver and use the classes from another program.

         Skip Zeroconf functions if the module is missing.

0.12  -- Barred effects and animate from all non-S3/HD TiVos running 9.1
         or 9.3. This may be overbroad, but I can't confirm that any
         S2's can handle these apps with 9.x.

         Made some things "private", so they won't be imported by "from
         hme import *".

         Added ".pyo" to the list of file types not to send.

         In the picture viewer, shuffle the pictures instead of sorting
         them; also, check not only for a valid directory, but for one
         containing pictures.

         Miscellaneous internal reworking and simplification.

         Tested under more versions.

         Typo: had "LPGL" instead of "LGPL".

0.11  -- Added a simple slideshow Picture Viewer to the included apps.
         It depends on the Python Imaging Library, and you'll have to
         edit picture/__init__.py to set ROOT to an appropriate
         directory. The app automatically uses hi-def mode when
         available.

         Changed the Animation class (and all the "animtime" parameters
         of various functions) to take seconds instead of milliseconds,
         to make it more consistent with general Python usage.

         Small tweak to the put_chunked() function.

0.10  -- Sending data larger than 64K was broken since 0.3. Argh.

         Images without names are not cached, but Image.remove() was
         still trying to remove them from the cache.

0.9   -- Added a separate set_resolution() function.

         Changing the resolution with an already-visible root view
         (which is always the situation, since 0.2) requires a
         set_bounds() call on the root view.

0.8   -- The dict items for transition() no longer have to be in list 
         form, although they still _can_ be. (The values returned to
         handle_init_info() are still lists, though.)

         Simplified the transition demo and added an icon for it.

         Print the skipped directories in hmeserver, along with the
         reasons they were skipped.

0.7   -- Added support for app transitions -- the last unimplemented
         part of the HME specification. (But I still have more to do to
         match the Java SDK.) This also entailed support for the HME
         "dict" type, which although mentioned in the specification is
         not documented. A sample app is included.

0.6   -- Added set_focus() to use when changing focus, instead of
         setting self.focus directly. Define a handle_focus() method for
         an object if you want it to do something special on a focus
         change; handle_focus() should take a single boolean parameter,
         which will be False when losing focus and True when gaining it.

         Shorter form for sound calls -- because in practice, they're
         always ID-based.

         Exit (event loop) on receiving an EVT_APP_INFO of active=false.

         Flush the sent handshake; exit mainloop() if no valid handshake
         is received.

0.5   -- Focus support -- set self.focus to the object you want to 
         handle events. It need not be a View; it can be any object.
         Just add the appropriate handler as an attribute. If a handler
         isn't present in the self.focus object, the app's handler is
         used. But if you want to pass events on from the object's
         handler, you'll have to call the app's handler explicitly.

         Default key repeat event behavior is now to call the key press
         handler.

         Unspecified width and height in a child window need to default
         to that of the parent window _minus_ the position.

0.4   -- Narrow the list of exceptions handled when importing -- this
         covers non-module directories without masking real errors.

         One more event handler -- handle_active(). This can be used
         where startup() used to be, i.e., after the startup events.

0.3   -- Absorb all exceptions during reading or writing, allowing
         orderly shutdown even if the socket is abrubtly cut off; also,
         the use of the term "chunk" was not appropriate -- it should be
         reserved for the components of the chunked stream.

         Removed self.app_info and self.device_info; added
         handle_app_info() and handle_device_info(). With the new
         structure (startup(), activate, then start handling events),
         something like this is necessary.

         Prevent animate and effects from being run on the broken 9.1
         software (the others seem OK); print more info about events in
         the test app.

0.2   -- Moved root view activation to after startup(), but before event
         handling; flush output before checking for input; flush input
         after close. This should bring it a little closer to the Java
         SDK's behavior, and makes it work under TiVo software 7.2.

         hmeserver now prints app names as they're published/unregistered.

0.1.3 -- Skip reverse lookup in hmeserver (thanks armooo).

         Include the app name in the Starting/Stopping HME line.

0.1.2 -- The mechanism for skipping non-app directories was broken.

0.1.1 -- Changed default port.


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
