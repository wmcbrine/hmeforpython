HME for Python, v0.8
by William McBrine <wmcbrine@gmail.com>
February 22, 2008

An implementation of TiVo's HME (Home Media Extensions) protocol for 
Python, as a module (hme.py), a simple server (hmeserver.py), and 
examples (mostly ported from TiVo's Java HME SDK). Everything is 
released under the LGPL 2.1+, except where noted. (Most of the examples 
are Common Public License.)

I developed this in Python 2.5.1, and tested it in Linux, Mac OS X, and 
Windows XP, and with Python 2.4.4. The requirements are minimal. (hme.py 
depends only on the struct module. hmeserver.py is a bit more demanding, 
but uses only the standard library.)


Quick Start
-----------

In Linux, Mac OS X, etc.:

  ./hmeserver.py

In Windows:

  python hmeserver.py

This will serve the example apps. The default port is 9042 (not TiVo's 
7288).


Quick Stop
----------

In Linux, Mac OS X, etc., Ctrl-C does an orderly shutdown, un-announcing 
the apps before closing.

In Windows, you're stuck with either Ctrl-Break, or closing the command 
window, neither of which does an orderly shutdown.


Changes
-------

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
