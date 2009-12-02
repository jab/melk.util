from collections import MutableMapping
from heapq import heapify, heappop, heappush, heapreplace
from itertools import izip, repeat
from functools import wraps

from melk.util.obsdict import obsdict

# based on OrderedDict recipe for Python >= 2.6:
# http://code.activestate.com/recipes/576669/
class nldict(obsdict, MutableMapping):
    """
    A ``MutableMapping`` that stores only the ``maxlen`` mappings of largest
    value according to comparison function ``sortkey``, which should provide
    an ordering over the mapped value type. Once the map reaches capacity,
    inserting a mapping with a larger value kicks out the mapping with
    smallest value.

    Inherits from ``obsdict`` rather than ``dict`` to provide a callback
    mechanism you can use to tell whether an item you attempted to insert
    was actually inserted.

    Pass a ``maxlen`` of ``None`` to behave like a normal unbounded ``dict``.

    Pass a ``sortkey`` of ``None`` to compare mapping values directly.

    Example::

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

        >>> mostrecent = nldict(2, attrgetter('timestamp'))
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

        >>> largest2 = nldict(2, None, [(1, 1), (2, 2), (3, 3)])
        >>> sorted(largest2.values())
        [2, 3]
        >>> largest3 = nldict(3, None,
        ...     twenty=20,
        ...     sixteen=16,
        ...     ten=10,
        ...     forty=40,
        ...     )
        >>> sorted(largest3.values())
        [16, 20, 40]
        >>> largest4 = nldict(4, None, {
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

    Test changing maxlen on a copy::
        
        >>> largestn = largest4.copy()
        >>> sorted(largestn.items(), key=itemgetter(1))
        [('forty', 40), ('fifty', 50)]
        >>> largestn.maxlen = 1 # try decreasing. should discard 40
        >>> sorted(largestn.items(), key=itemgetter(1))
        [('fifty', 50)]
        >>> len(largest4) # the original should not have been changed
        2
        >>> largestn.maxlen = 5 # try increasing
        >>> largestn.update(a=100, b=101, c=102, d=103, e=104, f=105)
        >>> sorted(largestn.values())
        [101, 102, 103, 104, 105]

    Test maxlen of None (should behave like a regular dict)::

        >>> largestn.maxlen = None
        >>> largestn.update(one=1, two=2)
        >>> sorted(largestn.items(), key=itemgetter(1))
        [('one', 1), ('two', 2), ('b', 101), ('c', 102), ('d', 103), ('e', 104), ('f', 105)]
        >>> largestn['three'] = 3
        >>> largestn.pop('three')
        3
        >>> largestn.maxlen = 2 # test changing back
        >>> sorted(largestn.items(), key=itemgetter(1))
        [('e', 104), ('f', 105)]

    Test changing sortkey::

        >>> # start with an nlargest
        >>> flipflop = nldict(2, None, {'one': 1, 'two': 2})
        >>> flipflop['three'] = 3 # discards 1
        >>> sorted(flipflop.items(), key=itemgetter(1))
        [('two', 2), ('three', 3)]
        >>> # make it an nsmallest
        >>> flipflop.sortkey = lambda x: -x
        >>> flipflop['one'] = 1 # discards 3
        >>> sorted(flipflop.items(), key=itemgetter(1))
        [('one', 1), ('two', 2)]

    Test fromkeys (tie goes to already inserted)::

        >>> largest2 = nldict.fromkeys(2, None, (-1, 0, 1), 0)
        >>> sorted(largest2.items())
        [(-1, 0), (0, 0)]

    """

    def __init__(self, maxlen, sortkey, *args, **kwds):
        """
        :param maxlen: the max number of mappings stored before the ones with
            smallest sort value start being discarded. Must be at least 1.
            Pass ``None`` to specify no max (like a regular ``dict``).
        :param sortkey: function to call on mapping values to determine
            their ordering, e.g. ``operator.attrgetter('timestamp')``.
            Pass ``None`` to compare values directly.

        Additional positional or keyword arguments are passed to :attr:`update`.

        :raises: :exc:`ValueError` if :attr:`maxlen` is neither None nor <= 0 or
            if :attr:`sortkey` is neither ``None`` nor a callable
        :raises: any exception raised by the :attr:`update` call, e.g.
            :exc:`TypeError` if more than one positional argument was given via
            *args
        """
        if maxlen is not None and maxlen <= 0:
            raise ValueError('maxlen must be either None or at least 1')
        if sortkey is not None and not hasattr(sortkey, '__call__'):
            raise ValueError('sortkey must be either None or a callable')
        obsdict.__init__(self)
        self._maxlen = maxlen
        self._sortkey = sortkey
        self._heap = []
        self.update(*args, **kwds)

    def _reheapify(self):
        sk = self._sortkey
        self._heap = [(sk(v), k) for (k, v) in self.iteritems()] if sk else \
                     [(v, k) for (k, v) in self.iteritems()]
        heapify(self._heap)

    def _maxlen_get(self):
        return self._maxlen

    def _maxlen_set(self, value):
        if self._maxlen == value:
            return
        if value is not None:
            if self._maxlen is None:
                self._reheapify()
            self._maxlen = value
            nover = max(0, len(self) - value)
            for i in xrange(nover):
                self.popitem()
        self._maxlen = value

    maxlen = property(_maxlen_get, _maxlen_set, doc="""\
        The maximum number of mappings stored. Can be changed after
        instantiation. If changed to a smaller capacity, the smallest mappings
        are popped off until the new capacity is reached. A value of ``None``
        indicates unlimited capacity.
        """)

    def _sortkey_get(self):
        return self._sortkey
    
    def _sortkey_set(self, value):
        if self._sortkey == value:
            return
        self._sortkey = value
        if self._maxlen is not None:
            self._reheapify()

    sortkey = property(_sortkey_get, _sortkey_set, doc="""\
        The function called on mapping values to determine their sort order.
        A value of ``None`` indicates the values themselves are used. If
        changed after instantiation, the underlying sort order is updated
        accordingly.
        """)

    def clear(self):
        del self._heap[:]
        obsdict.clear(self)
    
    def copy(self):
        """
        Returns a shallow copy.
        """
        return self.__class__(self._maxlen, self._sortkey, self)

    def _onlyifmaxlen(method):
        """
        Decorator for dict functions which nldict overrides only if its maxlen
        is not None.
        """
        @wraps(method, ('__name__', '__doc__'))
        def wrapper(self, *args, **kwds):
            if self._maxlen is not None:
                return method(self, *args, **kwds)
            return getattr(obsdict, method.__name__)(self, *args, **kwds)
        return wrapper

    @_onlyifmaxlen
    def __setitem__(self, key, value):
        cmpval = self._sortkey(value) if self._sortkey else value
        heapitem = (cmpval, key)
        if len(self) < self._maxlen:
            heappush(self._heap, heapitem)
            obsdict.__setitem__(self, key, value)
        elif cmpval > self._heap[0][0]:
            removed = heapreplace(self._heap, heapitem)
            obsdict.__delitem__(self, removed[1])
            obsdict.__setitem__(self, key, value)

    @_onlyifmaxlen
    def __delitem__(self, key):
        """
        This is not O(1) because we have to traverse the heap to find the item
        to delete and then reheapify!
        """
        value = obsdict.pop(self, key)
        cmpval = self._sortkey(value) if self._sortkey else value
        heapitem = (cmpval, key)
        self._heap.remove(heapitem)
        heapify(self._heap)

    @_onlyifmaxlen
    def popitem(self):
        """
        Removes and returns the (key, value) pair with smallest sorted value
        if available.
        """
        if not self:
            raise KeyError
        removed = heappop(self._heap)
        key = removed[1]
        value = obsdict.pop(self, key)
        return key, value

    __iter__ = obsdict.__iter__

    # Methods with indirect access via the above methods

    setdefault = MutableMapping.setdefault
    update = MutableMapping.update
    pop = MutableMapping.pop
    keys = MutableMapping.keys
    values = MutableMapping.values
    items = MutableMapping.items

    def __repr__(self):
        pairs = ', '.join(map('%r: %r'.__mod__, self.items()))
        return '%s(maxlen=%r, sortkey=%r, {%s})' % (self.__class__.__name__,
            self._maxlen, self._sortkey, pairs)
    __str__ = __repr__

    @classmethod
    def fromkeys(cls, maxlen, sortkey, iterable, value=None):
        return cls(maxlen, sortkey, izip(iterable, repeat(value)))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
