HME for Python, v0.2
by William McBrine <wmcbrine@gmail.com>
February 7, 2008

0.2   -- Moved root view activation to after startup(), but before event
         handling; flush output before checking for input; flush input
         after close. This should bring it a little closer to the Java
         SDK's behavior, and makes it work under TiVo software 7.2.
         Also, hmeserver now prints app names as they're published/
         unregistered.
0.1.3 -- Skip reverse lookup in hmeserver (thanks armooo); include the 
         app name in the Starting/Stopping HME line; added a silly 
         effect for the test app.
0.1.2 -- The mechanism for skipping non-app directories was broken.
0.1.1 -- Changed default port.

An implementation of TiVo's HME (Home Media Extensions) protocol for 
Python, as a module (hme.py), a simple server (hmeserver.py), and 
examples (mostly ported from TiVo's Java HME SDK). Everything is 
released under the LGPL 2.1+, except where noted. (Most of the examples 
are Common Public License.)

I developed this in Python 2.5.1, and haven't tested it with other 
versions, but it does nothing exotic. (hme.py depends only on the struct 
module. hmeserver.py is a bit more demanding.) But I have tested it in 
Linux, Mac OS X, and Windows XP.


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


Bugs
----

If you run the Animate demo from a Series 2 TiVo running 9.1 software, 
it will crash and make all your text disappear. This is a TiVo-side bug, 
not a bug in HME for Python; you can see the same behavior by running 
the original version of Animate from TiVo's Java HME SDK. Other models 
and/or software versions (Series 2 running 7.2, Series 3 running 9.2) 
are not affected.
