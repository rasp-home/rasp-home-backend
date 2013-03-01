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

# # BESSER: http://docs.cherrypy.org/stable/progguide/extending/customtools.html
# # see http://tools.cherrypy.org/wiki/AuthenticationAndAccessRestrictions

__all__ = ['send_request', 'send_requests']

import cherrypy
from http.client import HTTPSConnection
from rasphome.models import Role
from rasphome.models import Backend
from rasphome.models import Monitor
from rasphome.models import User

#TODO: Use process not thread and create new session of database
#@rasp_db_session def send_request(session, ...)
#TODO: Complete function with error handling
def send_request(role, method, type, value, value_type, name=None, attrib=None):
    uri = "/" + type
    if name != None:
        uri += "/" + name
    if attrib != None:
        uri += "/" + attrib
    client = HTTPSConnection(role.backend_name + ":" + role.backend_pass + "@" + role.ip + ":" + role.serverport, timeout=5)
    header = {"Content-type": value_type}
    try:
        client.request("GET", "/uri", value, header)
        response = client.getresponse()
        client.close()
        #print(response.status + " " + response.reason + " " + response.read())
        return response
    except:
        return None

#TODO: Complete function with error handling
def send_requests(roles, method, type, value, value_type, name=None, attrib=None):
    session = cherrypy.request.db
    elements = []
    if "backend" in roles:
        elements.extend(Backend.get_all(session))
    if "monitor" in roles:
        elements.extend(Monitor.get_all(session))
    if "user" in roles:
        if len(roles["user"]) == 2:
            elements.extend(User.get_all(session, roles["user"][0], roles["user"][1]))
        else:
            elements.extend(User.get_all(session))
    for element in elements:
        response = send_request(element, method, type, value, name, attrib)
        if response == None:
            pass