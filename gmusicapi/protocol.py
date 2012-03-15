#!/usr/bin/env python

#Copyright 2012 Simon Weber.

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

"""The protocol layer is a one-to-one mapping of calls to Google Music."""


import string
import os
import random
from collections import namedtuple
import exceptions
from uuid import getnode as getmac
from socket import gethostname
import base64
import hashlib
import json

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

import metadata_pb2
from utils import utils
from utils.apilogging import LogController #TODO this is a hack
from models.track import Track, TrackList
from models.playlist import Playlist, PlaylistList, PlaylistEntry, PlaylistEntryList


supported_filetypes = ("mp3")

class UnsupportedFiletype(exceptions.Exception):
    pass

class WC_Call:
    """An abstract class to hold the protocol for a web client call."""
    
    _base_url = 'https://music.google.com/music/'
    
    #Added to the url after _base_url. Most calls are made to /music/services/<call name>
    #Expected to end with a forward slash.
    _suburl = 'services/'

    #Should the response to this call be logged?
    #The request is always logged, currently.
    gets_logged = True

    #Do we need to be logged in before making the call?
    requires_login = True
    
    #Most calls will send u=0 and the xt cookie in the querystring.
    @classmethod
    def build_url(cls, query_string=None):
        """Return the url to make the call at."""

        #Most calls send u=0 and xt=<cookie value>
        qstring = '?u=0&xt={0}'.format(query_string['xt'])

        return cls._base_url + cls._suburl + cls.__name__ + qstring

    #Calls all have different request and response formats.
    @staticmethod
    def build_transaction():
        """Return a tuple of (filled request, response schemas)."""
        raise NotImplementedError

class _DefinesNameMetaclass(type):
    """A metaclass to create a 'name' attribute for _Metadata that respects
    any necessary name mangling."""

    def __new__(cls, name, bases, dct):
        dct['name'] = name.split('gm_')[-1]
        return super(_DefinesNameMetaclass, cls).__new__(cls, name, bases, dct)

class _Metadata_Expectation():
    """An abstract class to hold expectations for a particular metadata entry.

    Its default values are correct for most entries."""

    __metaclass__ = _DefinesNameMetaclass

    #Most keys have the same expectations.
    #In most cases, overriding val_type is all that is needed.

    #The validictory type we expect to see.
    #Possible values are:
        # "string" - str and unicode objects
        # "integer" - ints
        # "number" - ints and floats
        # "boolean" - bools
        # "object" - dicts
        # "array" - lists and tuples
        # "null" - None
        # "any" - any type is acceptable
    val_type = "string"

    #Can we change the value?
    mutable = True

    #A list of allowed values, or None for no restriction.
    allowed_values = None
    
    #Can the value change without us changing it?
    volatile = False

    #The name of the Metadata class our value depends on, or None.
    depends_on = None 

    #A function that takes the dependent key's value
    # and returns our own. Only implemented for dependent keys.
    @staticmethod
    def dependent_transformation(value):
        raise NotImplementedError

    #Is this entry optional?
    optional = False

    @classmethod
    def get_schema(cls):
        """Return the schema to validate this class with."""
        schema = {}
        schema["type"] = cls.val_type
        if cls.val_type == "string":
            schema["blank"] = True #Allow blank strings.
        if cls.optional:
            schema["required"] = False

        return schema
    

