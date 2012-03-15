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

from base import ModelBase

class Playlist(ModelBase):
    @staticmethod
    def kind():
        return 'sj#playlist'

    def __init__(self, jsdata=None):
        self._creationTimestamp = None
        self._deleted = None
        self._lastModifiedTimestamp = None
        self._name = None
        self._id = None
        self._type = None

        ModelBase.__init__(self, jsdata)

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
        if type(value) is not str: raise TypeError
        self._dirtyProps.add('name')
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
        ModelBase.from_json(self, jsobj)

        for key, value in jsobj.iteritems():
            if key == 'kind':
                continue

            setattr(self, ('_%s' % key), value)


    def mutation_update(self):
        mutate = {}
        mutate['id'] = self._id

        for prop in self._dirtyProps:
            mutate[prop] = getattr(self, ('_%s' % prop))

        self._dirtyProps.clear()

        return {'update': mutate}

    def mutation_delete(self):
        mutate = {}
        mutate['id'] = self._id

        return {'delete': mutate}



class PlaylistList(ModelBase):
    @staticmethod
    def kind():
        return 'sj#playlistList'

    def __init__(self, jsdata=None):
        self._nextPageToken = None
        self._items = []

        ModelBase.__init__(self, jsdata)

    @property
    def nextPageToken(self):
        return self._nextPageToken

    @property
    def items(self):
        return self._items

    def from_json(self, jsobj):
        ModelBase.from_json(self, jsobj)

        if 'nextPageToken' in jsobj:
            self._nextPageToken = jsobj['nextPageToken']

        if 'data' in jsobj:
            for plist in jsobj['data']['items']:
                playlist = Playlist()
                playlist.from_json(plist)
                self._items.append(playlist)



class PlaylistEntry(ModelBase):
    @staticmethod
    def kind():
        return 'sj#playlistEntry'

    def __init__(self, jsdata=None):
        self._absolutePosition = None
        self._clientId = None
        self._creationTimestamp = None
        self._followingEntryId = None
        self._deleted = None
        self._lastModifiedTimestamp = None
        self._precedingEntryId = None
        self._id = None
        self._playlistId = None
        self._trackId = None

        ModelBase.__init__(self, jsdata)


    @property
    def absolutePosition(self):
        return self._absolutePosition

    @absolutePosition.setter
    def absolutePosition(self, value):
        if type(value) is not str: raise TypeError
        self._dirtyProps.add('absolutePosition')
        self._absolutePosition = value


    @property
    def clientId(self):
        return self._clientId
    # No setter for clientId

    @property
    def creationTimestamp(self):
        return self._creationTimestamp
    # No setter for creationTimestamp


    @property
    def followingEntryId(self):
        return self._followingEntryId

    @followingEntryId.setter
    def followingEntryId(self, value):
        if type(value) is not str: raise TypeError
        self._dirtyProps.add('followingEntryId')
        self._followingEntryId = value


    @property
    def deleted(self):
        return self._deleted
    # No setter for deleted

    @property
    def lastModifiedTimestamp(self):
        return self._lastModifiedTimestamp
    # No setter for lastModifiedTimestamp


    @property
    def precedingEntryId(self):
        return self._precedingEntryId

    @precedingEntryId.setter
    def precedingEntryId(self, value):
        if type(value) is not str: raise TypeError
        self._dirtyProps.add('precedingEntryId')
        self._precedingEntryId = value


    @property
    def id(self):
        return self._id
    # No setter for id


    @property
    def playlistId(self):
        return self._playlistId

    @playlistId.setter
    def playlistId(self, value):
        if type(value) is not str: raise TypeError
        self._dirtyProps.add('playlistId')
        self._playlistId = value


    @property
    def trackId(self):
        return self._trackId

    @trackId.setter
    def trackId(self, value):
        if type(value) is not str: raise TypeError
        self._dirtyProps.add('trackId')
        self._trackId = value


    def from_json(self, jsobj):
        ModelBase.from_json(self, jsobj)

        for key, value in jsobj.iteritems():
            if key == 'kind':
                continue

            setattr(self, ('_%s' % key), value)


    def mutation_update(self):
        mutate = {}
        mutate['id'] = self._id

        for prop in self._dirtyProps:
            mutate[prop] = getattr(self, ('_%s' % prop))

        self._dirtyProps.clear()

        return {'update': mutate}

    def mutation_delete(self):
        mutate = {}
        mutate['id'] = self._id

        return {'delete': mutate}



class PlaylistEntryList(ModelBase):
    @staticmethod
    def kind():
        return 'sj#playlistEntryList'

    def __init__(self, jsdata=None):
        self._nextPageToken = None
        self._items = []

        ModelBase.__init__(self, jsdata)

    @property
    def nextPageToken(self):
        return self._nextPageToken

    @property
    def items(self):
        return self._items

    def from_json(self, jsobj):
        ModelBase.from_json(self, jsobj)

        if 'nextPageToken' in jsobj:
            self._nextPageToken = jsobj['nextPageToken']

        if 'data' in jsobj:
            for plist in jsobj['data']['items']:
                entry = PlaylistEntry()
                entry.from_json(plist)
                self._items.append(entry)
