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

class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    type = Column(String(50))
    name = Column(String(50), unique=True)
    password = Column(String(128))
    login = Column(Boolean, default=False)
    backend_pass = Column(String(50))
    
    __mapper_args__ = {
        'polymorphic_identity':'role',
        'polymorphic_on':type
    }
    
    def __init__(self, name, password):
        self.name = name
        self.password = self.get_hash_password(password)
        
    def __repr__(self):
        return "<Role %s>" % self.name
    
    def check_auth(self, password):
        return sha512_crypt.verify(password, self.password)
    
    def get_hash_password(self, password):
        return sha512_crypt.encrypt(password)
    
    @staticmethod
    def edit_one(session, my_role, attrib, value):
        if attrib == "name":
            my_role.name = value
            return my_role
        if attrib == "password":
            my_role.password = Role.get_hash_password(value)
            return my_role
        if attrib == "login":
            my_role.login = value
            return my_role
        if attrib == "backend_pass":
            my_role.backend_pass = value
            return my_role
        else:
            return -1
