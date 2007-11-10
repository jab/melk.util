import urlparse
import urllib
import cgi


# XXX hrm just make a class here? 

"""
Normalization: 

* path parameters are dropped
* fragments are dropped
* lower cased 'host', 'scheme'
* arguments are sorted by key, then value 

eg:

>>> from melk.util.objecturi import normalize_object_uri as norm
>>> uri = "hTtp://joe:blow@www.ExAmplE.org:9374/objects/author?name=Joe%20Schmoe&email=foo%40example.org&name=Jim%40Jones"
>>> norm(uri)
'http://joe:blow@www.example.org:9374/objects/author?email=foo%40example.org&name=Jim%40Jones&name=Joe%20Schmoe'
"""

def uri_escape(value):
    return urllib.quote_plus(value)


def normalize_object_uri(object_uri): 
    """
    normalizes a object uri so that it can 
    be compared directly to another normalized
    object_uri for equality as strings.
    """

    uri_parts = urlparse.urlsplit(object_uri)
    
    # parse the query string
    query_args = cgi.parse_qs(uri_parts[3], keep_blank_values=True)

    new_query = ''
    # put it back together, but sorted
    for key in sorted(query_args.keys()):
        for val in sorted(query_args[key]):
            new_query += "&%s=%s" % (urllib.quote(key), urllib.quote(val))
    
    if len(new_query) > 0:
        new_query = new_query[1:]
    

    return urlparse.urlunsplit([uri_parts[0], 
                                uri_parts[1].lower(),
                                uri_parts[2],
                                new_query,
                                ''])

def parse_object_uri(object_uri): 
    """
    returns base uri and dictionary of 
    query arguments  
    """
    object_uri = normalize_object_uri(object_uri)

    uri_parts = urlparse.urlsplit(object_uri)
    base_uri = urlparse.urlunsplit(list(uri_parts[0:3]) + ['',''])

    query_args = cgi.parse_qs(uri_parts[3], keep_blank_values=True)
    
    args = {}
    for arg in query_args:
        if len(query_args[arg]) == 1:
            args[arg] = query_args[arg][0]
        else:
            args[arg] = list(query_args[arg])

    return base_uri, args


def _make_arg(k, v): 
    arg = uri_escape(k)
    if v:
        arg += "=%s" % uri_escape(v)
    arg += "&"
    return arg


def make_object_uri(base_uri, cfg):
    uri = base_uri + "?"

    if cfg and len(cfg) > 0:
        for k in cfg.keys():
            uri += _make_arg(k, cfg[k])

    return normalize_object_uri(uri)
