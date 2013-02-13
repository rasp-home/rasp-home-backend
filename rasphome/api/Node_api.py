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
    "curl http://admin:admin@localhost:8090/user/
    "curl http://admin:admin@localhost:8090/user?user=sw
    """
    def GET(self, name = None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        if name == None:
            msg = "All Nodes: \n"
            result = Node.get_all(session)
            for name in result:
                msg = msg + str(name) + "\n"
            return msg
        else:
            my_node = Node.get_one(session, name)
            if isinstance(my_node, Node):
                return "Node: \n" + str(my_node) + "\n"
            else:
                raise cherrypy.HTTPError("404 Node %s not found" % name)
            
    
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
            
            Node.add_one(session, name, password)
            return "Node %s added." % (name)
        else:
            raise cherrypy.HTTPError("404 No body")
    
    """
    "curl -X DELETE http://admin:admin@localhost:8090/user/andi
    """
    @cherrypy.tools.require(roles=["Node"], user_isAdmin=True)
    def DELETE(self, name):
        session = cherrypy.request.db
        my_node = Node.del_one(session, name)
        if my_node == 0:
            cherrypy.response.headers['content-type'] = 'text/plain'
            return "Node deleted"
        else:
            raise cherrypy.HTTPError("404 Node %s not found" % name)
    
    """
    " curl -X POST -H "Content-Type: text/plain" -d "test" http://admin:admin@localhost:8090/user/andi/password
    """
    def POST(self, name, attrib):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        if (cherrypy.request.process_request_body == True):
            my_node = Node.edit_one(session, name, attrib, cherrypy.request.body.read())
            if isinstance(my_node, Node):
                return "Node: %s Attrib: %s\nPassword changed" % (name, attrib)
            elif my_node == -1:
                raise cherrypy.HTTPError("404 Attribute %s not found" % attrib)
            elif my_node == -2:
                raise cherrypy.HTTPError("404 Node %s not found" % name)
        else:
            raise cherrypy.HTTPError("404 No body")
