#!/usr/bin/env python

# HME Server for Python, v0.13
# Copyright 2008 William McBrine
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You didn't receive a copy of the license with this program because 
# you already have dozens of copies, don't you? If not, visit gnu.org.

""" HME Server for Python

    A simple HTTP server and Zeroconf announcer for use in conjunction
    with the HME module. It serves both HME apps (implemented as Python
    modules), and arbitrary files (with Python source and byte-code
    excluded), so that it can provide streaming resources for HME apps.
    It also supports the TiVo's "Manually add a server..." option when
    run on port 80.

    Each module is checked for a TITLE and CLASS_NAME attribute. If
    either is absent, the module name is used instead.

    While the samples have all been done as 'module/__init__.py' for
    neatness, they could just as well be named 'module.py' in this
    directory. And the subdirectories can be omitted if you don't need
    icons. (Other resources can be placed anywhere, but the TiVo always
    requests '/module/icon.png'.)

    Command-line options:

    -a, --address     Specify the address to bind to. The default is ''
                      (bind to all interfaces).

    -p, --port        Specify the port to bind to. The default is 9042.

    -b, --basepath    Specify the path to use as the base path when
                      sending regular files. The default is the location
                      of this file. Note that this doesn't specify the
                      path to the modules, which are just imported.

    -z, --nozeroconf  Disable Zeroconf broadcasts. Normally, Zeroconf is
                      used to announce the availability of new apps at
                      startup, and their removal at shutdown. When
                      disabled, the only way to access the apps is via
                      "Manually add a server...". Zeroconf is disabled
                      automatically if the Zeroconf module is not
                      present, or can't be loaded.

    -h, --help        Print help and exit.

    -v, --version     Print the version and exit.

    <app> <app>       Any other command-line option is treated as the
                      name of a module to load. If none are given, each
                      directory under this one is checked for a loadable
                      module.

"""

__author__ = 'William McBrine <wmcbrine@gmail.com>'
__version__ = '0.13'
__license__ = 'LGPL'

import getopt
import os
import socket
import sys
import time
import urllib
import SocketServer
import BaseHTTPServer

# Version of the protocol implemented
from hme import HME_MAJOR_VERSION, HME_MINOR_VERSION

