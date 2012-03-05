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

class Playlist(object):
    @staticmethod
    def kind():
        return 'sj#playlist'

    def __init__(self):
        self._creationTimestamp = None
        self._deleted = None
        self._lastModifiedTimestamp = None
        self._name = None
        self._id = None
        self._type = None

    @property
    def creationTimestamp(self):
        """The timestamp of this playlist's creation on the server."""
        return self._creationTimestamp
    # No setter for creationTimestamp


    @property
    def deleted(self):
        """Whether this playlist has been deleted."""
        return self._deleted
    # No setter for deleted


    @property
    def lastModifiedTimestamp(self):
        """The timestamp of the last modification to this playlist."""
        return self._lastModifiedTimestamp
    # No setter for lastModifiedTimestamp


    @property
    def name(self):
        """The name of this playlist."""
        return self._name

    @name.setter
    def name(self, value):
        assert type(value) is str
        self._name = value


    @property
    def id(self):
        """The internal ID of this playlist."""
        return self._id
    # No setter for id


    @property
    def type(self):
        """The internal type of this playlist."""
        return self._type
    # No setter for type


    def from_json(self, jsobj):
        if jsobj['kind']:
            assert jsobj['kind'] == Playlist.kind()

        for key, value in jsobj.iteritems():
            if key == 'kind':
                continue

            setattr(self, ('_%s' % key), value)



class PlaylistList(object):
    @staticmethod
    def kind():
        return 'sj#playlistList'

    def __init__(self, jsdata=None):
        self._nextPageToken = None
        self._items = []

        if jsdata:
            self.from_json(jsdata)

    @property
    def nextPageToken(self):
        return self._nextPageToken

    @property
    def items(self):
        return self._items

    def from_json(self, jsobj):
        if jsobj['kind']:
            assert jsobj['kind'] == PlaylistList.kind()

        if 'nextPageToken' in jsobj:
            self._nextPageToken = jsobj['nextPageToken']

        if 'data' in jsobj:
            for plist in jsobj['data']['items']:
                playlist = Playlist()
                playlist.from_json(plist)
                self._items.append(playlist)
