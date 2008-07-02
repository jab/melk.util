from melk.util.opml import feeds_in_opml, dump_opml

def test_opml_parse():

    opml = """<?xml version="1.0" encoding="utf-8"?>
    <opml version="1.1">
    <head>
        <title>Subscriptions</title>
        <dateCreated>Fri, 06 Jul 2007 21:36:50 GMT</dateCreated>
        <ownerName></ownerName>
    </head>
    <body>
       <outline title="ABC Blog" text="abc" htmlUrl="http://www.example.org/blog/abc" type="rss" xmlUrl="http://www.example.org/blog/abc/atom.xml"/>
       <outline title="DEF Blog" text="def" htmlUrl="http://www.example.org/blog/def" type="rss" xmlUrl="http://www.example.org/blog/def/atom.xml"/>
       <outline title="GHI Blog" text="ghi" htmlUrl="http://www.example.org/blog/ghi" type="rss" xmlUrl="http://www.example.org/blog/ghi/atom.xml"/>
    </body>
    </opml>
    """

    expected_feeds = ["http://www.example.org/blog/abc/atom.xml",
                      "http://www.example.org/blog/def/atom.xml",
                      "http://www.example.org/blog/ghi/atom.xml"]
    out_feeds = feeds_in_opml(opml)
    
    assert len(out_feeds) == len(expected_feeds)
    for url in expected_feeds:
        assert url in out_feeds
    
def test_opml_loop():
    in_feeds = ["http://www.abc.com/def", "http://www.foo.bar.org/quux", "http://example.org/feed"]
    out_feeds = feeds_in_opml(dump_opml(in_feeds))
    
    assert len(out_feeds) == len(in_feeds)
    for url in in_feeds:
        assert url in out_feeds