class Metadata_Expectations:
    """Holds expectations about metadata."""

    #Class names are GM response keys.
    #Clashes are prefixed with a gm_ (eg gm_type).

    @classmethod
    def get_expectation(cls, key):
        """Get the Expectation associated with the given key name.
        Return None if there is no Expectation for that name."""

        expt = None

        try:
            expt = getattr(cls, key)
        except AttributeError:
            expt = getattr(cls, "gm_"+key)
        
        try:
            if issubclass(expt, _Metadata_Expectation):
                return expt
        except TypeError:
            return None

    @classmethod
    def get_all_expectations(cls):
        """Return a dictionary mapping key name to Expectation for all known keys."""

        expts = {}

        for name in dir(cls):
            member = cls.get_expectation(name)
            if member: expts[member.name]=member
        
        return expts

    #Mutable metadata:
    class rating(_Metadata_Expectation):
        val_type = "integer"
        #0 = no thumb
        #1 = down thumb
        #5 = up thumb
        allowed_values = (0, 1, 5) 

    #strings (the default value for val_type
    class composer(_Metadata_Expectation):
        pass
    class album(_Metadata_Expectation):
        pass
    class albumArtist(_Metadata_Expectation):
        pass
    class genre(_Metadata_Expectation):
        pass
    class name(_Metadata_Expectation):
        pass
    class artist(_Metadata_Expectation):
        pass

    #integers
    class disc(_Metadata_Expectation):
        optional = True
        val_type = "integer"
    class year(_Metadata_Expectation):
        optional = True
        val_type = "integer"
    class track(_Metadata_Expectation):
        optional = True
        val_type = "integer"
    class totalTracks(_Metadata_Expectation):
        optional = True
        val_type = "integer"
    class playCount(_Metadata_Expectation):
        val_type = "integer"
    class totalDiscs(_Metadata_Expectation):
        optional = True
        val_type = "integer"



    #Immutable metadata:
    class durationMillis(_Metadata_Expectation):
        mutable = False #you can change this, but probably don't want to.
        val_type = "integer"
    class comment(_Metadata_Expectation):
        mutable = False
    class id(_Metadata_Expectation):
        mutable = False
    class deleted(_Metadata_Expectation):
        mutable = False
        val_type = "boolean"
    class creationDate(_Metadata_Expectation):
        mutable = False
        val_type = "integer"
    class albumArtUrl(_Metadata_Expectation):
        mutable = False
        optional = True #only seen when there is album art.
    class gm_type(_Metadata_Expectation):
        mutable = False
        val_type = "integer"
    class beatsPerMinute(_Metadata_Expectation):
        mutable = False
        val_type = "integer"
    class url(_Metadata_Expectation):
        mutable = False
    class playlistEntryId(_Metadata_Expectation):
        mutable = False
        optional = True #only seen when songs are in the context of a playlist.
        
    
    #Dependent metadata:
    class title(_Metadata_Expectation):
        depends_on = "name"
        
        @staticmethod
        def dependent_transformation(other_value):
            return other_value #nothing changes

    class titleNorm(_Metadata_Expectation):
        depends_on = "name"

        @staticmethod
        def dependent_transformation(other_value):
            return string.lower(other_value)

    class albumArtistNorm(_Metadata_Expectation):
        depends_on = "albumArtist"

        @staticmethod
        def dependent_transformation(other_value):
            return string.lower(other_value)

    class albumNorm(_Metadata_Expectation):
        depends_on = "album"

        @staticmethod
        def dependent_transformation(other_value):
            return string.lower(other_value)    

    class artistNorm(_Metadata_Expectation):
        depends_on = "artist"

        @staticmethod
        def dependent_transformation(other_value):
            return string.lower(other_value)

    
    #Metadata we have no control over:
    class lastPlayed(_Metadata_Expectation):
        mutable = False
        volatile = True
        val_type = "integer"

    
