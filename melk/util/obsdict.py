from functools import wraps


class obsdict(dict):
    """
    Observable dict class. Observers can implement callbacks in ``callbackmap``
    to be notified of various events.

    Example::

        >>> class Logger(object):
        ...     @staticmethod
        ...     def mapping_set(map, key, val):
        ...         print 'set %r -> %r on %r' % (key, val, map)
        ...
        ...     @staticmethod
        ...     def mapping_deleted(map, key):
        ...         print 'deleted %r from %r' % (key, map)
        ...
        >>> l = Logger()
        >>> d = obsdict()
        >>> d.observers.append(l)
        >>> d['foo'] = 'bar'
        set 'foo' -> 'bar' on obsdict({'foo': 'bar'}) at 0x...
        >>> del d['foo']
        deleted 'foo' from obsdict({}) at 0x...
    """
    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)
        self._observers = []

    def __str__(self):
        return '%s({%s})' % (self.__class__.__name__,
            ', '.join(('%r: %r' % (k, v) for (k, v) in self.iteritems())))

    def __repr__(self):
        return '%s at %s' % (self, hex(id(self)))

    @property
    def observers(self):
        """
        Read-only access to :attr:`_obs`. With the guarantee that the
        underlying list object will not change, clients can add or remove
        observers from it across multiple threads without issue.
        """
        return self._observers

    callbackmap = {
        '__setitem__': 'mapping_set',
        '__delitem__': 'mapping_deleted',
        }
    """
    maps method names to names of callback functions that will be called
    on observers after the method name is called.
    """

    def _notify(method, callbackname):
        @wraps(method, ('__name__', '__doc__'))
        def wrapper(self, *args, **kwds):
            result = method(self, *args, **kwds)
            for o in self._observers:
                try:
                    callback = getattr(o, callbackname)
                except AttributeError:
                    pass
                else:
                    callback(self, *args, **kwds)
            return result
        return wrapper

    for methodname in callbackmap:
        locals()[methodname] = _notify(getattr(dict, methodname), callbackmap[methodname])


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
