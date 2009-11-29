from collections import MutableMapping
from heapq import heapify, heappop, heappush, heapreplace
from itertools import izip, repeat


# based on OrderedDict recipe for Python >= 2.6:
# http://code.activestate.com/recipes/576669/
class NLDict(dict, MutableMapping):
    """
    Mapping type that stores only the n largest elements according to an
    arbitrary comparison function ``sortkey`` (pass ``None`` to compare
    elements directly). Once the mapping reaches capacity, a larger item
    kicks the smallest one out when inserted.

        >>> from datetime import datetime, timedelta
        >>> from operator import attrgetter, itemgetter
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
        >>> sorted(largest4.items(), key=itemgetter(1))
        [('ten', 10), ('sixteen', 16), ('twenty', 20), ('forty', 40)]

    Test the rest of the interface::

        >>> largest4.setdefault('forty', 2)
        40
        >>> largest4.setdefault('twelve', 12) # replaces 10
        12
        >>> sorted(largest4.items(), key=itemgetter(1))
        [('twelve', 12), ('sixteen', 16), ('twenty', 20), ('forty', 40)]
        >>> largest4.update([('fifty', 50), ('sixty', 60)])
        >>> sorted(largest4.items(), key=itemgetter(1))
        [('twenty', 20), ('forty', 40), ('fifty', 50), ('sixty', 60)]
        >>> largest4.update({'zero': 0}, one=1) # too small to go in
        >>> sorted(largest4.items(), key=itemgetter(1))
        [('twenty', 20), ('forty', 40), ('fifty', 50), ('sixty', 60)]
        >>> largest4.popitem() # pops the smallest mapping
        ('twenty', 20)
        >>> del largest4['sixty']
        >>> sorted(largest4.items(), key=itemgetter(1))
        [('forty', 40), ('fifty', 50)]

    Test changing maxlen::
        
        >>> largestn = largest4.copy()
        >>> largestn.maxlen = 1 # should discard 40
        >>> sorted(largestn.items(), key=itemgetter(1))
        [('fifty', 50)]
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
        """
        :param maxlen: the maximum number of elements to contain before smallest
            elements start falling off the end; must be at least 1
        :param sortkey: function to call on contained elements to determine
            their ordering, e.g. operator.attrgetter('timestamp'); pass ``None``
            to compare contained elements directly

        Additional positional or keyword arguments are passed to :attr:`update`.

        :raises: :exc:`ValueError` if :attr:`maxlen` <= 0 or :attr:`sortkey` is
            neither ``None`` nor a callable
        :raises: any exception raised by the :attr:`update` call, e.g.
            :exc:`TypeError` if more than one positional argument was given via
            *args
        """
        if maxlen <= 0:
            raise ValueError('maxlen must be at least 1')
        if sortkey is not None and not hasattr(sortkey, '__call__'):
            raise ValueError('sortkey must be either None or a callable')
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
            self.popsmallest()

    maxlen = property(_maxlen_get, _maxlen_set)

    def clear(self):
        del self._heap[:]
        dict.clear(self)
    
    def copy(self):
        """
        Returns a shallow copy.
        """
        return self.__class__(self._maxlen, self._sortkey, self)

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
        to delete and then reheapify!
        """
        value = dict.pop(self, key)
        cmpval = self._sortkey(value) if self._sortkey else value
        heapitem = (cmpval, key)
        self._heap.remove(heapitem)
        heapify(self._heap)

    def popsmallest(self):
        """
        Removes and returns the (key, value) pair with smallest sorted value.
        """
        if not self:
            raise KeyError
        removed = heappop(self._heap)
        key = removed[1]
        value = dict.pop(self, key)
        return key, value

    popitem = popsmallest

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
        return '%s(maxlen=%d, sortkey=%r, {%s})' % (self.__class__.__name__,
            self._maxlen, self._sortkey, pairs)
    __str__ = __repr__

    @classmethod
    def fromkeys(cls, maxlen, sortkey, iterable, value=None):
        return cls(maxlen, sortkey, izip(iterable, repeat(value)))

def maybe_nldict(maxlen=None, sortkey=None, *args, **kwds):
    if maxlen is None:
        return dict(*args, **kwds)
    return NLDict(maxlen, sortkey, *args, **kwds)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
