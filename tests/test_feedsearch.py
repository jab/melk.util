import logging 
import sys
# log = logging.getLogger('melk.util.feedsearch')
# log.setLevel(logging.DEBUG)
# log.addHandler(logging.StreamHandler(sys.stderr))


def test_feedsearch():

    def _check(fs, term, feed):
        assert not fs.is_feed(term)
        assert fs.is_feed(feed)

        rs = fs.find_feeds(term)
        found = False
        for r in rs:
            if r.url == feed:
                found = True
                break
        assert found, "Search failed: term: %s, rs: %s, expected: %s" % (term, rs, feed)

    from melk.util.feedsearch import GoogleFeedSearchService, HandScrapedFeedSearchService, ChainedFeedSearchService
    
    gs = GoogleFeedSearchService()
    hs = HandScrapedFeedSearchService()
    chained = ChainedFeedSearchService([gs, hs])

    assert not gs.is_feed('flume')
    assert not hs.is_feed('flume')
    assert not chained.is_feed('flume')

    url_tests = [('http://www.slashdot.org', 'http://rss.slashdot.org/Slashdot/slashdot'), ]

    query_tests = [('http://www.boingboing.net', 'http://feeds.boingboing.net/boingboing/iBag'),
                   ('slashdot', 'http://rss.slashdot.org/Slashdot/slashdot'), ]
    
    for term, feed in url_tests:
        yield _check, gs, term, feed
        yield _check, hs, term, feed
        yield _check, chained, term, feed

    # these only work with the googler
    for term, feed in query_tests:
        yield _check, gs, term, feed