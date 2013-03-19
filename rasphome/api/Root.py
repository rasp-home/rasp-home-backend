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
    
    def GET(self):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/xml'
        msg = "<backends>\n"
        backends = Backend.get_all(session)
        for backend in backends:
            msg += Backend.export_one(backend, "all").decode() + "\n"
        msg += "<backends>\n<monitors>\n"
        monitors = Monitor.get_all(session)
        for monitor in monitors:
            msg += Monitor.export_one(monitor, "all").decode() + "\n"
        msg += "</monitors>\n<nodes>\n"
        nodes = Node.get_all(session)
        for node in nodes:
            msg += Node.export_one(node, "all").decode() + "\n"
        msg += "</nodes>\n<rooms>\n"
        rooms = Room.get_all(session)
        for room in rooms:
            msg += Room.export_one(room, "all").decode() + "\n"
        msg += "</rooms>\n<users>\n"
        users = User.get_all(session)
        for user in users:
            msg += User.export_one(user, "all").decode() + "\n"
        msg += "</users>"
        return msg