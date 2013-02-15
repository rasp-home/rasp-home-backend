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
from cherrypy import Tool
from sqlalchemy.orm.exc import NoResultFound

def checkpassword():
    def checkpassword(realm, user, password):
        session = cherrypy.request.db
        from rasphome.models import Role
        try:
            results = session.query(Role).filter(Role.name == user).all()
            print("Check results %s" % results)
        except NoResultFound as e:
            print("noResults")
            return False
        else:
            print("inFound")
            found = False
            for role in results:
                if role.check_auth(password):
                    print("Password match")
                    found = True
                    cherrypy.request.role = role
                    return True
            return found
    
    return checkpassword

def require(roles = None, user_is_admin = None):
    noError = False
    print("Login: %s" % cherrypy.request.login)
    role = cherrypy.request.role
    if roles is not None:
        if role.__class__.__name__ in roles:
            if role.__class__.__name__ == "User" and user_is_admin == True:
                if role.isAdmin:
                    noError = True
            else :
                noError = True
    if not noError:
        raise cherrypy.HTTPError("403 Forbidden", "You are not allowed to access this resource.") 

cherrypy.tools.require = Tool('before_handler', require)