class WC_Protocol:
    """Holds the protocol for all suppported web client interactions."""

    #Shared response schemas.
    song_schema = {"type": "object",

                   #filled out next
                   "properties":{},

                   #don't allow metadata not in expectations
                   "additionalProperties":False} 

    for name, expt in Metadata_Expectations.get_all_expectations().items():
        song_schema["properties"][name] = expt.get_schema()

    song_array = {"type":"array",
                  "items": song_schema}        

    #All api calls are named as they appear in the request.

    class addplaylist(WC_Call):
        """Creates a new playlist."""

        @staticmethod
        def build_transaction(title): 
            """
            :param title: the title of the playlist to create.
            """
            
            req = {"title": title}

            #{"id":"<new playlist id>","title":"<name>","success":true}
            res = {"type": "object",
                      "properties":{
                        "id": {"type":"string"},
                        "title": {"type": "string"},
                        "success": {"type": "boolean"}
                        }
                   }
                     

            return (req, res)


    class addtoplaylist(WC_Call):
        """Adds songs to a playlist."""

        @staticmethod
        def build_transaction(playlist_id, song_ids):
            """
            :param playlist_id: id of the playlist to add to.
            :param song_ids: a list of song ids
            """

            req = {"playlistId": playlist_id, "songIds": song_ids} 
                                      
            #{"playlistId":"<same as above>","songIds":[{"playlistEntryId":"<new id>","songId":"<same as above>"}]}
            res = {"type": "object",
                      "properties":{
                        "playlistId": {"type":"string"},
                        "songIds":{
                            "type":"array",
                            "items":{
                                "type":"object",
                                "properties":{
                                    "songId":{"type":"string"},
                                    "playlistEntryId":{"type":"string"}
                                    }
                                }
                            }
                        }
                   }
                    
            return (req, res)


    class modifyplaylist(WC_Call):
        """Changes the name of a playlist."""

        @staticmethod
        def build_transaction(playlist_id, new_name):
            """
            :param playlist_id: id of the playlist to rename.
            :param new_title: desired title.
            """
        
            req = {"playlistId": playlist_id, "playlistName": new_name}

            #{}
            res = {"type": "object",
                   "properties":{},
                   "additionalProperties": False}

            return (req, res)

    
    class deleteplaylist(WC_Call):
        """Deletes a playlist."""

        @staticmethod
        def build_transaction(playlist_id):
            """
            :param playlist_id: id of the playlist to delete.
            """
            
            req = {"id": playlist_id}

            #{"deleteId": "<id>"}
            res = {"type": "object",
                     "properties":{
                       "deleteId": {"type":"string"}
                       }}
                     
            return (req, res)
        

    class deletesong(WC_Call):
        """Delete a song from the library or a playlist."""

        @staticmethod
        def build_transaction(song_ids, entry_ids = [""], playlist_id = "all"):
            """
            :param song_ids: a list of song ids
            :param entry_ids: for deleting from playlists
            :param list_id: for deleteing from playlists
            """
            req = {"songIds": song_ids, "entryIds":entry_ids, "listId": playlist_id}

            #{"listId":"<playlistId>","deleteIds":["<id1>"]}
            #playlistId might be "all" - meaning deletion from the library
            res = {"type": "object",
                     "properties":{
                       "listId": {"type":"string"},
                       "deleteIds":
                           {"type": "array",
                            "items": {"type": "string"}
                            }
                       }
                   }
            return (req, res)

    class loadalltracks(WC_Call):
        """Loads tracks from the library.
        Since libraries can have many tracks, GM gives them back in chunks.
        Chunks will send a continuation token to get the next chunk.
        The first request needs no continuation token.
        The last response will not send a token.
        """

        gets_logged = False

        @staticmethod
        def build_transaction(cont_token = None):
            """:param cont_token: (optional) token to get the next library chunk."""
            if not cont_token:
                req = {}
            else:
                req = {"continuationToken": cont_token}


            res = {"type": "object",
                   "properties":{
                      "continuation": {"type":"boolean"},
                      "differentialUpdate": {"type":"boolean"},
                      "playlistId": {"type": "string"},
                      "requestTime": {"type": "integer"},
                      "playlist": WC_Protocol.song_array
                      },
                   "additionalProperties":{
                       "continuationToken": {"type":"string"}}
                   }

            return (req, res)

    class loadplaylist(WC_Call):
        """Loads tracks from a playlist.
        Tracks include an entryId.
        """

        gets_logged = False

        @staticmethod
        def build_transaction(playlist_id):
            req = {"id": playlist_id}

            res = {"type": "object",
                   "properties":{
                       "continuation":{"type":"boolean"},
                       "playlist":WC_Protocol.song_array,
                       "playlistId":{"type":"string"},
                       "unavailableTrackCount": {"type": "integer"}
                       }
                   }
                           
            return (req, res)
        
    
    class modifyentries(WC_Call):
        """Edit the metadata of songs."""

        @classmethod
        def build_transaction(cls, songs):
            """:param songs: a list of dictionary representations of songs."""
        
            #Warn about metadata changes that may cause problems.
            #If you change the interface in api, you can warn about changing bad categories, too.
            #Something like safelychange(song, entries) where entries are only those you want to change.

            for song in songs:
                for key in song:
                    allowed_values = Metadata_Expectations.get_expectation(key).allowed_values
                    if allowed_values and song[key] not in allowed_values:
                        LogController.get_logger("modifyentries").warning("setting key {0} to unallowed value {1} for id {2}. Check metadata expectations in protocol.py".format(key, song[key], song["id"]))
                        

            req = {"entries": songs}

            res = {"type": "object",
                   "properties":{
                       "success": {"type":"boolean"},
                       "songs":WC_Protocol.song_array
                       }
                   }
            return (req, res)

    class multidownload(WC_Call):
        """Get download links and counts for songs."""

        @staticmethod
        def build_transaction(song_ids):
            """:param song_ids: a list of song ids."""
            req = {"songIds": song_ids}

            #This hasn't been tested yet.
            res = {"type":"object",
                   "properties":{
                       "downloadCounts":{
                           "type":"array",
                           "items":{
                               "type":"object",
                               "properties":{
                                   "id":{"type":"integer"}
                                   }
                               }
                           },
                       "url":{"type":"string"}
                       }
                   }
            return (req, res)

    class play(WC_Call):
        """Get a url that holds a file to stream."""

        #play is strange, it doesn't use music/services/play, just music/play
        _suburl = ''

        @classmethod
        def build_url(cls, query_string):
            #xt is not sent for play.
            #Instead, the songid is sent in the querystring, along with pt=e, for unknown reasons.
            qstring = '?u=0&pt=e'
            return cls._base_url + cls._suburl + cls.__name__ + qstring

        @staticmethod
        def build_transaction():
            req = None #body is completely empty.
            res = {"type":"object",
                   "properties":{
                       "url":{"type":"string"}
                       }
                   }
            res = None
            return (req, res)
        

    class search(WC_Call):
        """Search for songs, artists and albums.
        GM ignores punctuation."""
    
        @staticmethod
        def build_transaction(query):
            req = {"q": query}

            res = {"type":"object",
                   "properties":{
                       "results":{
                           "type":"object",
                           "properties":{
                               "artists": WC_Protocol.song_array,
                               "albums": WC_Protocol.song_array,
                               "songs": WC_Protocol.song_array
                               }
                           }
                       }
                   }
                                  
                    
            return (req, res)


