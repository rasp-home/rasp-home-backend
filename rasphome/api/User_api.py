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
import rasphome.database
from rasphome.models import User
from rasphome import authorization
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

class User_api(object):
    
    @cherrypy.expose
    def index(self):
        msg = "List of Users: \n"
        
        db = cherrypy.request.db
        cherrypy.response.headers['content-type'] = 'text/plain'
        result = db.query(User).all()
        for user in result:
            msg = msg + str(user) + "\n"
        return msg
    
    @cherrypy.expose
    def add(self, name, password):
        user = User(name, password)
        cherrypy.request.db.add(user)
        cherrypy.request.db.commit()
        cherrypy.response.headers['content-type'] = 'text/plain'
        return "User %s added." % (user.name)
    
    @cherrypy.expose
    @cherrypy.tools.protect(roles=["admin"])
    def delete(self, name):
        cherrypy.response.headers['content-type'] = 'text/plain'
        try:
            result = cherrypy.request.db.query(User).filter(User.name==name).one()
        except MultipleResultsFound as e:
            return "Multiple users with name %s found!" % (name)
        except NoResultFound as e:
            return "There is no user with name %s!" % (name)
        cherrypy.request.db.delete(result)
        return "User deleted"
    
    @cherrypy.expose
    def password(self, name, password):
        cherrypy.response.headers['content-type'] = 'text/plain'
        try:
            result = cherrypy.request.db.query(User).filter(User.name==name).one()
        except MultipleResultsFound as e:
            return "Multiple users with name %s found!" % (name)
        except NoResultFound as e:
            return "There is no user with name %s!" % (name)
        else:
            result.password = password
            return "Password changed"