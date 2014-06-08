gmusicapi: an unofficial API for Google Play Music
==================================================

edit

gmusicapi allows control of
`Google Music <http://music.google.com>`__ with Python.

.. code-block:: python

    from gmusicapi import Mobileclient
    
    api = Mobileclient()
    api.login('user@gmail.com', 'my-password')
    # => True
    
    library = api.get_all_songs()
    sweet_track_ids = [track['id'] for track in library
                       if track['artist'] == 'The Cat Empire']
    
    playlist_id = api.create_playlist('Rad muzak')
    api.add_songs_to_playlist(playlist_id, sweet_track_ids)
    
**gmusicapi is not supported nor endorsed by Google.**

That said, it's actively maintained, and powers a bunch of cool projects:

-  alternate clients, including
   `a command line client <https://github.com/mstill/thunner>`__
   and `FUSE filesystem <https://github.com/EnigmaCurry/GMusicFS>`__
-  `syncing tools <https://github.com/thebigmunch/gmusicapi-scripts>`__ for library management
-  `playlist tools <https://github.com/soulfx/gmusic-playlist>`__ for playlist management
-  proxies for media players, such as
   `gmusicproxy <http://gmusicproxy.net>`__ and
   `gmusicprocurator <https://github.com/malept/gmusicprocurator>`__,
   as well as plugins for 
   `Mopidy <https://github.com/hechtus/mopidy-gmusic>`__ and
   `Squeezebox <https://github.com/hechtus/squeezebox-googlemusic>`__.


Getting started
---------------
Everything you need is at http://unofficial-google-music-api.readthedocs.org.

If the documentation doesn't answer your questions, or you just want to get
in touch, either `drop by #gmusicapi on Freenode
<http://webchat.freenode.net/?channels=gmusicapi>`__ or shoot me an email.

Status and updates
------------------

.. image:: https://travis-ci.org/simon-weber/Unofficial-Google-Music-API.png?branch=develop
        :target: https://travis-ci.org/simon-weber/Unofficial-Google-Music-API

* November 2013: I started working fulltime at Venmo, meaning this project is back to night and weekend development.
* March 2014: a Google update broke much of the deprecated webclient interface and temporarily disrupted mobileclient streaming.


For fine-grained development updates, follow me on Twitter:
`@simonmweber <https://twitter.com/simonmweber>`__.

------------

Copyright 2014 `Simon Weber <http://www.simonmweber.com>`__.
Licensed under the 3-clause BSD. See LICENSE.
