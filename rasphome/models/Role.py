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

__all__ = ['Role']

from sqlalchemy import Column, Integer, String, Boolean
from rasphome.database import Base
from passlib.hash import sha512_crypt
from xml.etree import ElementTree

class Role(Base):
    ERROR_ATTRIB_NOT_VALID = -1
    
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    role = Column(String(50))
    name = Column(String(50), unique=True)
    password = Column(String(128))
    active = Column(Boolean, default=False)
    backend_name = Column(String(50))
    backend_pass = Column(String(50))
    ip = Column(String(50))
    serverport = Column(Integer)
    zeroconfport = Column(Integer)
    
    __mapper_args__ = {
        'polymorphic_identity':'role',
        'polymorphic_on':role
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
    
    def check_auth(self, password):
        return sha512_crypt.verify(password, self.password)
    
    @staticmethod
    def get_hashed_password(password):
        return sha512_crypt.encrypt(password)
    
    @staticmethod
    def export_one(tree, element, attribs):
        if "id" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "id")
            attrib.text = str(element.id)
        if "name" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "name")
            attrib.text = element.name
        if "password" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "password")
            attrib.text = element.password
        if "active" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "active")
            if element.active != None:
                if element.active == True:
                    attrib.text = "True"
                else:
                    attrib.text = "False"
        if "backend_name" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "backend_name")
            attrib.text = element.backend_name
        if "backend_pass" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "backend_pass")
            attrib.text = element.backend_pass
        if "ip" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "ip")
            attrib.text = element.ip
        if "serverport" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "serverport")
            if element.serverport != None:
                attrib.text = str(element.serverport)
        if "zeroconfport" in attribs or attribs == "all":
            attrib = ElementTree.SubElement(tree, "zeroconfport")
            if element.zeroconfport != None:
                attrib.text = str(element.zeroconfport)
        return tree
    
    @staticmethod
    def edit_one(element, attrib, value):
        if attrib == "id":
            element.id = value
        elif attrib == "name":
            element.name = value
        elif attrib == "password":
            if sha512_crypt.identify(value) == True:
                element.password = value
            else:
                element.password = Role.get_hashed_password(value)
        elif attrib == "active":
            if value == "True":
                element.active = True
            else:
                element.active = False
        elif attrib == "backend_name":
            element.backend_name = value
        elif attrib == "backend_pass":
            element.backend_pass = value
        elif attrib == "ip":
            element.ip = value
        elif attrib == "serverport":
            element.serverport = value
        elif attrib == "zeroconfport":
            element.zeroconfport = value
        else:
            return Role.ERROR_ATTRIB_NOT_VALID
        return element

    @staticmethod
    def import_one(tree, element, name=None):
        id = tree.findtext("id")
        if id != None:
            Role.edit_one(element, "id", id)
        if name == None:
            name = tree.findtext("name")
        if name != None:
            Role.edit_one(element, "name", name)
        password = tree.findtext("password")
        if password != None:
            Role.edit_one(element, "password", password)
        active = tree.findtext("active")
        if active != None:
            Role.edit_one(element, "active", active)
        backend_name = tree.findtext("backend_name")
        if backend_name != None:
            Role.edit_one(element, "backend_name", backend_name)
        backend_pass = tree.findtext("backend_pass")
        if backend_pass != None:
            Role.edit_one(element, "backend_pass", backend_pass)
        ip = tree.findtext("ip")
        if ip != None:
            Role.edit_one(element, "ip", ip)
        serverport = tree.findtext("serverport")
        if serverport != None:
            Role.edit_one(element, "serverport", serverport)
        zeroconfport = tree.findtext("zeroconfport")
        if zeroconfport != None:
            Role.edit_one(element, "zeroconfport", zeroconfport)
        return element
