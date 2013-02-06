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
import rasphome.api
import os
import os.path


def start_rasp_home_backend():
    db_path = os.path.abspath(os.path.join(os.curdir, 'rasp-home.db'))
    rasphome.database.set_db_path('sqlite:///%s' % (db_path))
    rasphome.database.SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = rasphome.database.SATool()
    
    root = rasphome.api.Root()
    root.user = rasphome.api.User_api()
    
    cherrypy.config.update({'server.socket_port': 8090})
    
    from cherrypy._cpserver import Server
    server = Server()
    server.socket_port = 8091
    server.ssl_certificate = './cert.pem'
    server.ssl_private_key = './privatekey.pem'
    server.subscribe()
    global user_dict
    
    config = { 
              '/' : {
                     'tools.auth_basic.on': True,
                     'tools.auth_basic.realm': 'earth',
                     'tools.auth_basic.checkpassword': rasphome.database.checkpassword_dict(),
                     'tools.db.on' : True
                     }
              }
    
    
    cherrypy.quickstart(root, '/', config)
   
    
    