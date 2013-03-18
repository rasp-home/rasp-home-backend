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

__all__ = ['Backend_api']

import cherrypy
import xml.etree.ElementTree
from rasphome import authorization
from rasphome.models.Backend import Backend
from rasphome import client_com

class Backend_api(object):
    exposed = True
    
    """
    "curl http://admin:admin@localhost:8090/backend/
    "curl http://admin:admin@localhost:8090/backend?master=true
    """
    @cherrypy.tools.require(roles={"backend":[]})
    def GET(self, name=None, master=None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        if name == None:
            elements = Backend.get_all(session, "master", master)
            if isinstance(elements, list):
                return Backend.export_all(elements, "all")
        else:
            element = Backend.get_one(session, name)
            if isinstance(element, Backend):
                return Backend.export_one(element, "all")
            elif elements == Backend.ERROR_ELEMENT_NOT_EXISTS:
                raise cherrypy.HTTPError("404", "Backend %s not found" % name)
    
    """
    " curl -X PUT -H "Content-Type: text/xml" -d "<backend><password>backend1</password><master>True</master></backend>" http://admin:admin@localhost:8090/backend/backend1
    " curl -X PUT -H "Content-Type: text/plain" -d "False" http://admin:admin@localhost:8090/backend/backend1/master
    """
    @cherrypy.tools.auth_basic(checkpassword=authorization.checkpassword("backend", "backend"))
    @cherrypy.tools.require(roles={"backend":[]})
    def PUT(self, name, attrib=None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        body = cherrypy.request.body.read().decode()
        if (cherrypy.request.process_request_body == True):
            if attrib == None:
                element = Backend.import_one(session, body, name=name)
                if isinstance(element, Backend):
                    element = Backend.add_one(session, element)
                    if isinstance(element, Backend):
                        client_com.send_requests_process({"backend": None}, "PUT", "backend", name, attrib, body, "text/xml")
                        return "Backend %s added" % name
                    elif element == Backend.ERROR_ELEMENT_ALREADY_EXISTS:
                        raise cherrypy.HTTPError("403", "Backend %s alread exists" % name)
                elif element == Backend.ERROR_TAG_NOT_VALID:
                    raise cherrypy.HTTPError("400", "Tag not valid")
            else:
                if not isinstance(cherrypy.request.role, str):
                    element = Backend.get_one(session, name)
                    if isinstance(element, Backend):
                        element = Backend.edit_one(session, element, attrib, body)
                        if isinstance(element, Backend):
                            client_com.send_requests_process({"backend": None}, "PUT", "backend", name, attrib, body, "text/plain")
                            return "Backend %s attribute %s value %s changed" % (name, attrib, body)
                        elif element == Backend.ERROR_ATTRIB_NOT_VALID:
                            raise cherrypy.HTTPError("404", "Attribute %s not found" % attrib)
                    elif element == Backend.ERROR_ELEMENT_NOT_EXISTS:
                        raise cherrypy.HTTPError("404", "Backend %s not found" % name)
                else:
                    raise cherrypy.HTTPError("401", "You are not allowed to access this resource.")
        else:
            raise cherrypy.HTTPError("400", "No body specified")
    
    """
    "curl -X POST -H "Content-Type: text/xml" -d "<backend><master>True</master></backend>" http://admin:admin@localhost:8090/backend/backend1
    """
    @cherrypy.tools.require(roles={"backend":[]})
    def POST(self, name):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        body = cherrypy.request.body.read().decode()
        if (cherrypy.request.process_request_body == True):
            element = Backend.get_one(session, name)
            if isinstance(element, Backend):
                element = Backend.import_one(session, body, element=element)
                if isinstance(element, Backend):
                    client_com.send_requests_process({"backend": None}, "POST", "backend", name, None, body, "text/xml")
                    return "Backend %s updated" % name
                elif element == Backend.ERROR_TAG_NOT_VALID:
                    raise cherrypy.HTTPError("400", "Tag not valid")
            elif element == Backend.ERROR_ELEMENT_NOT_EXISTS:
                raise cherrypy.HTTPError("404", "Backend %s not found" % name)
        else:
            raise cherrypy.HTTPError("400", "No body specified")
       
    """
    "curl -X DELETE http://admin:admin@localhost:8090/backend/backend1
    """
    @cherrypy.tools.require(roles={"backend":[]})
    def DELETE(self, name):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        element = Backend.get_one(session, name)
        if isinstance(element, Backend):
            element = Backend.del_one(session, element)
            if isinstance(element, Backend):
                client_com.send_requests_process({"backend": None}, "DELETE", "backend", name, None, None, None)
                return "Backend %s deleted" % name
        elif element == Backend.ERROR_ELEMENT_NOT_EXISTS:
            raise cherrypy.HTTPError("404", "Backend %s not found" % name)
