from melk.util.factory import BasicObjectURIFactory


def test_object_uri_factory_basic():
    foo_uri = 'http://www.example.org/foo?quux=baz'
    bar_uri = 'http://www.example.org/bar?quux=bazoo'
    baz_uri = 'http://www.example.org/baz'
    
    class Foo:
        def __init__(self, quux):
            self.quux = quux
            
    class Bar:
        def __init__(self, quux):
            self.quux = quux
    
    class Baz:
        def __init__(self):
            pass
            
    factory = BasicObjectURIFactory()
    factory.register(foo_uri, Foo)
    factory.register(bar_uri, Bar)
    factory.register(baz_uri, Baz)
    
    foo_ob = factory.create_from_uri(foo_uri) 
    assert(foo_ob.__class__ == Foo)
    assert(foo_ob.quux == u'baz')
    
    bar_ob = factory.create_from_uri(bar_uri) 
    assert(bar_ob.__class__ == Bar)
    assert(bar_ob.quux == u'bazoo')
    
    baz_ob = factory.create_from_uri(baz_uri) 
    assert(baz_ob.__class__ == Baz)