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
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from xml.etree import ElementTree
from rasphome.models.Role import Role
from rasphome.models.Room import Room

class Node(Role):
    ERROR_VALUE_NOT_VALID = -2
    ERROR_ELEMENT_ALREADY_EXISTS = -3
    ERROR_ELEMENT_NOT_EXISTS = -4
    ERROR_TAG_NOT_VALID = -5
    
    __tablename__ = 'node'
    id = Column(Integer, ForeignKey('role.id'), primary_key=True)
    room_id = Column(Integer, ForeignKey('room.id'))
    room = relationship(Room, primaryjoin=room_id==Room.id, foreign_keys=[room_id])
    title = Column(String(50))
    type = Column(String(50))
    input = Column(String(50))
    output = Column(String(50))
    
    __mapper_args__ = {
        'polymorphic_identity':'node'
    }
    
    def __repr__(self):
        return "<Node %s>" % (self.name)
    
    @staticmethod
    def export_one(element, attribs):
        tree = ElementTree.Element("node")
        tree = Role.export_one(tree, element, attribs)
        if "room" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "room")
            if element.room != None:
                attrib.text = element.room.name
        if "title" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "title")
            attrib.text = element.title
        if "type" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "type")
            attrib.text = element.type
        if "input" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "input")
            attrib.text = element.input
        if "output" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "output")
            attrib.text = element.output
        return ElementTree.tostring(tree, "UTF-8")
    
    @staticmethod
    def export_all(elements, attribs):
        tree = ElementTree.Element("nodes")
        for element in elements:
            tree.append(ElementTree.fromstring(Node.export_one(element, attribs)))
        return ElementTree.tostring(tree, "UTF-8")
    
    @staticmethod
    def get_one(session, name):
        try:
            return session.query(Node).filter(Node.name == name).one()
        except NoResultFound:
            return Node.ERROR_ELEMENT_NOT_EXISTS
    
    @staticmethod
    def get_all(session, attrib=None, value=None):
        if attrib == None:
            return session.query(Node).all()
        elif attrib == "room":
            my_room = Room.get_one(session, value)
            if isinstance(my_room, Room):
                return session.query(Node).filter(Node.room == my_room).all()
            else:
                return Node.ERROR_VALUE_NOT_VALID
        else:
            return Node.ERROR_ATTRIB_NOT_VALID
    
    @staticmethod
    def add_one(session, new_element):
        element = Node.get_one(session, new_element.name)
        if element == Node.ERROR_ELEMENT_NOT_EXISTS:
            session.add(new_element)
            return new_element
        else:
            return Node.ERROR_ELEMENT_ALREADY_EXISTS

    @staticmethod
    def add_all(session, new_elements):
        session.add_all(new_elements)
        
    @staticmethod
    def del_one(session, element):
        element = Node.get_one(session, element.name)
        if isinstance(element):
            session.delete(element)
            return element
        else:
            return Node.ERROR_ELEMENT_NOT_EXISTS
    
    @staticmethod
    def delete_all(session):
        session.query(Node).delete()
        
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
                    return Node.ERROR_VALUE_NOT_VALID
        elif attrib == "title":
            element.title = value
        elif attrib == "tyoe":
            element.type = value
        elif attrib == "input":
            element.input = value
        elif attrib == "output":
            element.output = value
        else:
            return Role.edit_one(element, attrib, value)
    
    @staticmethod
    def import_one(session, input, element=None, name=None):
        if element == None:
            element = Node()
        tree = ElementTree.fromstring(input)
        if tree.tag == "node":
            element = Role.import_one(tree, element, name)
            room = tree.findtext("room")
            if room != None:
                element = Node.edit_one(session, element, "room", room)
                if not isinstance(element, Node):
                    return element
            title = tree.findtext("title")
            if title != None:
                Node.edit_one(session, element, "title", title)
            type = tree.findtext("type")
            if type != None:
                Node.edit_one(session, element, "type", type)
            input = tree.findtext("input")
            if input != None:
                Node.edit_one(session, element, "input", input)
            output = tree.findtext("output")
            if output != None:
                Node.edit_one(session, element, "output", output)
            return element
        else:
            return Node.ERROR_TAG_NOT_VALID
            
    @staticmethod
    def import_all(session, input):
        elements = []
        tree = ElementTree.fromstring(input)
        if tree.tag == "nodes":
            for element in tree.findall("node"):
                new_element = Node.import_one(session, ElementTree.tostring(element, "UTF-8"))
                if isinstance(new_element, Node):
                    elements.append(new_element)
                else:
                    return new_element
            return elements
        else:
            return Node.ERROR_TAG_NOT_VALID