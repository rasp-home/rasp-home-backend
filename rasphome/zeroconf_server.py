#!/usr/bin/env python3
# encoding: utf-8
#
# rasp-home-backend (Home automation software for Raspberry Pi)
# Copyright (C) 2013 Sebastian Wallat, University Duisburg-Essen
# Copyright (C) 2013 Andreas Bayer , University Duisburg-Essen
#
# This file is part of rasp-home-backend.
#
# rasp-home-backend is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rasp-home-backend is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with rasp-home-backend.  If not, see <http://www.gnu.org/licenses/>.
import cherrypy
from socketserver import BaseServer, UDPServer, ThreadingMixIn, DatagramRequestHandler
from cherrypy.process import plugins
from multiprocessing import Process
import socket
import struct
import netifaces

class ZeroconfServer(ThreadingMixIn, UDPServer):

    address_family = socket.AF_INET

    socket_type = socket.SOCK_DGRAM

    protocol_type = socket.IPPROTO_UDP

    allow_reuse_address = True


    def __init__(self, server_address, multicast_group, RequestHandlerClass, bind_and_activate=True, multicast_ttl = 1):
        BaseServer.__init__(self, server_address, RequestHandlerClass)
        self.socket = socket.socket(self.address_family,
                                    self.socket_type,
                                    self.protocol_type)
        self.multicast_group = multicast_group
        self.multicast_ttl = multicast_ttl
        if bind_and_activate:
            self.server_bind()
            self.server_activate()


    def server_bind(self):
        if self.allow_reuse_address:
            self.socket.socketopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()

    def server_activate(self):
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
        mreq = struct.pack("4sl", socket.inet_aton(self.multicast_group), socket.INADDR_ANY)
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

class ZerconfHandler(DatagramRequestHandler):

    def handle(self):
        pass

    def _getAddrList(self):
        addrs = []
        for iface in netifaces.interfaces():
            if iface == "lo":
                continue
            ifaceAddr = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in ifaceAddr.keys():
                for item in ifaceAddr[netifaces.AF_INET]:
                    addrs.append(item['addr'])
        return addrs



class ZeroconfManager(Process):
    pass



class ZeroconfPlugin(plugins.SimplePlugin):
    """
    Zeroconf Plugin
    """

    def __init__(self, bus):
        super(ZeroconfPlugin, self).__init__(bus)


    def start(self):
        pass

    def stop(self):
        pass

    def request_start(self):
        pass

    def request_stop(self):
        pass

cherrypy.engine.zeroconf = ZeroconfPlugin(cherrypy.engine)

