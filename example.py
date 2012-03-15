#!/user/bin/env python

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


from gmusicapi.api import Api
from getpass import getpass

def init():
    """Makes an instance of the api and attempts to login with it.
    Returns the authenticated api.
    """

    api = Api()
    
    logged_in = False
    attempts = 0

    while not logged_in and attempts < 3:
        email = raw_input("Email: ")
        password = getpass()

        logged_in = api.login(email, password)
        attempts += 1

    return api

def main():
    """Demonstrates some api features.
    Logs in, gets library, searches for a song, selects the first result, 
    then creates a new playlist and adds that song to it.
    Finally, it renames and deletes the playlist.
    """

    api = init()

    print "Loading library...",
    library = api.get_sj_tracks()
    print "done"

    print len(library), "tracks detected."
    print
    
    query = raw_input("Search Query: ")
    search_results = api.search(query)
        
    #Note that this only looks at hits on songs.
    #Songs matched on artist/album hits are discarded by selecting ['songs'].
    songs = search_results['results']['songs']
    if len(songs) == 0:
        print "No songs from that search."
        return

    song = songs[0]
    print "Selected", song['title'],"by",song['artist']
    song_id = song['id']

    track = api.get_sj_track(song_id)

    playlist_name = raw_input("New playlist name: ")
    res = api.sj_create_playlist(playlist_name)

    if not res:
        print "Failed to make the playlist."
        return

    print "Made new playlist named", res.name
    playlist = res

    res = api.sj_add_to_playlist(playlist, track)
    print "Added to playlist."

    playlist.name = 'api playlist'
    res = api.sj_update_playlist(playlist)
    print "Changed playlist name to 'api playlist'."

    raw_input("Press enter to delete the playlist.")
    res = api.sj_delete_playlist(playlist)
    print "Deleted playlist."

    print "Done!"
    
    api.logout()

if __name__ == '__main__':
    main()
