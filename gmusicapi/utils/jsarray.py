# -*- coding: utf-8 -*-

"""
Tools to handle Google's ridiculous interchange format.
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import *
from future import standard_library
standard_library.install_aliases()

from io import StringIO
from tokenize import generate_tokens

from gmusicapi.compat import json


def to_json(s):
    """Return a valid json string, given a jsarray string.

    :param s: string of jsarray data
    """
    out = []

    for t in generate_tokens(StringIO(s).readline):
        if out and any(((',' == t[1] == out[-1]),  # double comma
                        (out[-1] == '[' and t[1] == ','),  # comma opening array
                        )):
            out.append('null')

        out.append(t[1])

    return ''.join(out)


def loads(s):
    return json.loads(to_json(s))
