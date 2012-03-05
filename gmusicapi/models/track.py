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

class Track(object):
    @staticmethod
    def kind():
        return 'sj#track'

    def __init__(self):
        self._album = None
        self._albumArtRef = None
        self._albumArtist = None
        self._albumId = None
        self._artist = None
        self._beatsPerMinute = None
        self._comment = None
        self._composer = None
        self._creationTimestamp = None
        self._discNumber = None
        self._durationMillis = None
        self._estimatedSize = None
        self._genre = None
        self._deleted = None
        self._lastModifiedTimestamp = None
        self._playCount = None
        self._rating = None
        self._id = None
        self._storeId = None
        self._title = None
        self._totalDiscCount = None
        self._trackNumber = None
        self._trackType = None
        self._year = None

    @property
    def album(self):
        """The name of this track's album."""
        return self._album

    @album.setter
    def album(self, value):
        assert type(value) is str
        self._album = value



    @property
    def albumArtRef(self):
        return self._albumArtRef
    # No setter for albumArtRef (yet)



    @property
    def albumArtist(self):
        """The name of the artist of this track's album."""
        return self._albumArtist

    @albumArtist.setter
    def albumArtist(self, value):
        assert type(value) is str
        self._albumArtist = value



    @property
    def albumId(self):
        """The internal ID of this track's album in the store."""
        return self._albumId
    # No setter for albumId



    @property
    def artist(self):
        """The name of the artist of this track."""
        return self._artist

    @artist.setter
    def artist(self, value):
        assert type(value) is str
        self._artist = value



    @property
    def beatsPerMinute(self):
        """The beats per minute of this track."""
        return self._beatsPerMinute

    @beatsPerMinute.setter
    def beatsPerMinute(self, value):
        assert type(value) is int
        self._beatsPerMinute = value



    @property
    def comment(self):
        """A comment associated with this track."""
        return self._comment

    @comment.setter
    def comment(self, value):
        assert type(value) is str
        self._comment = value



    @property
    def composer(self):
        """The composer of this track."""
        return self._composer

    @composer.setter
    def composer(self, value):
        assert type(value) is str
        self._composer = value



    @property
    def creationTimestamp(self):
        """The timestamp of this track's creation on the server."""
        return self._creationTimestamp
    # No setter for creationTimestamp



    @property
    def discNumber(self):
        """The album disc number of this track."""
        return self._discNumber

    @discNumber.setter
    def discNumber(self, value):
        assert type(value) is int
        self._discNumber = value



    @property
    def durationMillis(self):
        """The duration of this track in milliseconds."""
        return self._durationMillis

    @durationMillis.setter
    def durationMillis(self, value):
        assert type(value) is int
        self._durationMillis = value



    @property
    def estimatedSize(self):
        """The estimated file size of this track."""
        return self._estimatedSize

    @estimatedSize.setter
    def estimatedSize(self, value):
        assert type(value) is int
        self._estimatedSize = value



    @property
    def genre(self):
        """The genre of this track."""
        return self._genre

    @genre.setter
    def genre(self, value):
        assert type(value) is str
        self._genre = value



    @property
    def deleted(self):
        """Whether this track has been deleted from the library."""
        return self._deleted
    # No setter for deleted



    @property
    def lastModifiedTimestamp(self):
        """The timestamp of the last modification to this track."""
        return self._lastModifiedTimestamp
    # No setter for lastModifiedTimestamp



    @property
    def playCount(self):
        """The number of times this track has been played."""
        return self._playCount
    # No setter for playCount, use the TrackStats calls



    @property
    def rating(self):
        """The rating of this track, as a string."""
        return self._rating

    @rating.setter
    def rating(self, value):
        assert type(value) is str or type(value) is int
        self._rating = str(value)



    @property
    def id(self):
        """The internal ID of this track."""
        return self._id
    # No setter for id



    @property
    def storeId(self):
        """The internal ID of this track in the store."""
        return self._storeId
    # No setter for storeId



    @property
    def title(self):
        """The title of this track."""
        return self._title

    @title.setter
    def title(self, value):
        assert type(value) is str
        self._title = value



    @property
    def totalDiscCount(self):
        """The total number of discs for this track's album."""
        return self._totalDiscCount

    @totalDiscCount.setter
    def totalDiscCount(self, value):
        assert type(value) is int
        self._totalDiscCount = value



    @property
    def trackNumber(self):
        """The track number of this track."""
        return self._trackNumber

    @trackNumber.setter
    def trackNumber(self, value):
        assert type(value) is int
        self._trackNumber = value



    @property
    def trackType(self):
        """The internal type of this track."""
        return self._trackType
    # No setter for trackType



    @property
    def year(self):
        """The year this track was released."""
        return self._year

    @year.setter
    def year(self, value):
        assert type(value) is int
        self._year = value



    def from_json(self, jsobj):
        if jsobj['kind']:
            assert jsobj['kind'] == Track.kind()

        for key, value in jsobj.iteritems():
            if key == 'kind':
                continue

            setattr(self, ('_%s' % key), value)



class TrackList(object):
    @staticmethod
    def kind():
        return 'sj#trackList'

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
            assert jsobj['kind'] == TrackList.kind()

        if 'nextPageToken' in jsobj:
            self._nextPageToken = jsobj['nextPageToken']

        if 'data' in jsobj:
            for track in jsobj['data']['items']:
                trk = Track()
                trk.from_json(track)
                self._items.append(trk)
