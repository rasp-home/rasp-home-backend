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

__all__=['User_api']

import cherrypy
import xml.etree.ElementTree
from rasphome import authorization
from rasphome.models.User import User

class User_api(object):
    exposed = True
    
    """
    "curl http://admin:admin@localhost:8090/user/
    "curl http://admin:admin@localhost:8090/user?user=sw
    """
    def GET(self, name = None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        if name == None:
            msg = "All Users: \n"
            result = User.get_all(session)
            for name in result:
                msg = msg + str(name) + "\n"
            return msg
        else:
            my_user = User.get_one(session, name)
            if isinstance(my_user, User):
                return "User: \n" + str(my_user) + "\n"
            else:
                raise cherrypy.HTTPError("404 User %s not found" % name)
            
    
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
            
            User.add_one(session, name, password)
            return "User %s added." % (name)
        else:
            raise cherrypy.HTTPError("404 No body")
    
    """
    "curl -X DELETE http://admin:admin@localhost:8090/user/andi
    """
    @cherrypy.tools.require(roles=["User"], user_isAdmin=True)
    def DELETE(self, name):
        session = cherrypy.request.db
        my_user = User.del_one(session, name)
        if my_user == 0:
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
            my_user = User.edit_one(session, name, attrib, cherrypy.request.body.read())
            if isinstance(my_user, User):
                return "User: %s Attrib: %s" % (name, attrib)
            elif my_user == -1:
                raise cherrypy.HTTPError("404 Attribute %s not found" % attrib)
            elif my_user == -2:
                raise cherrypy.HTTPError("404 User %s not found" % name)
        else:
            raise cherrypy.HTTPError("404 No body")