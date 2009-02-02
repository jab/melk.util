try:
    from xml.etree import ElementTree as etree
except ImportError:
    # python < 2.5
    from elementtree import ElementTree as etree

def feeds_in_opml(opml_data, titles=False):
    """
    accepts a string containing the xml form of an OPML file
    returns a flat list of feed URLs referenced by the OPML
    regardless of OPML structure.
    
    if titles is True, returns a list of tuples, (url, title)
    containing the title specified for the feed in the opml.
    """

    opml = etree.XML(opml_data)
    urls = []
    #for node in opml.xpath('//outline[@type="rss"]'):
    for node in opml.getiterator('outline'):
        if node.get('type', '').lower() == 'rss':
            url= node.get('xmlUrl', None)
            if url is not None:
                if titles is False:
                    urls.append(url)
                else:
                    urls.append((url, node.get('title', '')))
    return urls

    
def dump_opml(feed_urls, title=None, feed_titles=None):
    """
    Serializes a list of feed URLs in OPML format,
    returns opml string
    """
    if feed_titles is None:
        feed_titles = {}
    
    root = etree.Element("opml", version="1.0")
    head = etree.Element("head")
    root.append(head)

    if title is not None:
        title = etree.Element("title")
        title.text = title
        head.append(title)

    body = etree.Element("body")
    root.append(body)

    for url in feed_urls:
        attrs = {}
        attrs['xmlUrl'] = url
        attrs['type'] = 'rss'
        
        if url in feed_titles:
            attrs['title'] = feed_titles[url]

        body.append(etree.Element("outline", **attrs))

    return etree.tostring(root)