from melk.util.objecturi import normalize_object_uri as norm_u
from melk.util.objecturi import parse_object_uri as parse_u
from melk.util.objecturi import make_object_uri as make_u




def basic_check_uri(uri):
    nu = norm_u(uri)

    # idempotent 
    assert nu == norm_u(nu)

    # parsable 
    base_uri, qargs = parse_u(uri)

    # reconstructable
    assert nu == make_u(base_uri, qargs), '%s != %s' % (nu, make_u(base_uri, qargs))


def check_config(cfg):
    uri = make_u('http://www.exmaple.com/foo/bar', cfg)
    basic_check_uri(uri)

    b, qa = parse_u(uri)
    for k in cfg:
        assert k in qa
        assert qa[k] == cfg[k], '%s != %s' % (qa[k], cfg[k])
    
def test_lists(): 
    cfg = {
        'abc' : ['apple juice','banana creme pie','chocolate upsidedown cake'],
        'def' : 'value'
        }
    check_config(cfg)
    

def test_embedded_url():
    cfg = {
        'source': 'http://www.example.org/Foo/bar/quux?abc=def',
        'abc': 'def'
        }
    check_config(cfg)
    
    
def test_nonascii():
    uris = ['http://www.foo.bar.org?def=%c09&abc=%94%96%c03',
            'http://www.foo.bar.org?def=%c09&abc=%94%96%c03&def=somethingelse',
            u'http://www.foo.bar.org?def=%c09&abc=%94%96%c03',
            u'http://www.foo.bar.org?def=%c09&abc=%94%96%c03&def=somethingelse']

    for uri in uris:
        basic_check_uri(uri)
