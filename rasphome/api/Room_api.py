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

__all__ = ['Room_api']

import cherrypy
from rasphome import authorization
from rasphome.models.Room import Room

class Room_api(object):
    exposed = True
    
    """
    "curl http://admin:admin@localhost:8090/room
    "curl http://admin:admin@localhost:8090/room/test1
    """
    @cherrypy.tools.require(roles={"Backend":[], "Monitor":[], "User":[]})
    def GET(self, name=None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        if name == None:
            elements = Room.get_all(session)
            if isinstance(elements, list):
                return Room.export_all(elements, ["name"])
        else:
            element = Room.get_one(session, name)
            if isinstance(element, Room):
                return Room.export_one(element, "all")
            else:
                raise cherrypy.HTTPError("404", "Room %s not found" % name)
    
    """
    " curl -X PUT -H "Content-Type: text/xml" -d "<room></room>" http://admin:admin@localhost:8090/room/test1
    " curl -X PUT -H "Content-Type: text/plain" -d "test2" http://admin:admin@localhost:8090/room/name
    """
    @cherrypy.tools.require(roles={"Backend":[], "User":["is_admin"]})
    def PUT(self, name, attrib=None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        body = cherrypy.request.body.read().decode()
        if (cherrypy.request.process_request_body == True):
            if attrib == None:
                element = Room.import_one(session, body, name=name)
                if isinstance(element, Room):
                    element = Room.add_one(session, element)
                    if isinstance(element, Room):
                        return "Room %s added" % name
                    elif element == Room.ERROR_ELEMENT_ALREADY_EXISTS:
                        raise cherrypy.HTTPError("403", "Room %s already exists" % name)
                elif element == Room.ERROR_TAG_NOT_VALID:
                    raise cherrypy.HTTPError("400", "Tag not valid")
            else:
                element = Room.get_one(session, name)
                if isinstance(element, Room):
                    element = Room.edit_one(session, element, attrib, body)
                    if isinstance(element, Room):
                        return "Room %s attribute %s value %s changed" % (name, attrib, body)
                    elif element == Room.ERROR_ATTRIB_NOT_VALID:
                        raise cherrypy.HTTPError("404", "Attribute % not found" % attrib)
                elif element == Room.ERROR_ELEMENT_NOT_EXISTS:
                    raise cherrypy.HTTPError("404", "Room %s not found" % name)
        else:
            raise cherrypy.HTTPError("400", "No body specified")
        
    """
    "curl -X POST -H "Content-Type: text/xml" -d "<room><name>test2</name></room>" http://admin:admin@localhost:8090/room/test1
    """
    @cherrypy.tools.require(roles={"Backend":[], "User":["is_admin"]})
    def POST(self, name):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        body = cherrypy.request.body.read().decode()
        if (cherrypy.request.process_request_body == True):
            element = Room.get_one(session, name)
            if isinstance(element, Room):
                element = Room.import_one(session, body, element=element)
                if isinstance(element, Room):
                    return "Room %s updated" % name
                elif element == Room.ERROR_TAG_NOT_VALID:
                    raise cherrypy.HTTPError("400", "Tag not valid")
            elif element == Room.ERROR_ELEMENT_NOT_EXISTS:
                raise cherrypy.HTTPError("404", "Room %s not found" % name)
        else:
            raise cherrypy.HTTPError("400", "No body specified")
    
    """
    "curl -X DELETE http://admin:admin@localhost:8090/room/test1
    """
    @cherrypy.tools.require(roles={"Backend":[], "User":["is_admin"]})
    def DELETE(self, name):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        element = Room.get_one(session, name)
        if isinstance(element, Room):
            element = Room.del_one(session, element)
            if isinstance(element, Room):
                return "Room %s deleted" % name
        elif element == Room.ERROR_ELEMENT_NOT_EXISTS:
            raise cherrypy.HTTPError("404", "User %s not found" % name)
