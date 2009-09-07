

def test_doctests():
    """
    run the doctests from the module.
    """
    import doctest
    from melk.util import urlnorm
    doctest.testmod(urlnorm, raise_on_error=True)