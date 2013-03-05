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
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from xml.etree import ElementTree
from rasphome.models.Role import Role
from rasphome.models.Room import Room

class User(Role):
    ERROR_VALUE_NOT_VALID = -2
    ERROR_ELEMENT_ALREADY_EXISTS = -3
    ERROR_ELEMENT_NOT_EXISTS = -4
    ERROR_TAG_NOT_VALID = -5
    
    __tablename__ = 'user'
    id = Column(Integer, ForeignKey('role.id'), primary_key=True)
    room_id = Column(Integer, ForeignKey('room.id'))
    room = relationship(Room, primaryjoin=room_id==Room.id, foreign_keys=[room_id])
    receive_room_id = Column(Integer, ForeignKey('room.id'))
    receive_room = relationship(Room, primaryjoin=receive_room_id==Room.id, foreign_keys=[receive_room_id])
    admin = Column(Boolean, default=False)
    
    __mapper_args__ = {
        'polymorphic_identity':'user'
    }
    
    def __repr__(self):
        return "<User %s>" % (self.name)
    
    @staticmethod
    def export_one(element, attribs):
        tree = ElementTree.Element("user")
        tree = Role.export_one(tree, element, attribs)
        if "room" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "room")
            if element.room != None:
                attrib.text = element.room.name
        if "receive_room" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "receive_room")
            if element.receive_room != None:
                attrib.text = element.receive_room.name
        if "admin" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "admin")
            if element.admin != None:
                if element.admin == True:
                    attrib.text = "True"
                else:
                    attrib.text = "False"
        return ElementTree.tostring(tree, "UTF-8")
    
    @staticmethod
    def export_all(elements, attribs):
        tree = ElementTree.Element("users")
        for element in elements:
            tree.append(ElementTree.fromstring(User.export_one(element, attribs)))
        return ElementTree.tostring(tree, "UTF-8")
    
    @staticmethod
    def get_one(session, name):
        try:
            return session.query(User).filter(User.name == name).one()
        except NoResultFound:
            return User.ERROR_ELEMENT_NOT_EXISTS
    
    @staticmethod
    def get_all(session, attrib=None, value=None):
        if attrib == None:
            return session.query(User).all()
        elif attrib == "room":
            my_room = Room.get_one(session, value)
            if isinstance(my_room, Room):
                return session.query(User).filter(User.room == my_room).all()
            else:
                return User.ERROR_VALUE_NOT_VALID
        elif attrib == "receiveroom":
            my_room = Room.get_one(session, value)
            if isinstance(my_room, Room):
                return session.query(User).filter(User.receive_room == my_room).all()
            else:
                return User.ERROR_VALUE_NOT_VALID
        else:
            return User.ERROR_ATTRIB_NOT_VALID
    
    @staticmethod
    def add_one(session, new_element):
        element = User.get_one(session, new_element.name)
        if element == User.ERROR_ELEMENT_NOT_EXISTS:
            session.add(new_element)
            return new_element
        else:
            return User.ERROR_ELEMENT_ALREADY_EXISTS

    @staticmethod
    def add_all(session, new_elements):
        session.add_all(new_elements)
        
    @staticmethod
    def del_one(session, element):
        element = User.get_one(session, element.name)
        if isinstance(element):
            session.delete(element)
            return element
        else:
            return User.ERROR_ELEMENT_NOT_EXISTS
    
    @staticmethod
    def delete_all(session):
        session.query(User).delete()
        
    @staticmethod
    def edit_one(session, element, attrib, value):
        if attrib == "room":
            if value == "":
                element.room = None
            else:
                my_room = Room.get_one(session, value)
                if isinstance(my_room, Room):
                    element.room = my_room
                else:
                    return User.ERROR_VALUE_NOT_VALID
        elif attrib == "receive_room":
            if value == "":
                element.receive_room = None
            else:
                my_room = Room.get_one(session, value)
                if isinstance(my_room, Room):
                    element.receive_room = my_room
                else:
                    return User.ERROR_VALUE_NOT_VALID
        elif attrib == "admin":
            if value == "True":
                element.admin = True
            else:
                element.admin = False
        else:
            return Role.edit_one(element, attrib, value)
    
    @staticmethod
    def import_one(session, input, element=None, name=None):
        if element == None:
            element = User()
        tree = ElementTree.fromstring(input)
        if tree.tag == "user":
            element = Role.import_one(tree, element, name)
            room = tree.findtext("room")
            if room != None:
                element = User.edit_one(session, element, "room", room)
                if not isinstance(element, User):
                    return element
            receive_room = tree.findtext("receive_room")
            if receive_room != None:
                element = User.edit_one(session, element, "receive_room", receive_room)
                if not isinstance(element, User):
                    return element
            admin = tree.findtext("admin")
            if admin != None:
                User.edit_one(session, element, "admin", admin)
            return element
        else:
            return User.ERROR_TAG_NOT_VALID
            
    @staticmethod
    def import_all(session, input):
        elements = []
        tree = ElementTree.fromstring(input)
        if tree.tag == "users":
            for element in tree.findall("user"):
                new_element = User.import_one(session, ElementTree.tostring(element, "UTF-8"))
                if isinstance(new_element, User):
                    elements.append(new_element)
                else:
                    return new_element
            return elements
        else:
            return User.ERROR_TAG_NOT_VALID
