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
from rasphome.models import User
from rasphome import authorization
from sqlalchemy.orm.exc import NoResultFound

class User_api(object):
    exposed = True
    
    """
    "curl http://admin:admin@localhost:8090/user/
    "curl http://admin:admin@localhost:8090/user?user=sw
    """
    def GET(self, user = None):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        if user is None:
            msg = "List of Users: \n"
            result = session.query(User).all()
            for user in result:
                msg = msg + str(user) + "\n"
            return msg
        else:
            try:
                my_user = session.query(User).filter(User.name==user).one()
            except NoResultFound:
                raise cherrypy.HTTPError("404 User %s not found" % user)
            return "User: \n" + str(my_user[0]) + "\n"
    
    """
    "curl -X PUT -H "Content-Type: text/xml" -d "<user><name>andi</name><password>test</password></user>" http://admin:admin@localhost:8090/user
    """
    @cherrypy.tools.auth_basic(on=False)
    def PUT(self):
        if cherrypy.request.process_request_body:
            txt = cherrypy.request.body.read()
        else:
            raise cherrypy.HTTPError("404 No body")
        tree = xml.etree.ElementTree.fromstring(txt)
        name = tree.find("name").text
        password = tree.find("password").text
            
        my_user = User(name, password)
        cherrypy.request.db.add(my_user)
        cherrypy.request.db.commit()
        cherrypy.response.headers['content-type'] = 'text/plain'
        return "User %s added." % my_user.name
    
    """
    "curl -X DELETE http://admin:admin@localhost:8090/user/andi
    """
    @cherrypy.tools.require(roles=["User"], user_isAdmin=True)
    def DELETE(self, user):
        session = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        try:
            my_user = session.query(User).filter(User.name==user).one()
        except NoResultFound:
            raise cherrypy.HTTPError("404 User %s not found" % user)
        session.delete(my_user)
        return "User deleted"
    
    """
    " curl -X POST -H "Content-Type: text/plain" -d "test" http://admin:admin@localhost:8090/user/andi/password
    """
    def POST(self, user, attrib):
        cherrypy.response.headers['content-type'] = 'text/plain'
        msg = "User: %s Attrib: %s" % (user, attrib)
        try:
            my_user = cherrypy.request.db.query(User).filter(User.name==user).one()
        except NoResultFound:
            raise cherrypy.HTTPError("404 User %s not found" % user)
        if cherrypy.request.process_request_body:
            if attrib == "password":
                my_user.password(cherrypy.request.body.read())
                return msg + "Password changed"
            else:
                raise cherrypy.HTTPError("404 Attribute %s not found" % attrib)
        else:
            raise cherrypy.HTTPError("404 No body")
        