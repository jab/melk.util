# Copyright (C) 2007 The Open Planning Project
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301
# USA

import urlparse
import urllib
import cgi
from melk.util.typecheck import is_atomic, is_listy
from types import UnicodeType

__all__ = ['normalize_object_uri', 'parse_object_uri', 'make_object_uri']


def normalize_object_uri(uri): 
    """
    normalizes an object uri so that it can 
    be compared directly to another normalized
    object_uri for equality as strings.

    - path parameters are dropped
    - fragments are dropped
    - lower cased 'host', 'scheme'
    - arguments are sorted by key, then value 
    - spaces are represented by +
    - %xx encoded entities are upcase only
    """
    # this should be ascii or there is a problem with the input
    object_uri = uri.encode('ascii')
    # this can come back as a string or unicode for some reason, but should always be ascii too...
    uri_parts = [x.encode('ascii') for x in urlparse.urlsplit(object_uri)]

    # parse the query string
    qsparts = cgi.parse_qsl(uri_parts[3], keep_blank_values=True)
    qsparts.sort()
    new_query = urllib.urlencode(qsparts)

    return urlparse.urlunsplit([uri_parts[0].lower(), 
                                uri_parts[1].lower(),
                                uri_parts[2],
                                new_query,
                                ''])

def parse_object_uri(object_uri): 
    """
    returns base uri and dictionary of
    query arguments. all output is unicode.
    """
    object_uri = normalize_object_uri(object_uri)

    uri_parts = urlparse.urlsplit(object_uri)
    base_uri = urlparse.urlunsplit(list(uri_parts[0:3]) + ['','']).decode('ascii')
    query_args = cgi.parse_qs(uri_parts[3], keep_blank_values=True)
    
    def _unqslify(arg):
        # the returned parse appears to be in latin-1... !? whatever...
        return arg.decode('latin-1').decode('unicode_escape')

    args = {}
    for arg in query_args:
        uarg = _unqslify(arg)
        if len(query_args[arg]) == 1:
            args[uarg] = _unqslify(query_args[arg][0])
        else:
            args[uarg] = [_unqslify(x) for x in query_args[arg]]

    return base_uri, args

def make_object_uri(base_uri, cfg):
    """
    takes a base uri and a dictionary of limited form and 
    produces an object uri.

    keys should be strings, values should 
    be unicodes, or lists of unicodes. strings
    or other types that have __str__ may be used but
    they must be in utf-8 encoding.
    """

    qargs = []
    for k, vs in cfg.items():
        okey = _ascii_escape(k)
        if is_atomic(vs):
            qargs.append( (okey, _ascii_escape(vs)) )
        elif is_listy(vs):
            for v in vs:
                qargs.append( (okey, _ascii_escape(v)) )

    uri = base_uri + "?" + urllib.urlencode(qargs)
    return normalize_object_uri(uri)

def _ascii_escape(istr):
    if isinstance(istr, UnicodeType):
        return istr.encode('unicode_escape')
    else:
        return str(istr).decode('utf-8').encode('unicode_escape')
