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


class Dibject(dict):
    """
    A dibject is a dict that can access it's keys through 
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
            raise AttributeError, "object has ot attribute '%s'" % key

    def __setattr__(self, key, value):
        if key.startswith('_'):
            self.__dict__[key] = value
        else:
            return self.__setitem__(key, value)
