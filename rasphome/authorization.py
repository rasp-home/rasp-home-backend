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

__all__ = ['checkpassword', 'require']

import cherrypy
from cherrypy import Tool
from sqlalchemy.orm.exc import NoResultFound
from rasphome.models.Role import Role
from rasphome.models.Backend import Backend

def checkpassword(type=None, type_password=None):
    def checkpassword(realm, username, password):
        session = cherrypy.request.db
        try:
            role = session.query(Role).filter(Role.name == username).one()
            if role.check_auth(password) == True:
                cherrypy.request.role = role
                return True
        except NoResultFound:
            pass
        if type != None and type_password != None and type == username and type_password == password:
            cherrypy.request.role = type
            return True
        return False
    
    return checkpassword

def require(roles=None):
    error = False
    role = cherrypy.request.role
    if roles != None:
        if isinstance(role, Role):
            if role.type not in roles:
                error = True
            else:
                if "admin" in roles[role.type]:
                    if role.admin == False:
                        error = True
                elif "self" in roles[role.type]:
                    match_name = cherrypy.request.path_info.split("/")
                    if len(match_name) < 3 or role.name != match_name[2]:
                        error = True
        else:
            if role not in roles:
                error = True
    if error:
        raise cherrypy.HTTPError("401", "You are not allowed to access this resource.") 

cherrypy.tools.require = Tool('before_handler', require)
