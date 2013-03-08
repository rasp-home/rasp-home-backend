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

__all__=['Node_api']

import cherrypy
import xml.etree.ElementTree
from rasphome import authorization
from rasphome.models.Node import Node

class Node_api(object):
    exposed = True

    """
    "curl http://admin:admin@localhost:8090/node
    "curl http://admin:admin@localhost:8090/node?room=room1
    "curl http://admin:admin@localhost:8090/node/node1
    """
    @cherrypy.tools.require(roles={"backend":[], "monitor":[], "user":[]})
    def GET(self, name=None, room=None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        if name == None:
            elements = Node.get_all(session, room)
            if isinstance(elements, list):
                if isinstance(cherrypy.request.role, User):
                    return Node.export_all(elements, ["name", "room", "title", "type", "input", "output"])
                else:
                    return Node.export_all(elements, "all")
            elif elements == Node.ERROR_VALUE_NOT_VALID:
                raise cherrypy.HTTPError("404", "Value %s of attribute %s not valid" % room, "room")
        else:
            element = Node.get_one(session, name)
            if isinstance(element, Node):
                return Node.export_one(element, "all")
            elif elements == Node.ERROR_ELEMENT_NOT_EXISTS:
                raise cherrypy.HTTPError("404", "Node %s not found" % name)
    
    """
    " curl -X PUT -H "Content-Type: text/xml" -d "<node><password>node1</password><receive_room>test2</receive_room></node>" http://admin:admin@localhost:8090/node/node1
    " curl -X PUT -H "Content-Type: text/plain" -d "test2" http://admin:admin@localhost:8090/node/node1/room
    """
    @cherrypy.tools.auth_basic(checkpassword=authorization.checkpassword("node", "node"))
    @cherrypy.tools.require(roles={"backend":[], "node":["self"]})
    def PUT(self, name, attrib=None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        body = cherrypy.request.body.read().decode()
        if (cherrypy.request.process_request_body == True):
            if attrib == None:
                element = Node.import_one(session, body, name=name)
                if isinstance(element, Node):
                    element = Node.add_one(session, element)
                    if isinstance(element, Node):
                        client_com.send_requests_process({"backend": None, "monitor": None, "user": element.room}, "PUT", "node", name, attrib, body, "text/xml")
                        return "Node %s added" % name
                    elif element == Node.ERROR_ELEMENT_ALREADY_EXISTS:
                        raise cherrypy.HTTPError("403", "Node %s alread exists" % name)
                elif element == Node.ERROR_VALUE_NOT_VALID:
                    raise cherrypy.HTTPError("403", "Value of attribute not valid")
                elif element == Node.ERROR_TAG_NOT_VALID:
                    raise cherrypy.HTTPError("400", "Tag not valid")
            else:
                if not isinstance(cherrypy.request.role, str):
                    element = Node.get_one(session, name)
                    if isinstance(element, Node):
                        old_room = element.room
                        element = Node.edit_one(session, element, attrib, body)
                        if isinstance(element, Node):
                            if old_room != element.room:
                                client_com.send_requests_process({"user": old_room}, "DELETE", "node", name, None, None, None)
                                client_com.send_requests_process({"user": element.room}, "PUT", "node", name, None, Node.export_one(element, ["name", "room", "title", "type", "input", "output"]), "text/xml")
                            else:
                                client_com.send_requests_process({"user": element.room}, "PUT", "node", name, attrib, body, "text/plain")
                            client_com.send_requests_process({"backend": None, "monitor": None}, "PUT", "node", name, attrib, body, "text/plain")
                            return "Node %s attribute %s value %s changed" % (name, attrib, body)
                        elif element == Node.ERROR_VALUE_NOT_VALID:
                            raise cherrypy.HTTPError("403", "Value %s of attribute %s not valid" % (body, attrib))
                        elif element == Node.ERROR_ATTRIB_NOT_VALID:
                            raise cherrypy.HTTPError("404", "Attribute %s not found" % attrib)
                    elif element == Node.ERROR_ELEMENT_NOT_EXISTS:
                        raise cherrypy.HTTPError("404", "Node %s not found" % name)
                else:
                    raise cherrypy.HTTPError("401", "You are not allowed to access this resource.")
        else:
            raise cherrypy.HTTPError("400", "No body specified")
    
    """
    "curl -X POST -H "Content-Type: text/xml" -d "<node><room>room2</room><title>Node1</title></user>" http://admin:admin@localhost:8090/node/node1
    """
    @cherrypy.tools.require(roles={"backend":[], "node":["self"], "user":[]})
    def POST(self, name):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        body = cherrypy.request.body.read().decode()
        if (cherrypy.request.process_request_body == True):
            element = Node.get_one(session, name)
            if isinstance(element, Node):
                old_room = element.room
                element = Node.import_one(session, body, element=element)
                if isinstance(element, Node):
                    if old_room != element.room:
                        client_com.send_requests_process({"user": old_room}, "DELETE", "node", name, None, None, None)
                        client_com.send_requests_process({"user": element.room}, "PUT", "node", name, None, Node.export_one(element, ["name", "room", "title", "type", "input", "output"]), "text/xml")
                    else:
                        client_com.send_requests_process({"user": element.room}, "POST", "node", name, None, body, "text/xml")
                    client_com.send_requests_process({"backend": None, "monitor": None}, "POST", "node", name, None, body, "text/xml")
                    return "Node %s updated" % name
                elif element == Node.ERROR_VALUE_NOT_VALID:
                    raise cherrypy.HTTPError("403", "Value of attribute not valid")
                elif element == Node.ERROR_TAG_NOT_VALID:
                    raise cherrypy.HTTPError("400", "Tag not valid")
            elif element == Node.ERROR_ELEMENT_NOT_EXISTS:
                raise cherrypy.HTTPError("404", "Node %s not found" % name)
        else:
            raise cherrypy.HTTPError("400", "No body specified")
        
    """
    "curl -X DELETE http://admin:admin@localhost:8090/node/node1
    """
    @cherrypy.tools.require(roles={"backend":[], "node":["self"]})
    def DELETE(self, name):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        element = Node.get_one(session, name)
        if isinstance(element, Node):
            element = Node.del_one(session, element)
            if isinstance(element, Node):
                client_com.send_requests_process({"backend": None, "monitor": None, "user": element.room}, "DELETE", "node", name, None, None, None)
                return "Node %s deleted" % name
        elif element == Node.ERROR_ELEMENT_NOT_EXISTS:
            raise cherrypy.HTTPError("404", "Node %s not found" % name)