class MM_Protocol():

    def __init__(self):

        #Mac and hostname are used to identify our client.
        self.mac = hex(getmac())[2:-1]
        self.mac = ':'.join([self.mac[x:x+2] for x in range(0, 10, 2)])

        hostname = gethostname()

        #Pre-filled protobuff instances.
        #These are used to fill in new instances.
        #Named scheme is '[protocol name]_filled'

        self.upload_auth_filled = metadata_pb2.UploadAuth()
        self.upload_auth_filled.address = self.mac
        self.upload_auth_filled.hostname = hostname

        self.client_state_filled = metadata_pb2.ClientState()
        self.client_state_filled.address = self.mac

        self.upload_auth_response_filled = metadata_pb2.UploadAuthResponse()

        self.client_state_response_filled = metadata_pb2.ClientStateResponse()

        self.metadata_request_filled = metadata_pb2.MetadataRequest()
        self.metadata_request_filled.address = self.mac

        self.metadata_response_filled = metadata_pb2.MetadataResponse()
        
        #Service name mapped to url.
        self.pb_services = {
            "upload_auth" : 'upauth',
            "client_state": 'clientstate',
            "metadata": 'metadata?version=1'}

    
    def make_pb(self, pb_name):
        """Makes a new instance of a protobuff protocol.
        Client identifying fields are pre-filled.
        
        :pb_name: the name of the protocol
        """
        
        #eg: for "upload_auth", pb gets metadata_pb2.UploadAuth()
        pb = getattr(metadata_pb2,
                     utils.to_camel_case(pb_name))()

        #copy prefilled fields
        pb.CopyFrom(getattr(self, pb_name + "_filled"))

        return pb


    def make_metadata_request(self, filenames):
        """Returns (Metadata protobuff, dictionary mapping ClientId to filename) for the given filenames."""

        filemap = {} #this maps a generated ClientID with a filename

        metadata = self.make_pb("metadata_request")

        for filename in filenames:

            #Only mp3 supported right now.
            if not filename.split(".")[-1] in supported_filetypes:
                raise UnsupportedFiletype("only these filetypes are supported for uploading: " + str(supported_filetypes))


            track = metadata.tracks.add()

            #Eventually pull this to supported_filetypes
            audio = MP3(filename, ID3 = EasyID3)


            #The id is a 22 char hash of the file. It is found by:
            # stripping tags
            # getting an md5 sum
            # converting sum to base64
            # removing trailing ===

            #My implementation is _not_ the same hash the music manager will send;
            # they strip tags first. But files are differentiated across accounts,
            # so this shouldn't cause problems.

            #This will reupload files if their tags change.
            
            #It looks like we can turn on/off rematching of tracks (in session request);
            # might be better to comply and then give the option.
            
            with open(filename) as f:
                file_contents = f.read()
            
            h = hashlib.md5(file_contents).digest()
            h = base64.encodestring(h)[:-3]
            id = h

            filemap[id] = filename
            track.id = id

            filesize = os.path.getsize(filename)

            track.fileSize = filesize

            track.bitrate = audio.info.bitrate / 1000
            track.duration = int(audio.info.length * 1000)

            #GM requires at least a title.
            track.title = audio["title"][0] if "title" in audio else filename.split(r'/')[-1]

            if "album" in audio: track.album = audio["album"][0]
            if "artist" in audio: track.artist = audio["artist"][0]
            if "composer" in audio: track.composer = audio["composer"][0]

            #albumartist is 'performer' according to this guy: 
            # https://github.com/plexinc-plugins/Scanners.bundle/commit/95cc0b9eeb7fa8fa77c36ffcf0ec51644a927700

            if "performer" in audio: track.albumArtist = audio["performer"][0]
            if "genre" in audio: track.genre = audio["genre"][0]
            if "date" in audio: track.year = int(audio["date"][0].split("-")[0]) #this looks like an assumption
            if "bpm" in audio: track.beatsPerMinute = int(audio["bpm"][0])

            #think these are assumptions:
            if "tracknumber" in audio: 
                tracknumber = audio["tracknumber"][0].split("/")
                track.track = int(tracknumber[0])
                if len(tracknumber) == 2:
                    track.totalTracks = int(tracknumber[1])

            if "discnumber" in audio:
                discnumber = audio["discnumber"][0].split("/")
                track.disc = int(discnumber[0])
                if len(discnumber) == 2:
                    track.totalDiscs = int(discnumber[1])

        return (metadata, filemap)


    def make_upload_session_requests(self, filemap, server_response):
        """Returns a list of (filename, serverid, json) to request upload sessions.
        If no sessions are created, returns an empty list.
        
        :param filemap: maps ClientID to filename
        :param server_response: the MetadataResponse that preceded these requests
        """

        sessions = []

        for upload in server_response.response.uploads:
            filename = filemap[upload.id]
            audio = MP3(filename, ID3 = EasyID3)
            upload_title = audio["title"] if "title" in audio else filename.split(r'/')[-1]

            inlined = {
                "title": "jumper-uploader-title-42",
                "ClientId": upload.id,
                "ClientTotalSongCount": len(server_response.response.uploads),
                "CurrentTotalUploadedCount": "0",
                "CurrentUploadingTrack": upload_title,
                "ServerId": upload.serverId,
                "SyncNow": "true",
                "TrackBitRate": audio.info.bitrate,
                "TrackDoNotRematch": "false",
                "UploaderId": self.mac
            }
            payload = {
              "clientId": "Jumper Uploader",
              "createSessionRequest": {
                "fields": [
                    {
                        "external": {
                      "filename": os.path.basename(filename),
                      "name": os.path.abspath(filename),
                      "put": {},
                      "size": os.path.getsize(filename)
                    }
                    }
                ]
              },
              "protocolVersion": "0.8"
            }
            for key in inlined:
                payload['createSessionRequest']['fields'].append({
                    "inlined": {
                        "content": str(inlined[key]),
                        "name": key
                    }
                })

            sessions.append((filename, upload.serverId, payload))

        return sessions


