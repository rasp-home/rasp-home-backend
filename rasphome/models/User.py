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

__all__ = ['User']

from sqlalchemy import  Column, Integer, Boolean, ForeignKey
from rasphome.models.Role import Role
from rasphome.models.Room import Room
from sqlalchemy.orm.exc import NoResultFound

class User(Role):
    __tablename__ = 'user'
    id = Column(Integer, ForeignKey('role.id'), primary_key=True)
    room_id = Column(Integer, ForeignKey('room.id'))
    receive_room_id = Column(Integer, ForeignKey('room.id'))
    is_admin = Column(Boolean, default=False)
    
    __mapper_args__ = {
        'polymorphic_identity':'user'
    }
    
    def __init__(self, name, password):
        super().__init__(name, password)
    
    def __repr__(self):
        return "<User %s>" % (self.name)
    
    @staticmethod
    def get_all(session):
        return session.query(User).all()
    
    @staticmethod
    def get_one(session, name):
        try:
            return session.query(User).filter(User.name == name).one()
        except NoResultFound:
            return -1
    
    @staticmethod
    def add_one(session, name, password):
        session.add(User(name, password))
        session.commit()
    
    @staticmethod
    def del_one(session, name):
        try:
            my_user = session.query(User).filter(User.name == name).one()
            session.delete(my_user)
            return 0
        except NoResultFound:
            return -1
        
    @staticmethod
    def edit_one(session, name, attrib, value):
        my_user = User.get_one(session, name)
        if isinstance(my_user, User):
            if attrib == "room_id":
                my_room = Room.get_one(session, value)
                if isinstance(my_room, Room):
                    my_user.room_id = my_room
                    return my_user
                else:
                    return -3
            if attrib == "receive_room_id":
                my_room = Room.get_one(session, value)
                if isinstance(my_room, Room):
                    my_user.receive_room_id = my_room
                    return my_user
                else:
                    return -3
            elif attrib == "is_admin":
                if value == "True":
                    my_user.is_admin = True
                else:
                    my_user.is_admin = False
                return my_user
            else:
                return Role.edit_one(session, my_user, attrib, value)
        else:
            return -2
