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

from copy import copy
from melk.util.typecheck import is_listy, is_dicty, is_atomic
import simplejson
from types import StringType, UnicodeType, FloatType, LongType, IntType
import logging 
log = logging.getLogger(__name__)

__all__ = ['Dibject', 'json_sleep', 'json_wake', 'dibjectify', 'deep_copy_dibject']

class Dibject(dict):
    """
    A dibject is a dict that can access its keys through 
    attributes like javascript objects...

    eg: 
    
    >>> dd = Dibject()
    >>> dd['abc'] = 'def'
    >>> dd.abc
    'def'
    >>> dd.abc = 'xyz'
    >>> dd['abc']
    'xyz'
    >>> dd = Dibject()
    >>> dd.ghi = 'jkl'
    >>> dd['ghi']
    'jkl'
    >>> dd['ghi'] = 'xyz'
    >>> dd.ghi
    'xyz'

    """

    def __getattr__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            pass
        
        try:
            assert not key.startswith('_')
            return self.__getitem__(key)
        except:
            raise AttributeError, "object has no attribute '%s'" % key

    def __setattr__(self, key, value):
        if key.startswith('_'):
            self.__dict__[key] = value
        else:
            return self.__setitem__(key, value)

def json_sleep(ff):
    """
    returns unicode string with json dump of feed object
    """
    return simplejson.dumps(ff).decode('utf-8')

def json_wake(juni):
    """
    returns feed object obtained by parsing the unicode json 
    string given, as produced by json_sleep
    """
    dd = simplejson.loads(juni, object_hook=Dibject)
    
    # strangely the object hook may not be called for the empty dict?!
    if isinstance(dd, dict) and not isinstance(dd, Dibject) and len(dd) == 0:
        return Dibject()
    else:
        return dd

def dibjectify(ob):
    try:
        return _dibjectify(ob)
    except:
        import traceback
        log.debug('Skipping "%s" of type %s: %s' % (ob, ob.__class__, traceback.format_exc()))
        return None

def _dibjectify(ob):
    """
    extracts whatever looks like a concoction of 
    dicts, lists and atomic types in ob and 
    recreates them as dicts, lists and atomic types

    dicts come back as the dict subclass Dibject
    which allows keys to be accessed as attributes
    like feedparser.
    """
    if ob is None:
        return None

    if is_atomic(ob):
        if isinstance(ob, UnicodeType):
            return UnicodeType(ob)
        elif isinstance(ob, StringType):
            return StringType(ob)
        elif isinstance(ob, IntType):
            return IntType(ob)
        elif isinstance(ob, FloatType):
            return FloatType(ob)
        elif isinstance(ob, LongType):
            return LongType(ob)
        else:
            log.debug('Skipping "%s" of atomic type %s' % (ob, ob.__class__))
            return None

    elif is_dicty(ob):
        d = Dibject()
        for (k, v) in ob.items():
            fk = dibjectify(k)
            fv = dibjectify(v)
            if fv is not None and fk is not None:
                d[fk] = fv
        return d

    elif is_listy(ob):
        l = []
        for x in ob:
            fv = dibjectify(x)
            if fv is not None:
                l.append(fv)
        return l

    else:
        log.debug('Skipping "%s" of unserializable type %s' % (ob, ob.__class__))
        return None

# maybe better since it's in C... ?
#def dibjectify(thinger):
#    return json_wake(json_sleep(thinger))
    
def deep_copy_dibject(other_thinger):
    return dibjectify(other_thinger)