class SJ_Protocol:
    class MusicURL:
        BASE_URL = 'https://www.googleapis.com/sj/v1beta1/'

        @staticmethod
        def tracks(trackid=None):
            url = SJ_Protocol.MusicURL.BASE_URL+'tracks'
            if trackid:
                url += '/%s' % trackid
            return url

        @staticmethod
        def track_audio(trackid, bitrate=256):
            return 'https://music.google.com/music/play?songid=%s&targetkbps=%d&pt=e' % (trackid, bitrate)

        @staticmethod
        def playlists(plid=None):
            url = SJ_Protocol.MusicURL.BASE_URL+'playlists'
            if plid:
                url += '/%s' % plid
            return url

        @staticmethod
        def playlist_entries(plid):
            return SJ_Protocol.MusicURL.BASE_URL+'plentries?plid=%s' % plid

        @staticmethod
        def playlist_entry(pleid):
            return SJ_Protocol.MusicURL.BASE_URL+'plentries/%s' % pleid

        @staticmethod
        def playlist_batch():
            return SJ_Protocol.MusicURL.BASE_URL+'playlistbatch'

        @staticmethod
        def plentries_batch():
            return SJ_Protocol.MusicURL.BASE_URL+'plentriesbatch'

    def __init__(self):
        pass

    def _handle_mutate_response(self, jsobj):
        if not 'mutate_response' in jsobj:
            return True

        ids = []

        mutations = jsobj['mutate_response']
        for mutation in mutations:
            if mutation['response_code'] != 'OK':
                raise ValueError
            if 'id' in mutation:
                ids.append(mutation['id'])

        return ids

    def _kind_to_model(self, kind):
        if kind == Track.kind():
            return Track
        elif kind == TrackList.kind():
            return TrackList
        elif kind == Playlist.kind():
            return Playlist
        elif kind == PlaylistList.kind():
            return PlaylistList
        elif kind == PlaylistEntry.kind():
            return PlaylistEntry
        elif kind == PlaylistEntryList.kind():
            return PlaylistEntryList
        else:
            raise ValueError

    def tracks(self, response):
        jsdata = json.loads(response)

        tl = self._kind_to_model(jsdata['kind'])(jsdata)
        if type(tl) is TrackList:
            return tl.items
        elif type(tl) is Track:
            return tl

    def playlists(self, response):
        jsdata = json.loads(response)

        pl = self._kind_to_model(jsdata['kind'])(jsdata)

        if type(pl) is PlaylistList:
            return pl.items
        elif type(pl) is Playlist:
            return pl

    def playlist_entries(self, response):
        jsdata = json.loads(response)

        el = self._kind_to_model(jsdata['kind'])(jsdata)

        if type(el) is PlaylistEntryList:
            return el.items
        elif type(el) is PlaylistEntry:
            return el

    def playlist_entry(self, response):
        return self.playlist_entries(response)

    def playlist_batch(self, response):
        jsdata = json.loads(response)

        return self._handle_mutate_response(jsdata)

    def plentries_batch(self, response):
        jsdata = json.loads(response)

        return self._handle_mutate_response(jsdata)
