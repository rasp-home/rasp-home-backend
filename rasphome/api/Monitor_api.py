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

__all__=['Monitor_api']

import cherrypy
import xml.etree.ElementTree
from rasphome import authorization
from rasphome.models.Monitor import Monitor

class Monitor_api(object):
    exposed = True
    
    """
    "curl http://admin:admin@localhost:8090/user/
    "curl http://admin:admin@localhost:8090/user?user=sw
    """
    def GET(self, name = None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        if name == None:
            msg = "All Monitors: \n"
            result = Monitor.get_all(session)
            for name in result:
                msg = msg + str(name) + "\n"
            return msg
        else:
            my_monitor = Monitor.get_one(session, name)
            if isinstance(my_monitor, Monitor):
                return "Monitor: \n" + str(my_monitor) + "\n"
            else:
                raise cherrypy.HTTPError("404 Monitor %s not found" % name)
            
    
    """
    "curl -X PUT -H "Content-Type: text/xml" -d "<user><name>andi</name><password>test</password></user>" http://admin:admin@localhost:8090/user
    """
    @cherrypy.tools.auth_basic(on=False)
    def PUT(self):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        if (cherrypy.request.process_request_body == True):
            tree = xml.etree.ElementTree.fromstring(cherrypy.request.body.read())
            name = tree.find("name").text
            password = tree.find("password").text
            
            Monitor.add_one(session, name, password)
            return "Monitor %s added." % (name)
        else:
            raise cherrypy.HTTPError("404 No body")
    
    """
    "curl -X DELETE http://admin:admin@localhost:8090/user/andi
    """
    @cherrypy.tools.require(roles=["Monitor"], user_is_admin=True)
    def DELETE(self, name):
        session = cherrypy.request.db
        my_monitor = Monitor.del_one(session, name)
        if my_monitor == 0:
            cherrypy.response.headers['content-type'] = 'text/plain'
            return "Monitor deleted"
        else:
            raise cherrypy.HTTPError("404 Monitor %s not found" % name)
    
    """
    " curl -X POST -H "Content-Type: text/plain" -d "test" http://admin:admin@localhost:8090/user/andi/password
    """
    def POST(self, name, attrib):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        if (cherrypy.request.process_request_body == True):
            my_monitor = Monitor.edit_one(session, name, attrib, cherrypy.request.body.read())
            if isinstance(my_monitor, Monitor):
                return "Monitor: %s Attrib: %s\nPassword changed" % (name, attrib)
            elif my_monitor == -1:
                raise cherrypy.HTTPError("404 Attribute %s not found" % attrib)
            elif my_monitor == -2:
                raise cherrypy.HTTPError("404 Monitor %s not found" % name)
        else:
            raise cherrypy.HTTPError("404 No body")