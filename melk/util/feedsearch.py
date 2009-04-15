"""
This module implements a few ways of searching for feeds. They look like this:

>>> from melk.util import feedsearch
>>> searcher = feedsearch.GoogleFeedSearchService()
>>> rs = searcher.find_feeds("new york times")
>>> rs[0]
{'url': u'http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml', 'link': u'http://www.nytimes.com/', 'title': u'The <b>New York Times</b> - Breaking News, World News &amp; Multimedia'}
>>> searcher.is_feed(rs[0].url)
True
>>> searcher.is_feed(rs[0].link)
False

"""

from formencode import Invalid
from formencode.validators import URL
from melk.util.dibject import Dibject, json_wake
from melk.util.http import NoKeepaliveHttp as Http, ForbiddenUrlError
import urllib
import traceback

import logging 
log = logging.getLogger(__name__)

__all__ = ['GoogleFeedSearchService', 'HandScrapedFeedSearchService', 'ChainedFeedSearchService']

FIND_FEED  = "http://ajax.googleapis.com/ajax/services/feed/find?v=1.0&q="
LOAD_FEED  = "http://ajax.googleapis.com/ajax/services/feed/load?v=1.0&q="

class GoogleFeedSearchService(object):
    """
    This class provides a simple feed searching service based on 
    google APIs.  You can query by keywords, urls of web pages linking
    to feeds or direct urls to feeds.
    
    It is a very fast path for common feeds, but *not comprehensive*.
    
    If you want to support small-fry feeds that have not been discovered by google, 
    consider chaining this together with the HandScrapedFeedSearchService as 
    a fallback.
    """

    def __init__(self, service_key=None, http_cache=None):
        self._service_key = service_key
        self._http_cache = http_cache
        self._as_url = URL(add_http=True)
        self._http_client = Http(cache=self._http_cache, timeout=5)

    def find_feeds(self, query, max_results=5):
        try:
            rs = self._find_feeds(query)
            rs = uniquify_results(rs)
            return rs[0:max_results]
        except:
            log.error("Error searching for feeds. query=%s: %s" % (query, traceback.format_exc()))
            return []

    def _find_feeds(self, query):
        # firstly, could this be a url? if so, let's try that...
        try:
            url = self._as_url.to_python(query)
            rs = self._search_url_any(url)
            if len(rs) > 0:
                return rs
        except Invalid:
            # nope, let's move on...
            pass

        # try searching terms...
        try:
            return self._search_terms(query)
        except:
            return []

    def is_feed(self, url):
        """
        test whether there is a feed at the url specified.
        (not referred to in the page specified, actually there)
        """
        return self._load_feed(url) is not None

    def _search_terms(self, query):
        rs = self._query(FIND_FEED, query)
        if rs is not None:
            return [Dibject(url=r["url"],
                            title=r.get('title', ''),
                            link=r.get('link', ''))
                    for r in rs.entries]
        else:
            return []

    def _load_feed(self, url):
        rs = self._query(LOAD_FEED, url)
        if rs is None:
            return None

        return Dibject(url=url,
                       title=rs.feed.get('title', ''),
                       link=rs.feed.get('link', ''))


    def _search_url_any(self, url):
        # okay, well this could be the url of a feed or 
        # it could be a web page that has a feed link in 
        # it...
        
        # try searching it as a web page first...
        rs = self._search_terms('site:%s' % url)
        if len(rs) > 0:
            return rs
        
        # hmm didn't seem to find anything, but it may be the 
        # actual url of a feed...
        rs = self._load_feed(url)
        if rs is not None:
            return [rs]
        else:
            return []
            

    def _query(self, service, q):
        query_url = service
        query_url += urllib.quote_plus(q)
        if self._service_key:
            query_url += "&key=%s" % self._service_key

        log.debug("Issuing query %s" % query_url)
        result = self._http_client.request(query_url, 'GET')
        if result is None:
            log.error("No response to query %s" % query_url)
            return None

        response, content = result
        log.debug("response was: %s, %s" % (response, content))
        
        if response.status != 200:
            log.error("Error response to %s: (%s, %s)" % (query_url, response, content))
            return None

        rr = json_wake(content)
        if not hasattr(rr, 'responseData'):
            return None
        return rr.responseData
        
