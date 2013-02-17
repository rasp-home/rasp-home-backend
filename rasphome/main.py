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

from rasphome.config import rasp_settings
import cherrypy
import rasphome.database
import rasphome.authorization
import rasphome.api
import os.path
from logging import handlers, DEBUG, Formatter
        
def create_user(session, username, password):
    from rasphome.models import User
    my_user = User(username, password)
    my_user.isAdmin = True
    session.add(my_user)
    try:
        session.commit()
    except:
        session.rollback()      
          
def create_node(session, username, password):
    from rasphome.models import Node
    my_node = Node(username, password)
    session.add(my_node)
    try:
        session.commit()
    except:
        session.rollback()

@rasphome.database.rasp_db_session
def create_init_db(session):
    create_user(session, username="admin", password="admin")
    create_node(session, username="test", password="test")

def setUpLogger():
    log = cherrypy.log

    log.error_file = ""
    log.access_file = ""
    maxBytes = getattr(log, "rot_maxBytes", 10000000)
    backupCount = getattr(log, "rot_backupCount", 1000)

    # Make a new RotatingFileHandler for the error log.
    fname = getattr(log, "rot_error_file", "error.log")
    print("Error log filename: %s" % fname)
    h = handlers.RotatingFileHandler(fname, 'a', maxBytes, backupCount)
    h.setLevel(DEBUG)
    formatter = Formatter("%(asctime)s %(name)-12s %(threadName)-10s %(levelname)-8s %(message)s")
    h.setFormatter(formatter)
    log.error_log.addHandler(h)

    # Make a new RotatingFileHandler for the access log.
    fname = getattr(log, "rot_access_file", "access.log")
    print("Access log filename: %s" % fname)
    h = handlers.RotatingFileHandler(fname, 'a', maxBytes, backupCount)
    h.setLevel(DEBUG)
    formatter = Formatter("%(asctime)s %(name)-12s %(threadName)-10s %(levelname)-8s %(message)s")
    h.setFormatter(formatter)
    log.access_log.addHandler(h)

    cherrypy.log = log

def _get_root_start():
    ## Set up path to db file
    db_path = os.path.abspath(os.path.join(os.curdir, 'rasp-home.db'))
    rasphome.database.set_db_path('sqlite:///%s' % db_path)

    ## Set up Admin User name and Default admin user
    # noinspection PyArgumentList
    create_init_db()

    ## Set up Sqlalchemy Plugin and Tool
    rasphome.database.SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = rasphome.database.SATool()

    ## Set standard port
    cherrypy.config.update({'server.socket_port': rasp_settings.http_port})

    ## Activate additional SSL Server
    from cherrypy._cpserver import Server
    server = Server()
    server.socket_port = rasp_settings.https_port
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
    root.backend = rasphome.api.Backend_api()
    root.monitor = rasphome.api.Monitor_api()
    root.node = rasphome.api.Node_api()
    root.room = rasphome.api.Room_api()
    root.user = rasphome.api.User_api()

    setUpLogger()
    return root, config


def start_rasp_home_backend(testing=False):
    """
    Start rasp-home-backend
    :return:
    """
    root, config = _get_root_start()
    if not testing:
        cherrypy.quickstart(root, '/', config)
    else:
        cherrypy.tree.mount(root, '/', config)