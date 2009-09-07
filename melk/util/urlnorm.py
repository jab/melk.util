import re
from urllib import quote_plus, unquote_plus, urlencode
from urlparse import urlsplit, urlunsplit

try:
    # python 2.6
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl
    

def canonical_url(url):
    """
    normalize a url to produce an equivalent canonical representation
    
    - fragment identifier is dropped
    - lower cased 'host', 'scheme'
    - default port is dropped from host (:80)
    - empty query argument is removed
    - empty valued query arguments include = sign
    - spaces are represented by + in path and query
    - unreserved characters in path and query are NOT percent encoded (eg %41 -> A)
    - %xx encoded entities are upcase only (%9b -> %9B) in path and query
    - query arguments are sorted by key, then value
    - trailing slash in path is removed
    - remove dot segments (. or ..) as in RFC3986
    - remove repeated / in path segment

    >>> canonical_url('http://example.org/foo#fragment')
    'http://example.org/foo'
    
    >>> canonical_url('HTtp://Example.ORG/foo/Bar')
    'http://example.org/foo/Bar'

    >>> canonical_url('http://example.org:80/foo/bar')
    'http://example.org/foo/bar'
    
    >>> canonical_url('http://example.org/foo?')
    'http://example.org/foo'

    >>> canonical_url('http://example.org?a')
    'http://example.org?a='

    >>> canonical_url('http://example.org/the%20webbers?are=the%20great')
    'http://example.org/the+webbers?are=the+great'

    >>> canonical_url('http://example.org/%41%42C%44?%45%46=%47%48')
    'http://example.org/ABCD?EF=GH'

    >>> canonical_url('http://example.org/%9a?%9b=%9c')
    'http://example.org/%9A?%9B=%9C'

    >>> canonical_url('http://example.org?B&C=0&C=1&%41=foo')
    'http://example.org?A=foo&B=&C=0&C=1'
    
    >>> canonical_url('http://example.org/foo/bar/?xyz=w')
    'http://example.org/foo/bar?xyz=w'
    
    >>> canonical_url('http://example.org/a/../b/./c')
    'http://example.org/b/c'
    
    >>> canonical_url('http://example.org//a/////b//')
    'http://example.org/a/b'

    >>> canonical_url('HttP://exAmple.org:80////foo/..////bar/?B&%41=%20+%3f#quux')
    'http://example.org/bar?A=++%3F&B='
    """

    # to begin with, if it is a legit url, it should be ascii
    url = url.encode('ascii')
    parts = [x.encode('ascii') for x in urlsplit(url)]

    # downcase hostname
    parts[1] = parts[1].lower()

    # remove default port from host if present
    if re.match('^(.*?):80$', parts[1]):
        parts[1] = parts[1][0:-3]

    # re-encode the path
    path = parts[2].split('/')
    path = [quote_plus(unquote_plus(x)) for x in path]
    parts[2] = '/'.join(path)

    # remove .. and . segments from path 
    parts[2] = remove_dot_segments(parts[2])

    # remove repeated / from path
    parts[2] = re.sub('\/+', '/', parts[2])

    # remove any trailing slash from path
    if parts[2].endswith('/'):
        parts[2] = parts[2][0:-1]


    # parse and re-form the query string in sorted order
    qsparts = parse_qsl(parts[3], keep_blank_values=True)
    qsparts.sort()
    parts[3] = urlencode(qsparts)

    # drop fragment identifier 
    parts[4] = ''

    return urlunsplit(parts)
    
def remove_dot_segments(path):
    """
    algorithm remove_dot_segments from RFC3986, 
    remove . and .. components of a path.
    """
    inp = path
    outp = []

    while len(inp):
        # A.  If the input buffer begins with a prefix of "../" or "./",
        #     then remove that prefix from the input buffer; otherwise        
        if inp.startswith('../') or inp.startswith('./'):
            inp = inp[inp.index('/')+1:]
            continue

        # B.  if the input buffer begins with a prefix of "/./" or "/.",
        #     where "." is a complete path segment, then replace that
        #     prefix with "/" in the input buffer; otherwise,
        if inp.startswith('/./') or inp == '/.':
            inp = inp[2:] or '/'
            continue

        # C.  if the input buffer begins with a prefix of "/../" or "/..",
        #      where ".." is a complete path segment, then replace that
        #      prefix with "/" in the input buffer and remove the last
        #      segment and its preceding "/" (if any) from the output
        #      buffer; otherwise,
        if inp.startswith('/../') or inp == '/..':
            inp = inp[3:] or '/'
            try:
                outp.pop()
            except IndexError:
                pass
            continue

        #  D.  if the input buffer consists only of "." or "..", then remove
        #      that from the input buffer; otherwise,
        if inp == '.' or inp == '..':
            inp = ''
            continue

        #  E.  move the first path segment in the input buffer to the end of
        #      the output buffer, including the initial "/" character (if
        #      any) and any subsequent characters up to, but not including,
        #      the next "/" character or the end of the input buffer.
        seg = ''
        if inp.startswith('/'):
            seg = '/'
            inp = inp[1:]
        seg_end = inp.find('/')
        if seg_end == -1:
            seg += inp
            inp = ''
        else:
            seg += inp[0:seg_end]
            inp = inp[seg_end:]

        outp.append(seg)

    return ''.join(outp)
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()