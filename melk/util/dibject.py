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


class DibWrap(dict):
    """
    This is like a Dibject but instead it 
    wraps a given dictionary from another 
    source.  It will recursively wrap 
    inner dictionaries to provide 
    attribute access.
    
    if the underlying dictionary is changed, 
    so is the dibwrap's value of that attribute:
    
    >>> from melk.util.dibject import DibWrap
    >>> d = dict(foo='bar')
    >>> dw = DibWrap(d)
    >>> dw.foo
    'bar'
    >>> d['foo'] = 'twelve'
    >>> dw.foo
    'twelve'
    
    this also works with sub-dictionaries:
    >>> from melk.util.dibject import DibWrap
    >>> d = {'foo': {'bar': 'quux'}}
    >>> dw = DibWrap(d)
    >>> dw.foo.bar
    'quux'
    
    and even sub-dictionaries inside lists...
    >>> from melk.util.dibject import DibWrap
    >>> d = {'foo': [{'bar': 'quux'}, {'zoom': 'blip'}]}
    >>> dw = DibWrap(d)
    >>> dw.foo[0].bar
    'quux'
    >>> dw.foo[1].zoom
    'blip'
    
    etc.
    """
    
    def __init__(self, wdict):
        self._data = wdict

    # attribute access...

    def __getattr__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            pass

        try:
            assert not key.startswith('_')
            return self.__getitem__(key)
        except:
            raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, key))


    def __setattr__(self, key, value):
        if key.startswith('_'):
            self.__dict__[key] = value
        else:
            return self.__setitem__(key, value)

    ##################################################
    # dict proxy...
    def __cmp__(self, other):
        return self._data.__cmp__(other)

    def __contains__(self, item):
        return self._data.__contains__(item)

    # def __delattr__(self, name):

    def __delitem__(self, key):
        return self._data.__delitem__(key)

    def __eq__(self, other):
        return self._data.__eq__(other)

    def __ge__(self, other):
        return self._data.__ge__(other)

    # def __getattribute__(self, name):

    def __getitem__(self, key):
        return self.wrap(self._data.__getitem__(key))
        
    def __gt__(self, other):
        return self._data.__gt__(other)

    # def __hash__(self):

    def __iter__(self):
        return self._data.__iter__()

    def __le__(self, other):
        return self._data.__le__(other)

    def __len__(self):
        return self._data.__len__()

    def __lt__(self, other):
        return self._data.__lt__(other)

    def __ne__(self, other):
        return self._data.__ne__(other)

    # def __reduce__(self):
    # def __reduce_ex__(self):

    def __repr__(self):
        return self._data.__repr__()

    # def __setattr__(self, name, value)

    def __setitem__(self, key, value):
        self._data.__setitem__(key, value)

    def __str__(self):
        return str(self._data)

    def __unicode__(self):
        return unicode(self._data)

    def clear(self):
        return self._data.clear()

    # def copy():

    @classmethod
    def fromkeys(cls, seq, value=None):
        return DibWrap(dict.fromkeys(seq, value=value))

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def has_key(self, key):
        return self._data.has_key(key)

    def items(self):
        return list(self.iteritems())

    def iteritems(self):
        for (k, v) in self._data.iteritems():
            yield (k, self.wrap(v))

    def iterkeys(self):
        return self._data.iterkeys()

    def itervalues(self):
        for v in self._data.itervalues():
            yield self.wrap(v)

    def keys(self):
        return list(self.iterkeys())

    def pop(self, *args):
        if len(args) == 0:
            raise TypeError('pop expected at least 1 arguments, got 0')
        if len(args) > 2:
            raise TypeError('pop expected at most 2 arguments, got %d' % len(args))


        try:
            popkey = args[0]
            return self.wrap(self._data.pop(popkey))
        except KeyError:
            if len(args) == 1:
                raise
            else:
                return args[1]

    def popitem(self):
        k, v = self._data.popitem()
        return (k, self.wrap(v))

    def setdefault(self, key, default=None):
        return self._data.setdefault(key, default=default)

    def update(self, other):
        return self._data.update(other)

    def values(self):
        return [self.wrap(v) for v in self._data.values()]

    @classmethod
    def wrap(self, val):
        if is_atomic(val):
            return val
        elif is_listy(val):
            return DibListProxy(val)
        elif is_dicty(val):
          return DibWrap(val)
        else:
            return val

    def unwrap(self):
        return _data
        

class DibListProxy(list):
    """
    this is a list proxy that wraps any dicts
    inside itself with DibWraps
    """
    def __init__(self, list):
        self._data = list

    def __lt__(self, other):
        return self._data < other

    def __le__(self, other):
        return self._data <= other

    def __eq__(self, other):
        return self._data == other

    def __ne__(self, other):
        return self._data != other

    def __gt__(self, other):
        return self._data > other

    def __ge__(self, other):
        return self._data >= other

    def __repr__(self):
        return repr(self._data)

    def __str__(self):
        return str(self._data)

    def __unicode__(self):
        return unicode(self._data)

    def __delitem__(self, index):
        del self._data[index]

    def __getitem__(self, index):
        return DibWrap.wrap(self._data[index])

    def __setitem__(self, index, value):
        self._data[index] = value

    def __contains__(self, value):
        return value in self._data

    def __iter__(self):
        for index in range(len(self)):
            yield self[index]

    def __len__(self):
        return len(self._data)

    def __nonzero__(self):
        return bool(self._data)

    def append(self, *args, **kwargs):
        return self._data.append(*args, **kwargs)

    def count(self, value):
        return self._data.count(value)

    def extend(self, list):
        for item in list:
            self.append(item)

    def index(self, value):
        return self._data.index(value)

    def insert(self, idx, *args, **kwargs):
        return self._data.insert(idx, *args, **kwargs)

    def remove(self, value):
        return self._data.remove(value)
        
if __name__ == '__main__':
    import doctest
    doctest.testmod()