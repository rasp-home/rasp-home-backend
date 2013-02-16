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

__all__ = ['Backend']

from sqlalchemy import  Column, Integer, String, Boolean, ForeignKey
from rasphome.models.Role import Role
from sqlalchemy.orm.exc import NoResultFound

class Backend(Role):
    __tablename__ = 'backend'
    id = Column(Integer, ForeignKey('role.id'), primary_key=True)
    master = Column(Boolean)
    
    __mapper_args__ = {
        'polymorphic_identity':'backend'
    }
    
    def __init__(self, name, password):
        super().__init__(name, password)
    
    def __repr__(self):
        return "<Backend %s>" % (self.name)

    @staticmethod
    def get_all(session):
        return session.query(Backend).all()
    
    @staticmethod
    def get_one(session, name):
        try:
            return session.query(Backend).filter(Backend.name == name).one()
        except NoResultFound:
            return -1
    
    @staticmethod
    def add_one(session, name, password):
        session.add(Backend(name, password))
        session.commit()
    
    @staticmethod
    def del_one(session, name):
        try:
            my_backend = session.query(Backend).filter(Backend.name == name).one()
            session.delete(my_backend)
            return 0
        except NoResultFound:
            return -1
        
    @staticmethod
    def edit_one(session, name, attrib, value):
        my_backend = Backend.get_one(session, name)
        if isinstance(my_backend, Backend):
            Role.edit_one(session, my_backend, attrib, value)
        else:
            return -2