class Server(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    def __init__(self, addr, handler, basepath, apptitles):
        self.basepath = basepath
        self.apptitles = apptitles
        BaseHTTPServer.HTTPServer.__init__(self, addr, handler)

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = 'HMEPython/%s' % __version__

    BUFSIZE = 0x10000

    MIMETYPES = {'.html': 'text/html',
                 '.xml': 'text/xml',
                 '.css': 'text/css',
                 '.gif': 'image/gif',
                 '.jpg': 'image/jpeg',
                 '.png': 'image/png',
                 '.txt': 'text/plain',
                 '.pdf': 'application/pdf',
                 '.mp3': 'audio/mpeg'}

    MIMEFALLBACK = 'application/octet-stream'

    BADEXTS = ('.py', '.pyc', '.pyo')  # Don't send back the code

    XML_HEADER = """<TiVoContainer><Details>
        <ContentType>x-container/tivo-server</ContentType>
        <SourceFormat>x-container/folder</SourceFormat>
        <TotalItems>%d</TotalItems><Title>HME Server for Python</Title>
        </Details><ItemStart>0</ItemStart><ItemCount>%d</ItemCount>
    """

    XML_ITEM = """<Item><Details><ContentType>application/x-hme</ContentType>
        <SourceFormat>x-container/folder</SourceFormat><Title>%s</Title>
        </Details><Links><Content><Url>http://%s:%d/%s/</Url></Content></Links>
        </Item>
    """

    XML_CLOSER = '</TiVoContainer>'

    def address_string(self):
        """ Override address_string() with a version that skips the 
            reverse lookup. Suggestion of Jason Michalski.

        """
        host, port = self.client_address[:2]
        return host

    def _ok(self, mime):
        self.send_response(200)
        self.send_header('Content-type', mime)
        self.end_headers()

    def _page(self, body):
        name = self.path.strip('/')
        apps = self.server.apptitles.keys()
        apptitles = self.server.apptitles

        if name.startswith('TiVoConnect'):
            self._ok('text/xml')

            self.wfile.write(self.XML_HEADER % (len(apps), len(apps)))
            host, port = self.connection.getsockname()
            for name in apps:
                self.wfile.write(self.XML_ITEM % (apptitles[name],
                                                  host, port, name))
            self.wfile.write(self.XML_CLOSER)

        elif name in apps:
            app = __import__(name)
            appname = getattr(app, 'CLASS_NAME', name.title())
            try:
                appclass = getattr(app, appname)
            except AttributeError:
                self.send_error(403)
                raise Exception, "Can't find application class for %s" % name

            self._ok('application/x-hme')

            print time.asctime(), 'Starting HME: %s' % name
            appinst = appclass(context=self)
            appinst.mainloop()
            print time.asctime(), 'Ending HME: %s' % name

        else:
            path = (self.server.basepath +
                    urllib.unquote(self.path).replace('/..', ''))
            if os.path.isdir(path):
                self.send_error(403)
                return
            ext = os.path.splitext(path)[1].lower()
            if ext in self.BADEXTS:
                self.send_error(404)
                return
            try:
                mime = self.MIMETYPES[ext]
            except:
                mime = self.MIMEFALLBACK
            try:
                page = open(path, 'rb')
            except IOError:
                self.send_error(404)
                return
            self._ok(mime)
            while body:
                block = page.read(self.BUFSIZE)
                if not block:
                    break
                self.wfile.write(block)
            page.close()

    def do_HEAD(self):
        self._page(False)

    def do_GET(self):
        self._page(True)

class Broadcast:
    def __init__(self, addr, apptitles):
        self.addr, self.port = addr
        self.apps = apptitles.keys()
        self.apps.sort()
        self.appinfo = []
        self.rz = Zeroconf.Zeroconf()
        for name in self.apps:
            print 'Registering:', name
            desc = {'path': '/%s/' % name,
                    'version': '%d.%d' % (HME_MAJOR_VERSION,
                                          HME_MINOR_VERSION)}
            info = Zeroconf.ServiceInfo('_tivo-hme._tcp.local.',
                                        '%s._tivo-hme._tcp.local.' %
                                        apptitles[name],
                                        self.get_address(), self.port,
                                        0, 0, desc)
            self.rz.registerService(info)
            self.appinfo.append(info)

    def shutdown(self):
        print 'Unregistering:', ' '.join(self.apps)
        for info in self.appinfo:
            self.rz.unregisterService(info)
        self.rz.close()

    def get_address(self):
        if not self.addr:
            try:
                self.addr = socket.gethostbyname(socket.gethostname())
                # On my system, this always gives me 127.0.0.1. Hence...
            except:
                self.addr = ''
            if not self.addr or self.addr.startswith('127.'):
                # ...the hard way. This may not be the right interface, 
                # either; if not, set HOST to the desired address.
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('4.2.2.1', 0))
                self.addr = s.getsockname()[0]
        return socket.inet_aton(self.addr)

if __name__ == '__main__':
    host = ''      # By default, attach to all available interfaces
    port = 9042    # TiVo Inc. uses 7288. But set it to 80 to make
                   # "Manually add a server" work.
    root = os.path.abspath(os.path.dirname(__file__))   # You are here

    have_zc = True
    apps = []
    opts = []

    print 'HME Server for Python', __version__

    try:
        opts, apps = getopt.getopt(sys.argv[1:], 'a:p:b:zvh',
                                   ['address=', 'port=', 'basepath=',
                                    'nozeroconf', 'version', 'help'])
    except getopt.GetoptError, msg:
        print msg

    for opt, value in opts:
        if opt in ('-a', '--address'):
            host = value
        elif opt in ('-p', '--port'):
            port = int(value)
        elif opt in ('-b', '--basepath'):
            root = value
        elif opt in ('-z', '--nozeroconf'):
            have_zc = False
        elif opt in ('-v', '--version'):
            exit()
        elif opt in ('-h', '--help'):
            print __doc__
            exit()

    try:
        assert(have_zc)
        import Zeroconf
    except Exception, msg:
        print 'Not using Zeroconf:', msg
        have_zc = False

    if not apps:
        apps = [name for name in os.listdir(root) if 
                os.path.isdir(os.path.join(root, name))]

    apptitles = {}

    for name in apps:
        try:
            app = __import__(name)
        except (ValueError, ImportError), msg:
            print 'Skipping:', name, '-', msg
        else:
            apptitles[name] = getattr(app, 'TITLE', name.title())

    print time.asctime(), 'Server Starts'
    httpd = Server((host, port), Handler, root, apptitles)
    if have_zc:
        bd = Broadcast((host, port), apptitles)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        if have_zc:
            bd.shutdown()
    print time.asctime(), 'Server Stops'
