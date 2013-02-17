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
# You should have received a copy of the GNU Lesser General Publ     ic License
# along with rasp-home-backend.  If not, see <http://www.gnu.org/licenses/>.

import configparser


config = configparser.ConfigParser()
config.read(["/etc/rasp-home-backend/rasp-home-backend.conf", "rasp-home-backend.conf"])

class ConfigSection(object):

    def __init__(self, config, sectionName):
        self.config = config
        self.sectionName = sectionName

    def bool(self, string):
        if string in ["False", "false", "f", "F", "0"]:
            return False
        else:
            return True

    def __getOption(self, option, defaultValue):
        if self.config.has_option(self.sectionName, option):
            return self.config.get(self.sectionName, option)
        else:
            return defaultValue

    def __setOption(self, optionName, option):
        self.__class__.__setattr__(self, optionName, option)
        return self.__class__.__getattribute__(self, optionName)

    def addOption(self, option, defaultValue):
        return self.__setOption(option, self.__getOption(option, defaultValue))

    def addBoolOption(self, option, defaultValue):
        return self.__setOption(option, self.bool(self.__getOption(option, defaultValue)))

    def addIntOption(self, option, defaultValue):
        return self.__setOption(option, int(self.__getOption(option, defaultValue)))


rasp_settings = ConfigSection(config, "rasp-home")
rasp_settings.addIntOption("http_port", 8090)
rasp_settings.addIntOption("https_port", 8091)

