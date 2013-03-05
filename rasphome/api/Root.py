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

__all__=['Root']

import cherrypy
import rasphome.database
from rasphome.models import Backend
from rasphome.models import Monitor
from rasphome.models import Node
from rasphome.models import Room
from rasphome.models import User

class Root(object):
    exposed = True
    
    @cherrypy.tools.require(roles={"backend":[], "monitor":[], "user":["admin"]})
    def GET(self):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        msg = "Backends:\n"
        backends = Backend.get_all(session)
        for backend in backends:
            msg += str(backend) + "\n"
        msg += "Monitors:\n"
        monitors = Monitor.get_all(session)
        for monitor in monitors:
            msg += str(monitor) + "\n"
        msg += "Nodes:\n"
        nodes = Node.get_all(session)
        for node in nodes:
            msg += str(node) + "\n"
        msg += "Rooms:\n"
        rooms = Room.get_all(session)
        for room in rooms:
            msg += str(room) + "\n"
        msg += "Users:\n"
        users = User.get_all(session)
        for user in users:
            msg += str(user) + "\n"