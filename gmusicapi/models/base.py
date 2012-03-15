#!/usr/bin/env python

#Copyright 2012 Darryl Pogue

#This file is part of gmusicapi - the Unofficial Google Music API.

#Gmusicapi is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#Gmusicapi is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with gmusicapi.  If not, see <http://www.gnu.org/licenses/>.

class ModelBase(object):
    @staticmethod
    def kind():
        raise NotImplementedError

    def __init__(self, jsdata=None):
        self._dirtyProps = set()

        if jsdata:
            self.from_json(jsdata)

    def from_json(self, jsdata):
        if 'kind' in jsdata:
            if jsdata['kind'] != self.__class__.kind():
                raise ValueError("Incorrect kind of model")

    def mutation_update(self):
        raise NotImplementedError

    def mutation_delete(self):
        raise NotImplementedError
