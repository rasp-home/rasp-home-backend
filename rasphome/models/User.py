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
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from rasphome.database import Base
import hashlib
import string
import random
from rasphome.models import Role

users_roles = Table('users_roles', Base.metadata,
    Column('users_id', Integer, ForeignKey('users.id')),
    Column('roles_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    name = Column(String(50), unique=True)
    password = Column(String(128))
    salt = Column(String(11))
    roles = relationship("Role",
                    secondary=users_roles,
                    backref="users")
    
    def __init__(self, name=None, password=None):
        self.name = name
        self.salt = User.generate_salt()
        self.password = User.get_password_salted(password, self.salt)
        
    def __repr__(self):
        return "<User %s>" % (self.name)
    
    def set_new_password(self, password):
        self.password = User.get_password_salted(password, self.salt)
    
    def check_auth(self, password):
        hash = hashlib.sha512((self.salt+password).encode())
        return hash.hexdigest() == self.password
    
    def has_role(self, role_name):
        for role in self.roles:
            if role.name == role_name:
                return True
        return False
    
    @staticmethod
    def get_password_salted(newPassword, salt):
        hash = hashlib.sha512((salt+newPassword).encode())
        return hash.hexdigest()
    
    @staticmethod
    def generate_salt():
        saltchars = string.ascii_letters + string.digits + './'
        salt = "$1$"
        salt += ''.join([ random.choice(saltchars) for x in range(8) ])
        return salt
        