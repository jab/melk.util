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

from types import UnicodeType
from urllib import quote_plus, unquote_plus, urlencode
from urlparse import urlsplit, urlunsplit

try:
    # python 2.6
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from melk.util.typecheck import is_atomic, is_listy
from melk.util.urlnorm import canonical_url

__all__ = ['normalize_object_uri', 'parse_object_uri', 'make_object_uri']


def normalize_object_uri(uri): 
    return canonical_url(uri)

def parse_object_uri(object_uri): 
    """
    returns base uri and dictionary of
    query arguments. all output is unicode.
    """
    object_uri = normalize_object_uri(object_uri)
    
    uri_parts = urlsplit(object_uri)
    base_uri = urlunsplit(list(uri_parts[0:3]) + ['','']).decode('ascii')
    query_args = parse_qs(uri_parts[3], keep_blank_values=True)

    args = {}
    for arg in query_args:
        uarg = arg.decode('utf-8')
        if len(query_args[arg]) == 1:
            args[uarg] = query_args[arg][0].decode('utf-8')
        else:
            args[uarg] = [x.decode('utf-8') for x in query_args[arg]]

    return base_uri, args

def make_object_uri(base_uri, cfg):
    """
    takes a base uri and a dictionary of limited form and 
    produces an object uri.

    base_uri and keys should be strings, values should 
    be unicodes, or lists of unicodes. strings
    or other types that have __str__ may be used but
    they must be in utf-8 encoding.
    """
    qargs = []
    for k, vs in cfg.items():
        okey = _to_utf8(k)
        if is_atomic(vs):
            qargs.append( (okey, _to_utf8(vs)) )
        elif is_listy(vs):
            for v in vs:
                qargs.append( (okey, _to_utf8(v)) )

    uri = base_uri + "?" + urlencode(qargs)
    return normalize_object_uri(uri)

def _to_utf8(s):
    """
    encodes s to utf-8 if it is a unicode, 
    otherwise asserts that it is a string in utf-8
    """
    if isinstance(s, UnicodeType):
        return s.encode('utf-8')
    else:
        return s.decode('utf-8').encode('utf-8')