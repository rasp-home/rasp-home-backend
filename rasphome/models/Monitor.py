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

__all__ = ['Monitor']

from sqlalchemy import  Column, Integer, ForeignKey
from sqlalchemy.orm.exc import NoResultFound
from xml.etree import ElementTree
from rasphome.models.Role import Role

class Monitor(Role):    
    ERROR_ELEMENT_ALREADY_EXISTS = -3
    ERROR_ELEMENT_NOT_EXISTS = -4
    ERROR_TAG_NOT_VALID = -5
    
    __tablename__ = 'monitor'
    id = Column(Integer, ForeignKey('role.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity':'monitor'
    }
    
    def __repr__(self):
        return "%d %s %s %s %s, %s, %s, %s, %d, %d" % (self.id, 
                              self.role, 
                              self.name, 
                              self.password, 
                              self.active, 
                              self.backend_name, 
                              self.backend_pass, 
                              self.ip, 
                              self.serverport, 
                              self.zeroconfport)

    @staticmethod
    def export_one(element, attribs):
        tree = ElementTree.Element("monitor")
        tree = Role.export_one(tree, element, attribs)
        return ElementTree.tostring(tree, "UTF-8")
    
    @staticmethod
    def export_all(elements, attribs):
        tree = ElementTree.Element("monitors")
        for element in elements:
            tree.append(ElementTree.fromstring(Monitor.export_one(element, attribs)))
        return ElementTree.tostring(tree, "UTF-8")
    
    @staticmethod
    def get_one(session, name):
        try:
            return session.query(Monitor).filter(Monitor.name == name).one()
        except NoResultFound:
            return Monitor.ERROR_ELEMENT_NOT_EXISTS
    
    @staticmethod
    def get_all(session, attrib=None, value=None):
        if attrib == None:
            return session.query(Monitor).all()
        elif attrib == "login":
            return session.query(Monitor).filter(Monitor.login == True).all()
    
    @staticmethod
    def add_one(session, new_element):
        element = Monitor.get_one(session, new_element.name)
        if element == Monitor.ERROR_ELEMENT_NOT_EXISTS:
            session.add(new_element)
            return new_element
        else:
            return Monitor.ERROR_ELEMENT_ALREADY_EXISTS

    @staticmethod
    def add_all(session, new_elements):
        session.add_all(new_elements)
        
    @staticmethod
    def del_one(session, element):
        element = Monitor.get_one(session, element.name)
        if isinstance(element):
            session.delete(element)
            return element
        else:
            return Monitor.ERROR_ELEMENT_NOT_EXISTS
    
    @staticmethod
    def delete_all(session):
        session.query(Monitor).delete()
        
    @staticmethod
    def edit_one(session, element, attrib, value):
        return Role.edit_one(element, attrib, value)
    
    @staticmethod
    def import_one(session, input, element=None, name=None):
        if element == None:
            element = Monitor()
        tree = ElementTree.fromstring(input)
        if tree.tag == "monitor":
            element = Role.import_one(tree, element, name)
            return element
        else:
            return Monitor.ERROR_TAG_NOT_VALID
            
    @staticmethod
    def import_all(session, input):
        elements = []
        tree = ElementTree.fromstring(input)
        if tree.tag == "monitors":
            for element in tree.findall("monitor"):
                new_element = Monitor.import_one(session, ElementTree.tostring(element, "UTF-8"))
                if isinstance(new_element, Monitor):
                    elements.append(new_element)
                else:
                    return new_element
            return elements
        else:
            return Monitor.ERROR_TAG_NOT_VALID
