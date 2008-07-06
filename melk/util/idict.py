from melk.util.typecheck import is_listy

class _istr(str):
    """
    a string that compares and hashes case insensitively 
    """
    def __hash__(self):
        return hash(self.lower())

    def __eq__(self, other):
        return self.lower() == other.lower()

class idict(dict):
    """
    A normalization insensitive dictionary type based on a post from the python mailing list
    http://mail.python.org/pipermail/python-list/2005-April/315600.html
    and a comment in: 
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66315
    
    by default, this is a case insensitive dictionary with string keys
    """

    def __init__(self, dict=None, **kwargs):
        """
        tries to stick pretty close to dictionary interface, accepts another 
        dictionary-type thing, keyword arguments or a list of 2-tuples...
        """
        # set this class in subclasses before calling this initializer if
        # override behavior is desired...
        if not hasattr(self, 'Norm'):
            self.Norm = _istr
        self.update(dict, **kwargs)
            
    def __setitem__(self, key, value):
        dict.__setitem__(self, self.Norm(key), value)
    def __getitem__(self, key):
        return dict.__getitem__(self, self.Norm(key))
    def __contains__(self, key):
        return dict.__contains__(self, self.Norm(key))
    def __delitem__(self, key):
        return dict.__delitem__(self, self.Norm(key))
    def has_key(self, key):
        return dict.has_key(self, self.Norm(key))
    def get(self, key, def_val=None):
        return dict.get(self, self.Norm(key), def_val)
    def pop(self, key, def_val=None):
        return dict.pop(self, self.Norm(key), def_val)
    def setdefault(self, key, def_val=None):
        return dict.setdefault(self, self.Norm(key), def_val)
    def fromkeys(self, iterable, value=None):
        d = self.__class__()
        for k in iterable:
            d[k] = value
        return d

    def update(self, dict=None, **kwargs):
        if dict is None:
            pass
        elif hasattr(dict, 'items'):
            for k, v in dict.items():
                self[k] = v
        else:
            for k,v in dict:
                self[k] = v

        if len(kwargs):
            for k, v in kwargs.items():
                self[k] = v