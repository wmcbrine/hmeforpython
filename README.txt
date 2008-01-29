HME for Python, v0.1.1
by William McBrine <wmcbrine@gmail.com>
January 28, 2008

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