from BeautifulSoup import BeautifulSoup as SoupHTML
import feedparser
import urlparse
DEFINITE_FEED_CONTENT_TYPES = ['application/atom+xml', 'application/rss+xml', 'application/rdf+xml']
DEFINITE_HTML_CONTENT_TYPES = ['text/html', 'application/xhtml+xml']
AMBIGUOUS_XML_CONTENT_TYPES = ['text/xml', 'application/xml']

class HandScrapedFeedSearchService(object):
    """
    This is a slow path hand scraper / checker feed search. It does not 
    handle keyword searches, only urls which it laboriously fetches and 
    inspects.  If there is a feed to be found, it will try pretty hard
    (at the expense of time) to prove it.
    """

    def __init__(self, http_cache=None):
        self._http_cache = http_cache
        self._as_url = URL(add_http=True)
        self._http_client = Http(cache=self._http_cache, timeout=5)
        
    def find_feeds(self, query, max_results=5):
        try:
            rs = self._find_feeds(query)
            rs = uniquify_results(rs)
            return rs[0:max_results]
        except:
            log.error("Error finding feeds in %s, %s" % (query, traceback.format_exc()))
            return []
            
    def _find_feeds(self, query):
        try:
            url = self._as_url.to_python(query)
        except Invalid:
            return []
            
        rs = self._search_url(url)
        if len(rs) > 0:
            return rs
        else:
            return []

    def is_feed(self, url):
        try:
            ff, response, content = self._check_for_feed(url)
            return ff is not None
        except:
            log.error("Error determining existence of feed %s: %s" % (url, traceback.format_exc()))

    def _search_url(self, url):
        feeds = []
        try:
            # check to see if the URL points to a feed
            ff, response, content = self._check_for_feed(url)
                
            if ff is not None:
                return [ff]
                
            if response is None or content is None:
                return []

            # dig feed links out...
            ct = get_content_type(response.get('content-type', '')).lower()
            if ct in DEFINITE_HTML_CONTENT_TYPES or ct in AMBIGUOUS_XML_CONTENT_TYPES:
                try:
                    feed_urls = self._find_feed_links(content)
                except:
                    log.error("Error scraping feed links from %s: %s" % (url, traceback.format_exc()))
                else:
                    for furl in feed_urls:
                        # mm make sure it's not relative...
                        furl = urlparse.urljoin(url, furl)
                        ff, response, content = self._check_for_feed(furl)
                        if ff is not None:
                            feeds.append(ff)
            return feeds
        except ForbiddenUrlError, e:
            log.warn(e)
            return []
        except:
            log.error("Error locating feeds in %s:\n%s" % (url, traceback.format_exc()))
            return feeds

    def _check_for_feed(self, url):
        result = self._http_client.request(url, "GET")
        if result is None:
            return None, None, None
        response, content = result
        ct = get_content_type(response.get('content-type', '')).lower()
        if ((response.status == 200 or response.status == 304) and 
            (ct in DEFINITE_FEED_CONTENT_TYPES or ct in AMBIGUOUS_XML_CONTENT_TYPES)):
            # try to parse the page as a feed
            ff = feedparser.parse(content, url)
            if ff and 'feed' in ff and 'bozo_exception' not in ff:
                rf = Dibject(url=url, title= ff['feed'].get('title', 'Untitled Feed'), link='')
                return rf, response, content
        return None, response, content

    def _find_feed_links(self, html):       
        feed_links = []
        # try parsing it as HTML and searching for feeds
        soup = SoupHTML(html)
        for node in soup.findAll('link'):
            href = node.get('href', None)
            if href:
                rel_type = node.get('type', '').lower()
                if rel_type in DEFINITE_FEED_CONTENT_TYPES:
                    feed_links.append(href)
        return feed_links
        
        
def get_content_type(ct):
    if ';' in ct:
        ct = ct[0:ct.find(';')].strip()
    return ct

def uniquify_results(results):
    """
    make sure we only give back 1 result per feed url
    """
    seen_urls = set()
    rsout = []
    for r in results:
        url = r.url.lower().strip()
        if url in seen_urls:
            continue
        seen_urls.add(url)
        rsout.append(r)
    return rsout
        
class ChainedFeedSearchService(object):
    def __init__(self, services):
        self._services = services
        
    def find_feeds(self, query):
        for service in self._services:
            rs = service.find_feeds(query)
            if len(rs) > 0:
                return rs
        
    def is_feed(self, url):
        for service in self._services:
            if service.is_feed(url):
                return True
        return False
