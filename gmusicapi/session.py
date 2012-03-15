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

"""The session layer allows for authentication and the making of authenticated requests."""

import cookielib
import exceptions
import urllib
import urllib2
import os
import json
import warnings
from urllib2  import *
from urlparse import *
import httplib

try:
    from decorator import decorator
except ImportError:
    from utils.utils import mock_decorator as decorator

import mechanize

from utils.apilogging import UsesLog
from utils.clientlogin import ClientLogin

try:
    # These are for python3 support
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
    from urllib.parse import urlencode
    unistr = str
except ImportError:
    # Fallback to python2
    from urllib2 import urlopen, Request
    from urllib2 import HTTPError
    from urllib import urlencode
    unistr = unicode


class AlreadyLoggedIn(exceptions.Exception):
    pass
class NotLoggedIn(exceptions.Exception):
    pass


class WC_Session(UsesLog):
    """A session for the GM web client."""


    #The wc requires a common user agent.
    _user_agent = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)"


    def __init__(self):
        self._cookie_jar = cookielib.LWPCookieJar() #to hold the session
        self.logged_in = False

        self.init_logger()

    def logout(self):
        self.__init__() #discard our session


    def open_authed_https_url(self, url_builder, extra_url_args=None, encoded_data = None):
        """Same as open_https_url, but raises an exception if the session isn't logged in."""
        if not self.logged_in:
            raise NotLoggedIn

        return self.open_https_url(url_builder, extra_url_args, encoded_data)

    def open_https_url(self, url_builder, extra_url_args=None, encoded_data = None):
        """Opens an https url using the current session and returns the response.
        Code adapted from: http://code.google.com/p/gdatacopier/source/browse/tags/gdatacopier-1.0.2/gdatacopier.py
        :param url_builder: the url, or a function to receieve a dictionary of querystring arg/val pairs and return the url.
        :extra_url_args: (optional) key/val querystring pairs.
        :param encoded_data: (optional) encoded POST data.
        """

        if isinstance(url_builder, basestring):
            url = url_builder
        else:
            url = url_builder({'xt':self.get_cookie("xt").value})
        
        #Add in optional pairs to the querystring.
        if extra_url_args:
            #Assumes that a qs has already been started (ie we don't need to put a ? first)
            assert (url.find('?') >= 0)

            extra_args = ""
            for name, val in extra_url_args.iteritems():
                extra_args += "&{0}={1}".format(name, val)

            url += extra_args
        
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._cookie_jar))

        opener.addheaders = [('User-agent', self._user_agent)]
        
        if encoded_data:
            response = opener.open(url, encoded_data)
        else:
            response = opener.open(url)
            
        return response

    def get_cookie(self, name):
        """Finds a cookie by name from the cookie jar.
        Returns None on failure.

        :param name:
        """

        for cookie in self._cookie_jar:
            if cookie.name == name:
                return cookie

        return None

    def login(self, email, password):
        """Attempts to login with the given credentials.
        Returns True on success, False on failure.
        
        :param email:
        :param password:
        """

        if self.logged_in:
            raise AlreadyLoggedIn

        #It's easiest just to emulate a browser; some fields are filled by javascript.
        #This code adapted from: http://stockrt.github.com/p/emulating-a-browser-in-python-with-mechanize/

        br = mechanize.Browser()
        br.set_cookiejar(self._cookie_jar)

        # Browser options
        br.set_handle_equiv(True)
        
        #Suppress warning that gzip support is experimental.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            br.set_handle_gzip(True) 

        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)

        # Follows refresh 0 but doesn't hang on refresh > 0
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        # Google auth requires a common user-agent.
        br.addheaders = [('User-agent', self._user_agent)]

        br.open('https://music.google.com')

        br.select_form(nr=0)

        br.form['Email']=email
        br.form['Passwd']=password
        br.submit()

        self.logged_in = True if self.get_cookie("SID") else False

        return self.logged_in


class MM_Session:    
    """A session for the Music Manager."""

    @decorator
    def require_auth(f, self = None, *args, **kw):
        """Decorator to check for auth before running a function.
        Assumes that the function is a member of this class.
        """

        if not self.sid:
            raise NotLoggedIn

        return f(self, *args, **kw)

    def __init__(self):
        self.sid = None

        self.android = httplib.HTTPSConnection("android.clients.google.com")
        self.jumper = httplib.HTTPConnection('uploadsj.clients.google.com')

    def login(self, email, password):

        if self.sid:
            raise AlreadyLoggedIn

        client = ClientLogin(email, password, 'sj')
        self.sid = client.get_sid_token()

        if self.sid is None:
            return False

        return True


    def logout(self):
        self.sid = None
        #There's got to be more to do...

    @require_auth
    def protopost(self, path, proto):
        """Returns the response from encoding and posting the given data.
        
        :param path: the name of the service url
        :param proto: data to be encoded with protobuff
        """

        self.android.request("POST", "/upsj/"+path, proto.SerializeToString(), {
            "Cookie": ('SID=%s' % self.sid),
            "Content-Type": "application/x-google-protobuf"
        })
        r = self.android.getresponse()

        return r.read()

    @require_auth
    def jumper_post(self, url, encoded_data, headers=None):
        """Returns the response of a post to the MM jumper service."""

        if not headers:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded", #? shouldn't it be json? but that's what the google client sends
                "Cookie": ('SID=%s' % self.sid)}

        self.jumper.request("POST", url, encoded_data, headers)

        return self.jumper.getresponse()


class SJ_Session:
    """A session using the SkyJam Service API."""

    def __init__(self):
        self.client = None
        self.cookie = None

    def _get_cookie(self):
        header = {'Authorization': 'GoogleLogin auth=%s' % self.client.get_auth_token()}

        req = Request('https://music.google.com/music/listen?u=0', None, header)
        resp_obj = urlopen(req)
        info = resp_obj.info()

        cookies = dict(s.split(';', 1)[0].split('=', 1) for s in info.getheaders('Set-Cookie'))
        if 'sjsaid' not in cookies:
            raise KeyError

        self.cookie = cookies['sjsaid']


    def login(self, email, password):
        self.client = ClientLogin(email, password, 'sj')

        if self.client.get_auth_token() is None:
            return False

        self._get_cookie()

        return True

    def logout(self):
        self.client = None

    def request(self, url, data=None, headers={}):
        if not data:
            data = None
        else:
            if type(data) is not str:
                data = urlencode(data)
            data = data.encode('utf8')

        if not 'Content-Type' in headers:
            headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'GoogleLogin auth=%s' % self.client.get_auth_token()

        req = Request(url, data, headers)
        err = None

        try:
            resp_obj = urlopen(req)
        except HTTPError as e:
            err = e.code
            return err, e.read()
        resp = resp_obj.read()
        resp_obj.close()
        return None, unistr(resp, encoding='utf8')

    def audio_request(self, url, headers={}):
        if not 'Content-Type' in headers:
            headers['Content-Type'] = 'audio/mp3'
        headers['Authorization'] = 'GoogleLogin auth=%s' % self.client.get_auth_token()
        headers['Cookie'] = 'sjsaid=%s' % self.cookie

        req = Request(url, None, headers)
        err = None

        try:
            resp_obj = urlopen(req)
        except HTTPError as e:
            err = e.code
            return err, e.read()
        resp = resp_obj.read()
        resp_obj.close()

        return None, resp
