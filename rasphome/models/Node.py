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

class Node(Role):
    __tablename__ = 'node'
    id = Column(Integer, ForeignKey('role.id'), primary_key=True)
    room_id = Column(Integer, ForeignKey('room.id'))
    title = Column(String(50))
    type = Column(String(50))
    value = Column(String(50))
    
    __mapper_args__ = {
        'polymorphic_identity':'node'
    }
    
    def __init__(self, name, password):
        super().__init__(name, password)
    
    def __repr__(self):
        return "<Node %s>" % (self.name)