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

from types import *
from UserDict import *
from UserList import *

__all__ = ['is_listy', 'is_dicty', 'is_atomic']

LIST_TYPES = (ListType, TupleType, UserList)
def is_listy(ob):
    if isinstance(ob, LIST_TYPES):
        return True
        
    if is_atomic(ob):
        return False

    # otherwise listen for quacks
    try: 
        iter(ob)
    except TypeError:
        return False
    
    try:
        ob[0:0]
        # it's iterable and sliceable...
        return True
    except TypeError:
        return False
    
DICT_TYPES = (DictType, UserDict, DictMixin)
def is_dicty(ob):
    if isinstance(ob, DICT_TYPES):
        return True
    
    # otherwise listen for quacks
    # XXX...
    
    return False
    

ATOMIC_BUILTIN_TYPES = (UnicodeType, StringType, 
                        BooleanType, IntType, 
                        LongType, FloatType)
def is_atomic(ob):
    return isinstance(ob, ATOMIC_BUILTIN_TYPES)
