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
from sqlalchemy.orm.exc import NoResultFound
from xml.etree import ElementTree
from rasphome.database import Base

class Room(Base):
    ERROR_ATTRIB_NOT_VALID = -1
    ERROR_ELEMENT_NOT_EXISTS = -2
    ERROR_ELEMENT_ALREADY_EXISTS = -3
    ERROR_TAG_NOT_VALID = -4
    
    __tablename__ = 'room'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    
    def __repr__(self):
        return "<Room %s>" % (self.name)

    @staticmethod
    def export_one(element, attribs):
        tree = ElementTree.Element("room")
        if "name" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "name")
            attrib.text = element.name
        return ElementTree.tostring(tree, "UTF-8")

    @staticmethod
    def export_all(elements, attribs):
        tree = ElementTree.Element("rooms")
        for element in elements:
            tree.append(ElementTree.fromstring(Room.export_one(element, attribs)))
        return ElementTree.tostring(tree, "UTF-8")
    
    @staticmethod
    def get_one(session, name):
        try:
            return session.query(Room).filter(Room.name == name).one()
        except NoResultFound:
            return Room.ERROR_ELEMENT_NOT_EXISTS
    
    @staticmethod
    def get_all(session):
        return session.query(Room).all()
    
    @staticmethod
    def add_one(session, new_element):
        element = Room.get_one(session, new_element.name)
        if element == Room.ERROR_ELEMENT_NOT_EXISTS:
            session.add(new_element)
            return new_element
        else:
            return Room.ERROR_ELEMENT_ALREADY_EXISTS
    
    @staticmethod
    def add_all(session, new_elements):
        session.add_all(new_elements)
    
    @staticmethod
    def del_one(session, element):
        element = Room.get_one(session, element.name)
        if isinstance(element):
            session.delete(element)
            return element
        else:
            return Room.ERROR_ELEMENT_NOT_EXISTS
        
    @staticmethod
    def delete_all(session):
        session.query(Room).delete()
    
    @staticmethod
    def edit_one(session, element, attrib, value):
        if attrib == "name":
            element.name = value
        else:
            return Room.ERROR_ATTRIB_NOT_VALID
        return element

    @staticmethod
    def import_one(session, input, element=None, name=None):
        if element == None:
            element = Room()
        tree = ElementTree.fromstring(input)
        if tree.tag == "room":
            if name == None:
                name = tree.findtext("name")
            if name != None:
                Room.edit_one(element, "name", name)
            return element
        else:
            return Room.ERROR_TAG_NOT_VALID
            
    @staticmethod
    def import_all(session, input):
        elements = []
        tree = ElementTree.fromstring(input)
        if tree.tag == "rooms":
            for element in tree.findall("room"):
                new_element = Room.import_one(session, ElementTree.tostring(element, "UTF-8"))
                if isinstance(new_element, Room):
                    elements.append(new_element)
                else:
                    return new_element
            return elements
        else:
            return Room.ERROR_TAG_NOT_VALID