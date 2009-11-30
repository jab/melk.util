class obsdict(dict):
    """
    Extend built-in ``dict`` to implement the observer pattern.

    Observers can implement the callbacks ``mapping_set`` and
    ``mapping_deleted`` to be notified of the corresponding events.

    Example::

        >>> class Logger(object):
        ...     @staticmethod
        ...     def mapping_set(map, key, val):
        ...         print 'set %r -> %r on %r' % (key, val, map)
        ...
        ...     @staticmethod
        ...     def mapping_deleted(map, key, val):
        ...         print 'deleted %r -> %r from %r' % (key, val, map)
        ...
        >>> l = Logger()
        >>> d = obsdict()
        >>> d.observers.append(l)
        >>> d['foo'] = 'bar'
        set 'foo' -> 'bar' on obsdict({...}) at 0x...
        >>> d['foo'] = 'baz'
        deleted 'foo' -> 'bar' from obsdict({...}) at 0x...
        set 'foo' -> 'baz' on obsdict({...}) at 0x...
        >>> del d['foo']
        deleted 'foo' -> 'baz' from obsdict({...}) at 0x...
        >>> d.update(one=1, two=2)
        set 'two' -> 2 on obsdict({...}) at 0x...
        set 'one' -> 1 on obsdict({...}) at 0x...
        >>> d.pop('one')
        deleted 'one' -> 1 from obsdict({...}) at 0x...
        1
        >>> d.popitem()
        deleted 'two' -> 2 from obsdict({...}) at 0x...
        ('two', 2)
        >>> d['foo'] = 'bar'
        set 'foo' -> 'bar' on obsdict({...}) at 0x...
        >>> d.clear()
        deleted 'foo' -> 'bar' from obsdict({...}) at 0x...
    """
    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)
        self._observers = []

    @property
    def observers(self):
        """
        Read-only access to :attr:`_obs`. With the guarantee that the
        underlying list object will not change, clients can add or remove
        observers from it across multiple threads without issue.
        """
        return self._observers

    ## XXX locking?

    def _notify(self, callbackname, *args, **kwds):
        for o in self._observers:
            try:
                callback = getattr(o, callbackname)
            except AttributeError:
                pass
            else:
                callback(self, *args, **kwds)

    def __delitem__(self, key):
        val = self[key]
        dict.__delitem__(self, key)
        self._notify('mapping_deleted', key, val)

    def pop(self, key):
        val = dict.pop(self, key)
        self._notify('mapping_deleted', key, val)
        return val

    def popitem(self):
        key, val = dict.popitem(self)
        self._notify('mapping_deleted', key, val)
        return key, val

    def clear(self):
        for key, val in self.iteritems():
            self._notify('mapping_deleted', key, val)
        dict.clear(self)
    
    def __setitem__(self, key, val):
        try:
            oldval = self[key]
        except KeyError:
            pass
        else:
            self._notify('mapping_deleted', key, oldval)
        dict.__setitem__(self, key, val)
        self._notify('mapping_set', key, val)

    def update(self, *args, **kwds):
        for k, v in dict(*args, **kwds).iteritems():
            try:
                oldv = self[k]
            except KeyError:
                pass
            else:
                self._notify('mapping_deleted', k, oldv)
            self._notify('mapping_set', k, v)
        dict.update(self, *args, **kwds)

    def __str__(self):
        return '%s({%s})' % (self.__class__.__name__,
            ', '.join(('%r: %r' % (k, v) for (k, v) in self.iteritems())))

    def __repr__(self):
        return '%s at %s' % (self, hex(id(self)))


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
