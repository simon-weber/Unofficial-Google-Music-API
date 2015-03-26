from __future__ import (unicode_literals, print_function, division,
                        absolute_import)
from future import standard_library
standard_library.install_aliases()
from gmusicapi.clients.webclient import Webclient
from gmusicapi.clients.musicmanager import Musicmanager, OAUTH_FILEPATH
from gmusicapi.clients.mobileclient import Mobileclient

(Webclient, Musicmanager, Mobileclient, OAUTH_FILEPATH)  # noqa
