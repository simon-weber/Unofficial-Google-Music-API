from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from gmusicapi.clients.webclient import Webclient
from gmusicapi.clients.musicmanager import Musicmanager, OAUTH_FILEPATH
from gmusicapi.clients.mobileclient import Mobileclient

(Webclient, Musicmanager, Mobileclient, OAUTH_FILEPATH)  # noqa
