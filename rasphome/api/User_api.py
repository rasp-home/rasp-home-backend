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

__all__ = ['User_api']

import cherrypy
from rasphome import authorization
from rasphome.models.User import User
from rasphome import client_com
from multiprocessing import Process

class User_api(object):
    exposed = True
    
    """
    "curl http://admin:admin@localhost:8090/user
    "curl http://admin:admin@localhost:8090/user?room=room1
    "curl http://admin:admin@localhost:8090/user/admin
    """
    @cherrypy.tools.require(roles={"backend":[], "monitor":[], "user":["admin"]})
    def GET(self, name=None, room=None, receive_room=None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        if name == None:
            if room != None:
                elements = User.get_all(session, "room", room)
            elif receive_room != None:
                elements = User.get_all(session, "receive_room", receive_room)
            else:
                elements = User.get_all(session)
            if isinstance(elements, list):
                return User.export_all(elements, ["name", "room", "receive_room"])
            elif elements == User.ERROR_VALUE_NOT_VALID:
                raise cherrypy.HTTPError("404", "Value %s of attribute %s not valid" % room, "room")
        else:
            element = User.get_one(session, name)
            if isinstance(element, User):
                return User.export_one(element, "all")
            elif elements == User.ERROR_ELEMENT_NOT_EXISTS:
                raise cherrypy.HTTPError("404", "User %s not found" % name)
    
    """
    " curl -X PUT -H "Content-Type: text/xml" -d "<user><password>user1</password><receive_room>test2</receive_room></user>" http://admin:admin@localhost:8090/user/user1
    " curl -X PUT -H "Content-Type: text/plain" -d "user1" http://admin:admin@localhost:8090/user/user1/password
    " curl -X PUT -H "Content-Type: text/plain" -d "room1" http://admin:admin@localhost:8090/user/user1/room
    """
    @cherrypy.tools.require(roles={"backend":[], "user":["admin", "self"]})
    def PUT(self, name, attrib=None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        body = cherrypy.request.body.read().decode()
        if (cherrypy.request.process_request_body == True):
            if attrib == None:
                element = User.import_one(session, body, name=name)
                if isinstance(element, User):
                    element = User.add_one(session, element)
                    if isinstance(element, User):
                        Process(target=client_com.send_requests, args=()).start()
                        return "User %s added" % name
                    elif element == User.ERROR_ELEMENT_ALREADY_EXISTS:
                        raise cherrypy.HTTPError("403", "User %s alread exists" % name)
                elif element == User.ERROR_VALUE_NOT_VALID:
                    raise cherrypy.HTTPError("403", "Value of attribute not valid")
                elif element == User.ERROR_TAG_NOT_VALID:
                    raise cherrypy.HTTPError("400", "Tag not valid")
            else:
                element = User.get_one(session, name)
                if isinstance(element, User):
                    element = User.edit_one(session, element, attrib, body)
                    if isinstance(element, User):
                        return "User %s attribute %s value %s changed" % (name, attrib, body)
                    elif element == User.ERROR_VALUE_NOT_VALID:
                        raise cherrypy.HTTPError("403", "Value %s of attribute %s not valid" % (body, attrib))
                    elif element == User.ERROR_ATTRIB_NOT_VALID:
                        raise cherrypy.HTTPError("404", "Attribute %s not found" % attrib)
                elif element == User.ERROR_ELEMENT_NOT_EXISTS:
                    raise cherrypy.HTTPError("404", "User %s not found" % name)
        else:
            raise cherrypy.HTTPError("400", "No body specified")
    
    """
    "curl -X POST -H "Content-Type: text/xml" -d "<user><login>False</login><serverport>8000</serverport></user>" http://admin:admin@localhost:8090/user/user1
    "curl -X POST -H "Content-Type: text/xml" -d "<user><room>room1</room><receive_room>room2</receive_room></user>" http://admin:admin@localhost:8090/user/user1
    """
    @cherrypy.tools.require(roles={"backend":[], "user":["admin"]})
    def POST(self, name):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        body = cherrypy.request.body.read().decode()
        if (cherrypy.request.process_request_body == True):
            element = User.get_one(session, name)
            if isinstance(element, User):
                element = User.import_one(session, body, element=element)
                if isinstance(element, User):
                    return "User %s updated" % name
                elif element == User.ERROR_VALUE_NOT_VALID:
                    raise cherrypy.HTTPError("403", "Value of attribute not valid")
                elif element == User.ERROR_TAG_NOT_VALID:
                    raise cherrypy.HTTPError("400", "Tag not valid")
            elif element == User.ERROR_ELEMENT_NOT_EXISTS:
                raise cherrypy.HTTPError("404", "User %s not found" % name)
        else:
            raise cherrypy.HTTPError("400", "No body specified")
        
    """
    "curl -X DELETE http://admin:admin@localhost:8090/user/user1
    """
    @cherrypy.tools.require(roles={"Backend":[], "User":["admin"]})
    def DELETE(self, name):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        element = User.get_one(session, name)
        if isinstance(element, User):
            element = User.del_one(session, element)
            if isinstance(element, User):
                return "User %s deleted" % name
        elif element == User.ERROR_ELEMENT_NOT_EXISTS:
            raise cherrypy.HTTPError("404", "User %s not found" % name)
