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

__all__ = ['Node']

from sqlalchemy import  Column, Integer, String, ForeignKey
from rasphome.models.Role import Role
from rasphome.models.Room import Room
from sqlalchemy.orm.exc import NoResultFound

class Node(Role):
    __tablename__ = 'node'
    id = Column(Integer, ForeignKey('role.id'), primary_key=True)
    room_id = Column(Integer, ForeignKey('room.id'))
    title = Column(String(50))
    type = Column(String(50))
    input = Column(String(50))
    output = Column(String(50))
    
    __mapper_args__ = {
        'polymorphic_identity':'node'
    }
    
    def __init__(self, name, password):
        super().__init__(name, password)
    
    def __repr__(self):
        return "<Node %s>" % (self.name)

    @staticmethod
    def get_all(session):
        return session.query(Node).all()
    
    @staticmethod
    def get_one(session, name):
        try:
            return session.query(Node).filter(Node.name == name).one()
        except NoResultFound:
            return -1
    
    @staticmethod
    def add_one(session, name, password):
        session.add(Node(name, password))
        session.commit()
    
    @staticmethod
    def del_one(session, name):
        try:
            my_node = session.query(Node).filter(Node.name == name).one()
            session.delete(my_node)
            return 0
        except NoResultFound:
            return -1
        
    @staticmethod
    def edit_one(session, name, attrib, value):
        my_node = Node.get_one(session, name)
        if isinstance(my_node, Node):
            if attrib == "room_id":
                my_room = Room.get_one(session, value)
                if isinstance(my_room, Room):
                    my_node.room_id = my_room
                    return my_node
                else:
                    return -3
            elif attrib == "title":
                my_node.title = value
                return my_node
            elif attrib == "type":
                my_node.type = value
                return my_node
            elif attrib == "input":
                my_node.input = value
                return my_node
            elif attrib == "output":
                my_node.output = value
                return my_node
            else:
                return Role.edit_one(session, my_node, attrib, value)
        else:
            return -2
