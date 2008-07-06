from melk.util.idict import idict


def test_idict():
    foo = idict()
    foo['bar'] = 'quux'
    assert len(foo) == 1
    
    assert foo['bar'] == 'quux'
    assert foo['BaR'] == 'quux'

    assert 'bar' in foo
    assert foo.has_key('bar')
    assert 'bAr' in foo
    assert foo.has_key('bAr')
    assert not 'buhloney' in foo
    assert not foo.has_key('bahloney')
    
    foo['BaR'] = 'baz'
    assert len(foo) == 1
    assert 'bar' in foo
    assert foo.has_key('bar')
    assert foo['bar'] == 'baz'
    
    del foo['BaR']
    assert not 'bar' in foo
    assert not foo.has_key('bar')
    assert not 'BaR' in foo
    assert not foo.has_key('BaR')


def test_idict_init_kw():
    foo = idict(Bar='quux', bAz='zoom')
    assert 'bar' in foo
    assert foo.has_key('bar')
    assert foo['bar'] == 'quux'
    assert foo['BaR'] == 'quux'
    
    assert 'baz' in foo
    assert foo.has_key('baz')
    assert foo['baz'] == 'zoom'
    assert foo['BaZ'] == 'zoom'

def test_idict_tuple_construct():
    foo = idict([('a', 'b'), ('C', 'd')])
    assert 'a' in foo
    assert foo.has_key('a')
    assert 'A' in foo
    assert foo.has_key('A')
    assert 'c' in foo
    assert foo.has_key('c')
    assert 'C' in foo
    assert foo.has_key('C')

def test_idict_tuple_update():
    foo = idict()
    foo.update([('a', 'b'), ('C', 'd')])
    assert 'a' in foo
    assert 'A' in foo
    assert 'c' in foo
    assert 'C' in foo

    
def test_idict_new_norm():
    
    class Prefix4(str):
        def __hash__(self):
            return hash(self[0:4])

        def __eq__(self, other):
            return self[0:4] == other[0:4]

    class PrefixDict(idict):
        def __init__(self, *args, **kwargs):
            self.Norm = Prefix4
            idict.__init__(self, *args, **kwargs)
        
    pd = PrefixDict()
    pd['foobia'] = 'bar'
    assert 'foobia' in pd
    assert 'foobarar' in pd
    assert pd['foobsrushinwherebarsfeartotread'] == 'bar'
