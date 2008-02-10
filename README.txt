HME for Python, v0.4
by William McBrine <wmcbrine@gmail.com>
February 9, 2008

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
