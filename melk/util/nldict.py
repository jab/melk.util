from collections import MutableMapping
from heapq import heapify, heappop, heappush, heapreplace


# based on OrderedDict recipe for Python >= 2.6:
# http://code.activestate.com/recipes/576669/
class NLDict(dict, MutableMapping):
    """
    Mapping type that stores only the n largest elements according to an
    arbitrary comparison function ``sortkey`` (pass ``None`` to compare
    elements directly). A larger item kicks the smallest one out when
    inserted once the mapping reaches capacity.

        >>> from datetime import datetime, timedelta
        >>> from operator import attrgetter
        >>> class NewsItem(object):
        ...     def __init__(self, id, timestamp):
        ...         self.id = id
        ...         self.timestamp = timestamp
        >>> now = datetime.utcnow()
        >>> inow = NewsItem('n', now)
        >>> ilastweek = NewsItem('lw', now - timedelta(days=7))
        >>> ilastmonth = NewsItem('lm', now - timedelta(days=31))
        >>> ilastyear = NewsItem('ly', now - timedelta(days=365))
        >>> mostrecent = NLDict(2, attrgetter('timestamp'))
        >>> len(mostrecent)
        0
        >>> mostrecent[ilastweek.id] = ilastweek
        >>> ilastweek.id in mostrecent
        True
        >>> mostrecent[ilastmonth.id] = ilastmonth
        >>> ilastmonth.id in mostrecent
        True
        >>> len(mostrecent)
        2

    Adding inow should kick out ilastmonth and leave ilastweek::

        >>> mostrecent[inow.id] = inow
        >>> len(mostrecent)
        2
        >>> ilastmonth.id in mostrecent
        False
        >>> ilastweek.id in mostrecent
        True
    
    Inserting ilastyear should not actually add it since it's too old::

        >>> mostrecent[ilastyear.id] = ilastyear
        >>> ilastyear.id in mostrecent
        False
        >>> len(mostrecent)
        2

    Test update::

        >>> mostrecent.clear()
        >>> len(mostrecent)
        0
        >>> mostrecent.update({inow.id: inow, ilastweek.id: ilastweek,
        ...     ilastmonth.id: ilastmonth, ilastyear.id: ilastyear})
        >>> len(mostrecent)
        2
        >>> inow.id in mostrecent and ilastweek.id in mostrecent
        True
        >>> ilastmonth.id not in mostrecent and ilastyear.id not in mostrecent
        True

    Test initializers, don't specify a key function::

        >>> largest2 = NLDict(2, None, [(1, 1), (2, 2), (3, 3)])
        >>> sorted(largest2.values())
        [2, 3]
        >>> largest3 = NLDict(3, None,
        ...     twenty=20,
        ...     sixteen=16,
        ...     ten=10,
        ...     forty=40,
        ...     )
        >>> sorted(largest3.values())
        [16, 20, 40]
        >>> largest4 = NLDict(4, None, {
        ...     'one': 1,
        ...     'twenty': 20,
        ...     'sixteen': 16,
        ...     'ten': 10,
        ...     'forty': 40,
        ...     })
        >>> sorted(largest4.values())
        [10, 16, 20, 40]

    Test the rest of the interface::

        >>> largest4.setdefault('forty', 2)
        40
        >>> largest4.setdefault('twelve', 12) # replaces 10
        12
        >>> largest4['twelve']
        12
        >>> largest4.poplast()
        ('twelve', 12)
        >>> del largest4['sixteen']
        >>> len(largest4)
        2

    Test changing maxlen::
        
        >>> largestn = largest4
        >>> largestn.maxlen = 1 # should discard 20
        >>> largestn.values()
        [40]
        >>> largestn.maxlen = 5
        >>> largestn.update(a=100, b=101, c=102, d=103, e=104, f=105)
        >>> sorted(largestn.values())
        [101, 102, 103, 104, 105]

    Test fromkeys (tie goes to already inserted)::

        >>> largest2 = NLDict.fromkeys(2, None, (-1, 0, 1), 0)
        >>> sorted(largest2.items())
        [(-1, 0), (0, 0)]

    """

    def __init__(self, maxlen, sortkey, *args, **kwds):
        self._heap = []
        self._maxlen = maxlen
        self._sortkey = sortkey
        if args or kwds:
            self.update(*args, **kwds)

    def _maxlen_get(self):
        return self._maxlen

    def _maxlen_set(self, value):
        self._maxlen = value
        nover = max(0, len(self) - value)
        for i in xrange(nover):
            self.poplast()

    maxlen = property(_maxlen_get, _maxlen_set)

    def clear(self):
        del self._heap[:]
        dict.clear(self)

    def __setitem__(self, key, value):
        cmpval = self._sortkey(value) if self._sortkey else value
        heapitem = (cmpval, key)
        if len(self) < self._maxlen:
            heappush(self._heap, heapitem)
            dict.__setitem__(self, key, value)
        elif heapitem[0] > self._heap[0][0]:
            removed = heapreplace(self._heap, heapitem)
            dict.__delitem__(self, removed[1])
            dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        """
        This is not O(1) because we have to traverse the heap to find the item
        to delete and then reheapify
        """
        value = dict.pop(self, key)
        cmpval = self._sortkey(value) if self._sortkey else value
        heapitem = (cmpval, key)
        self._heap.remove(heapitem)
        heapify(self._heap)

    def popitem(self):
        if not self:
            raise KeyError
        removed = heappop(self._heap)
        key = removed[1]
        value = dict.pop(self, key)
        return key, value

    poplast = popitem

    __iter__ = dict.__iter__

    # Methods with indirect access via the above methods

    setdefault = MutableMapping.setdefault
    update = MutableMapping.update
    pop = MutableMapping.pop
    keys = MutableMapping.keys
    values = MutableMapping.values
    items = MutableMapping.items

    def __repr__(self):
        pairs = ', '.join(map('%r: %r'.__mod__, self.items()))
        return '%s(maxlen=%d, {%s})' % (self.__class__.__name__, self._maxlen, pairs)

    @classmethod
    def fromkeys(cls, maxlen, sortkey, iterable, value=None):
        d = cls(maxlen, sortkey)
        for key in iterable:
            d[key] = value
        return d


def maybe_nldict(maxlen=None, sortkey=None, *args, **kwds):
    if maxlen is None:
        return dict(*args, **kwds)
    return NLDict(maxlen, sortkey, *args, **kwds)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
