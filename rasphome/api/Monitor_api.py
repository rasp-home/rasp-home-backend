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
    "curl http://admin:admin@localhost:8090/monitor
    "curl http://admin:admin@localhost:8090/monitor/monitor1
    """
    @cherrypy.tools.require(roles={"Backend":[], "Monitor":["self"]})
    def GET(self, name=None, room=None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        if name == None:
            elements = Monitor.get_all(session, room)
            if isinstance(elements, list):
                return Monitor.export_all(elements, ["name"])
        else:
            element = Monitor.get_one(session, name)
            if isinstance(element, Monitor):
                return Monitor.export_one(element, "all")
            elif elements == Monitor.ERROR_ELEMENT_NOT_EXISTS:
                raise cherrypy.HTTPError("404", "Monitor %s not found" % name)
    
    """
    " curl -X PUT -H "Content-Type: text/xml" -d "<monitor><password>monitor1</password></monitor>" http://admin:admin@localhost:8090/monitor/monitor1
    " curl -X PUT -H "Content-Type: text/plain" -d "test123" http://admin:admin@localhost:8090/monitor/monitor1/password
    """
    @cherrypy.tools.auth_basic(on=False)
    def PUT(self, name, attrib=None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        body = cherrypy.request.body.read().decode()
        if (cherrypy.request.process_request_body == True):
            if attrib == None:
                element = Monitor.import_one(session, body, name=name)
                if isinstance(element, Monitor):
                    element = Monitor.add_one(session, element)
                    if isinstance(element, Monitor):
                        return "Monitor %s added" % name
                    elif element == Monitor.ERROR_ELEMENT_ALREADY_EXISTS:
                        raise cherrypy.HTTPError("403", "Monitor %s alread exists" % name)
                elif element == Monitor.ERROR_TAG_NOT_VALID:
                    raise cherrypy.HTTPError("400", "Tag not valid")
            else:
                element = Monitor.get_one(session, name)
                if isinstance(element, Monitor):
                    element = Monitor.edit_one(session, element, attrib, body)
                    if isinstance(element, Monitor):
                        return "Monitor %s attribute %s value %s changed" % (name, attrib, body)
                    elif element == Monitor.ERROR_ATTRIB_NOT_VALID:
                        raise cherrypy.HTTPError("404", "Attribute %s not found" % attrib)
                elif element == Monitor.ERROR_ELEMENT_NOT_EXISTS:
                    raise cherrypy.HTTPError("404", "Monitor %s not found" % name)
        else:
            raise cherrypy.HTTPError("400", "No body specified")
    
    """
    "curl -X POST -H "Content-Type: text/xml" -d "<monitor><password>monitor1</password></user>" http://admin:admin@localhost:8090/monitor/monitor1
    """
    @cherrypy.tools.require(roles={"Backend":[], "Monitor":["self"]})
    def POST(self, name):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        body = cherrypy.request.body.read().decode()
        if (cherrypy.request.process_request_body == True):
            element = Monitor.get_one(session, name)
            if isinstance(element, Monitor):
                element = Monitor.import_one(session, body, element=element)
                if isinstance(element, Monitor):
                    return "Monitor %s updated" % name
                elif element == Monitor.ERROR_TAG_NOT_VALID:
                    raise cherrypy.HTTPError("400", "Tag not valid")
            elif element == Monitor.ERROR_ELEMENT_NOT_EXISTS:
                raise cherrypy.HTTPError("404", "Monitor %s not found" % name)
        else:
            raise cherrypy.HTTPError("400", "No body specified")
        
    """
    "curl -X DELETE http://admin:admin@localhost:8090/monitor/monitor1
    """
    @cherrypy.tools.require(roles={"Backend":[], "Monitor":["self"]})
    def DELETE(self, name):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        element = Monitor.get_one(session, name)
        if isinstance(element, Monitor):
            element = Monitor.del_one(session, element)
            if isinstance(element, Monitor):
                return "Monitor %s deleted" % name
        elif element == Monitor.ERROR_ELEMENT_NOT_EXISTS:
            raise cherrypy.HTTPError("404", "Monitor %s not found" % name)