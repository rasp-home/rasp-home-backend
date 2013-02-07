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
# You should have received a copy of the GNU Lesser General Publ     ic License
# along with rasp-home-backend.  If not, see <http://www.gnu.org/licenses/>.

import cherrypy
import rasphome.database
import rasphome.authorization
import rasphome.api
import os
import os.path
from sqlalchemy.orm.exc import NoResultFound

def create_role(session, role):
    from rasphome.models import Role
    
    my_role = Role(name=role)
    session.add(my_role)
    try:
        session.commit()
    except:
        session.rollback()
        
def create_user(session, username, password, role):
    from rasphome.models import Role
    from rasphome.models import User
    
    my_user = User(username, password)
    session.add(my_user)
    
    try:
        my_role = session.query(Role).filter(Role.name==role).all()[0]
        my_user.roles.append(my_role)
    except NoResultFound:
        pass
    
    try:
        session.commit()
    except:
        session.rollback()



@rasphome.database.rasp_db_session
def create_init_db(session):
    create_role(session, role="admin")
    create_user(session, username="admin", password="admin", role="admin")



def start_rasp_home_backend():
    ## Set up path to db file
    db_path = os.path.abspath(os.path.join(os.curdir, 'rasp-home.db'))
    rasphome.database.set_db_path('sqlite:///%s' % (db_path))
    
    ## Set up Admin User name and Default admin user
    create_init_db()
    
    ## Set up Sqlalchemy Plugin and Tool
    rasphome.database.SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = rasphome.database.SATool()
    
    
    ## Set standard port
    cherrypy.config.update({'server.socket_port': 8090})
    
    ## Activate additional SSL Server
    from cherrypy._cpserver import Server
    server = Server()
    server.socket_port = 8091
    server.ssl_certificate = './cert.pem'
    server.ssl_private_key = './privatekey.pem'
    server.subscribe()
    
    
    ## Do other config
    config = { 
              '/' : {
                     'tools.auth_basic.on': True,
                     'tools.auth_basic.realm': 'earth',
                     'tools.auth_basic.checkpassword': rasphome.authorization.checkpassword(),
                     'tools.db.on' : True,
                     'request.dispatch': cherrypy.dispatch.MethodDispatcher()
                     }
              }
    
    ## Set up Api
    root = rasphome.api.Root()
    root.user = rasphome.api.User_api()
    
    #application = cherrypy.tree.mount(root, '/', config)
    
    #cherrypy.engine.start()
    
    cherrypy.quickstart(root, '/', config)
   
    
    