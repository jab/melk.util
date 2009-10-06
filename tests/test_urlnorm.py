
OK_HOSTS = [        
 '0.0.0.0',
 '127.127.127.127',
 '255.255.255.255',
 '127.127.127.127:0',
 '127.127.127.127:80',
 '127.127.127.127:65535',
 'www.slashdot.org',
 'www.slashdot.org:80',
 '.'.join(['w'*63, 'x'*63, 'y'*63, 'z'*60, 'cz']),
 '.'.join(['w'*63, 'x'*63, 'y'*63, 'z'*60, 'cz']) + ':4453',
]

BAD_HOSTS = [
'256.127.127.127',
'127.256.127.127',
'127.127.256.127',
'127.127.127.256',
'_foo.example.org',
'foo_.example.org',
'x'*64 + '.example.org',
'.'.join(['w'*63, 'x'*63, 'y'*63, 'z'*60, 'com']),
]    

def test_is_host():
    from melk.util.urlnorm import is_host
    for host in OK_HOSTS:
        assert is_host(host), host
    for host in BAD_HOSTS:
        assert not is_host(host), host

OK_SCHEMES = ['http', 'HtTp', 'https', 'HTTPS']
BAD_SCHEMES = ['', 'ftp', 'gopher', 'melk']
def test_is_http_url():
    from melk.util.urlnorm import is_http_url

    for host in OK_HOSTS:
        assert not is_http_url(host)

        for scheme in OK_SCHEMES:
            assert is_http_url(scheme + '://' + host)
        
        for scheme in BAD_SCHEMES:
            assert not is_http_url(scheme + '://' + host)

    for host in BAD_HOSTS:
        assert not is_http_url(host)
        for scheme in OK_SCHEMES:
            assert not is_http_url(scheme + '://' + host)
        for scheme in BAD_SCHEMES:
            assert not is_http_url(scheme + '://' + host)

def test_doctests():
    """
    run the doctests from the module.
    """
    import doctest
    from melk.util import urlnorm
    doctest.testmod(urlnorm, raise_on_error=True)