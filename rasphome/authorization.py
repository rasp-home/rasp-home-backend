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

## BESSER: http://docs.cherrypy.org/stable/progguide/extending/customtools.html
## see http://tools.cherrypy.org/wiki/AuthenticationAndAccessRestrictions

__all__=['checkpassword', 'protect']
import cherrypy
from cherrypy import tools
from cherrypy import Tool
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound


def checkpassword():
    def checkpassword(realm, user, password):
        session = cherrypy.request.db
        from rasphome.models import User
        try:
            results = session.query(User).filter(User.name == user).all()
            print("Check results %s" % (results))
        except NoResultFound as e:
            print("noResults")
            return False
        else:
            print("inFound")
            found = False
            for user in results:
                if user.check_auth(password):
                    print("password match")
                    found = True
                    cherrypy.request.user = user
                    return True
            return found
    
    return checkpassword

def require(roles = None, users = None):
    noError = False
    print("Login: %s" % (cherrypy.request.login))
    user = cherrypy.request.user
    if roles != None and users == None:
        for role in roles:
            if user.has_role(role):
                noError = True
                break
    elif users != None and roles == None:
        if user.name in users:
            noError = False
        else:
            noError = True
    elif user != None and roles != None:
        if not user.name in users:
            for role in roles:
                if user.has_role(role):
                    noError = True
                    break
        else:
            noError = True
    
    if noError == False:
        raise cherrypy.HTTPError("403 Forbidden", "You are not allowed to access this resource.") 

cherrypy.tools.protect = Tool('before_handler', require)