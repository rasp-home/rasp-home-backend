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
from sqlalchemy.orm.exc import NoResultFound
from xml.etree import ElementTree
from rasphome.models.Role import Role

class Backend(Role):
    ERROR_ELEMENT_ALREADY_EXISTS = -3
    ERROR_ELEMENT_NOT_EXISTS = -4
    ERROR_TAG_NOT_VALID = -5
    
    __tablename__ = 'backend'
    id = Column(Integer, ForeignKey('role.id'), primary_key=True)
    master = Column(Boolean, default=False)
    
    __mapper_args__ = {
        'polymorphic_identity':'backend'
    }
    
    def __repr__(self):
        return "%d %s %s %s %s, %s, %s, %s, %d, %d %s" % (self.id, 
                              self.role, 
                              self.name, 
                              self.password, 
                              self.active, 
                              self.backend_name, 
                              self.backend_pass, 
                              self.ip, 
                              self.serverport, 
                              self.zeroconfport,
                              self.master)
    
    @staticmethod
    def export_one(element, attribs):
        tree = ElementTree.Element("backend")
        tree = Role.export_one(tree, element, attribs)
        if "master" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "master")
            if element.master != None:
                if element.master == True:
                    attrib.text = "True"
                else:
                    attrib.text = "False"
        return ElementTree.tostring(tree, "UTF-8")
    
    @staticmethod
    def export_all(elements, attribs):
        tree = ElementTree.Element("backends")
        for element in elements:
            tree.append(ElementTree.fromstring(Backend.export_one(element, attribs)))
        return ElementTree.tostring(tree, "UTF-8")

    @staticmethod
    def get_one(session, name):
        try:
            return session.query(Backend).filter(Backend.name == name).one()
        except NoResultFound:
            return Backend.ERROR_ELEMENT_NOT_EXISTS
        
    @staticmethod
    def get_all(session, attrib=None, value=None):
        if attrib == None:
            return session.query(Backend).all()
        elif attrib == "login":
            return session.query(Backend).filter(Backend.login == True).all()
        elif attrib == "master":
            if value == "True":
                return session.query(Backend).filter(Backend.master == True).all()
            else:
                return session.query(Backend).filter(Backend.master == False).all()
        else:
            return Backend.ERROR_ATTRIB_NOT_VALID
            
    @staticmethod
    def add_one(session, new_element):
        element = Backend.get_one(session, new_element.name)
        if element == Backend.ERROR_ELEMENT_NOT_EXISTS:
            session.add(new_element)
            return new_element
        else:
            return Backend.ERROR_ELEMENT_ALREADY_EXISTS

    @staticmethod
    def add_all(session, new_elements):
        session.add_all(new_elements)
    
    @staticmethod
    def del_one(session, element):
        element = Backend.get_one(session, element.name)
        if isinstance(element):
            session.delete(element)
            return element
        else:
            return Backend.ERROR_ELEMENT_NOT_EXISTS
    
    @staticmethod
    def delete_all(session):
        session.query(Backend).delete()
        
    @staticmethod
    def edit_one(session, element, attrib, value):
        if attrib == "master":
            if value == "True":
                element.master = True
            else:
                element.master = False
        else:
            return Role.edit_one(element, attrib, value)

    @staticmethod
    def import_one(session, input, element=None, name=None):
        if element == None:
            element = Backend()
        tree = ElementTree.fromstring(input)
        if tree.tag == "backend":
            element = Role.import_one(tree, element, name)
            master = tree.findtext("master")
            if master != None:
                Backend.edit_one(session, element, "master", master)
            return element
        else:
            return Backend.ERROR_TAG_NOT_VALID
                
    @staticmethod
    def import_all(session, input):
        elements = []
        tree = ElementTree.fromstring(input)
        if tree.tag == "backends":
            for element in tree.findall("backend"):
                new_element = Backend.import_one(session, ElementTree.tostring(element, "UTF-8"))
                if isinstance(new_element, Backend):
                    elements.append(new_element)
                else:
                    return new_element
            return elements
        else:
            return Backend.ERROR_TAG_NOT_VALID