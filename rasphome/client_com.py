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
from base64 import b64encode
from http.client import HTTPSConnection
from rasphome.models import Role
from rasphome.models import Backend
from rasphome.models import Monitor
from rasphome.models import User
from multiprocessing import Process

# TODO: Support HTTP and HTTPS support
# TODO: Use process not thread and create new session of database
# @rasp_db_session def send_request(session, ...)
def send_request(role, method, type, name, attrib, value, value_type):
    host = role.ip + ":" + role.serverport
    auth = b64encode((role.backend_name + ":" + role.backend_pass).encode()).decode()
    uri = "/" + type + ("/" + name) if name != None else "" + ("/" + attrib) if attrib != None else ""
    header = {"Authorization": "Basic " + auth}
    if value_type != None:
        header["Content-type"] = value_type
    client = HTTPSConnection(host, timeout=5)
    try:
        print("Send request: %s %s" % (host, uri))
        client.request(method, uri, value, header)
        response = client.getresponse()
        client.close()
        print("Get response: %s %s %s" % (response.status, response.reason, response.read()))
        return response
    except:
        print("Send error: %s %s" % (host, uri))
        role.active = False
        return None

def send_requests(roles, method, type, name, attrib, value, value_type):
    session = cherrypy.request.db
    elements = []
    if "backend" in roles:
        elements.extend(Backend.get_all(session, active=True))
    if "monitor" in roles:
        elements.extend(Monitor.get_all(session, active=True))
    if "user" in roles:
        elements.extend(User.get_all(session, "room", roles["user"], active=True))
    for element in elements:
        response = send_request(element, method, type, value, name, attrib)

def send_request_process(role, method, type, name, attrib, value, value_type):
    Process(target=send_request, args=(role, method, type, name, attrib, value, value_type, attrib)).start()

def send_requests_process(roles, method, type, name, value, value_type, attrib=None):
    Process(target=send_requests, args=(roles, method, type, name, attrib, value, value_type, attrib)).start()
