from melk.util.hash import melk_id

def test_melk_id_unicode():
    ustr = u'http://feeds.wired.com/wired/\xff\xff\xff\xffhttp://blog.wired.com/defense/2009/01/inside-israels.html'
    mid = melk_id(ustr)

