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

__all__=['Backend_api']

import cherrypy
import xml.etree.ElementTree
from rasphome import authorization
from rasphome.models.Backend import Backend

class Backend_api(object):
    exposed = True
    
    """
    "curl http://admin:admin@localhost:8090/user/
    "curl http://admin:admin@localhost:8090/user?user=sw
    """
    def GET(self, name = None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        if name == None:
            msg = "All Backends: \n"
            result = Backend.get_all(session)
            for name in result:
                msg = msg + str(name) + "\n"
            return msg
        else:
            my_backend = Backend.get_one(session, name)
            if isinstance(my_backend, Backend):
                return "Backend: \n" + str(my_backend) + "\n"
            else:
                raise cherrypy.HTTPError("404 Backend %s not found" % name)
            
    
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
            
            Backend.add_one(session, name, password)
            return "Backend %s added." % (name)
        else:
            raise cherrypy.HTTPError("404 No body")
    
    """
    "curl -X DELETE http://admin:admin@localhost:8090/user/andi
    """
    @cherrypy.tools.require(roles=["User"], user_isAdmin=True)
    def DELETE(self, name):
        session = cherrypy.request.db
        my_backend = Backend.del_one(session, name)
        if my_backend == 0:
            cherrypy.response.headers['content-type'] = 'text/plain'
            return "User deleted"
        else:
            raise cherrypy.HTTPError("404 User %s not found" % name)
    
    """
    " curl -X POST -H "Content-Type: text/plain" -d "test" http://admin:admin@localhost:8090/user/andi/password
    """
    def POST(self, name, attrib):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        if (cherrypy.request.process_request_body == True):
            my_backend = Backend.edit_one(session, name, attrib, cherrypy.request.body.read())
            if isinstance(my_backend, Backend):
                return "User: %s Attrib: %s\nPassword changed" % (name, attrib)
            elif my_backend == -1:
                raise cherrypy.HTTPError("404 Attribute %s not found" % attrib)
            elif my_backend == -2:
                raise cherrypy.HTTPError("404 User %s not found" % name)
        else:
            raise cherrypy.HTTPError("404 No body")