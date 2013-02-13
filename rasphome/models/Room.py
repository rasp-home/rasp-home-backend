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

__all__ = ['Room']

from sqlalchemy import  Column, Integer, String
from rasphome.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

class Room(Base):
    __tablename__ = 'room'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    user = relationship("User", backref="room")
    node = relationship("Node", backref="room")
    
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return "<Room %s>" % (self.name)
    
    @staticmethod
    def get_all(session):
        return session.query(Room).all()
    
    @staticmethod
    def get_one(session, name):
        try:
            return session.query(Room).filter(Room.name == name).one()
        except NoResultFound:
            return -1
    
    @staticmethod
    def add_one(session, name):
        session.add(Room(name))
        session.commit()
    
    @staticmethod
    def del_one(session, name):
        try:
            my_room = session.query(Room).filter(Room.name == name).one()
            session.delete(my_room)
            return 0
        except NoResultFound:
            return -1
        
    @staticmethod
    def edit_one(session, name, attrib, value):
        my_room = Room.get_one(session, name)
        if isinstance(my_room, Room):
            if attrib == "name":
                my_room.name = value
                return my_room
            else:
                return -1
        else:
            return -2
