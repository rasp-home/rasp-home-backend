#!/usr/bin/python3
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

import cherrypy
from cherrypy.process import plugins
 
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

__all__ = ['SAEnginePlugin', 'SATool', 'set_db_path', 'Base', 'rasp_db_session']

general_db_path = 'sqlite:///:memory:'

def set_db_path(dbPath):
    global general_db_path
    general_db_path = dbPath



def _rasp_create_engine():
    global general_db_path
    return create_engine(general_db_path, echo=True, convert_unicode=True)

def _rasp_session(engine = None):
    
    if engine is None:
        return scoped_session(sessionmaker(autoflush=False, 
                                                autocommit=False))
    else:
        return scoped_session(sessionmaker(autoflush=False,
                                                autocommit=False,
                                                bind=engine))

Base = declarative_base()

def rasp_db_session(f):
    def wrapped_f(*args, **kwargs):
        engine = _rasp_create_engine()
        Base.metadata.create_all(engine)
        session = _rasp_session(engine)
        ret = f(session, *args, **kwargs)
        session.remove()
        engine.dispose()
        return ret
    return wrapped_f



# Import all Sqlalchemy Classes here
 
#Besser https://bitbucket.org/Lawouach/cherrypy-recipes/src/50aff88dc4e24206518ec32e1c32af043f2729da/web/database/sql_alchemy?at=default
# From: http://www.defuze.org/archives/222-integrating-sqlalchemy-into-a-cherrypy-application.html
 
class SAEnginePlugin(plugins.SimplePlugin):
    def __init__(self, bus):
        """
        The plugin is registered to the CherryPy engine and therefore
        is part of the bus (the engine *is* a bus) registery.
 
        We use this plugin to create the SA engine. At the same time,
        when the plugin starts we create the tables into the database
        using the mapped class of the global metadata.
 
        Finally we create a new 'bind' channel that the SA tool
        will use to map a session to the SA engine at request time.
        """
        plugins.SimplePlugin.__init__(self, bus)
        self.sa_engine = None
        self.bus.subscribe("bind", self.bind)
 
    def start(self):
        global general_db_path
        self.sa_engine = create_engine(general_db_path, echo=True, convert_unicode=True)
        Base.metadata.create_all(self.sa_engine)
 
    def stop(self):
        if self.sa_engine:
            self.sa_engine.dispose()
            self.sa_engine = None
 
    def bind(self, session):
        session.configure(bind=self.sa_engine)
 
class SATool(cherrypy.Tool):
    def __init__(self):
        """
        The SA tool is responsible for associating a SA session
        to the SA engine and attaching it to the current request.
        Since we are running in a multithreaded application,
        we use the scoped_session that will create a session
        on a per thread basis so that you don't worry about
        concurrency on the session object itself.
 
        This tools binds a session to the engine each time
        a requests starts and commits/rollbacks whenever
        the request terminates.
        """
        cherrypy.Tool.__init__(self, 'on_start_resource',
                               self.bind_session,
                               priority=20)
 
        self.session = _rasp_session()
 
    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('on_end_resource',
                                      self.commit_transaction,
                                      priority=80)
 
    def bind_session(self):
        cherrypy.engine.publish('bind', self.session)
        cherrypy.request.db = self.session
 
    def commit_transaction(self):
        cherrypy.request.db = None
        try:
            self.session.commit()
        except:
            self.session.rollback()  
            raise
        finally:
            self.session.remove()
 



