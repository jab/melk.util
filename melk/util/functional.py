# Copyright (C) 2008 The Open Planning Project
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



## 'any' and 'all' are not in __builtins__ before
## python 2.5, so define them here if necessary

try:
    any, all

except NameError:
    from itertools import ifilter, ifilterfalse

    def all(seq, pred=None):
        "Returns True if pred(x) is true for every element in the iterable"
        for elem in ifilterfalse(pred, seq):
            return False
        return True

    def any(seq, pred=None):
        "Returns True if pred(x) is true for at least one element in the iterable"
        for elem in ifilter(pred, seq):
            return True
        return False

any = any
all = all



def flatten(x):
    """
    http://kogs-www.informatik.uni-hamburg.de/~meine/python_tricks

    flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result
