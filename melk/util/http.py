from httplib2 import Http as HttpBase
from socket import gethostbyname
from urlparse import urlparse
import logging

log = logging.getLogger(__name__)

class ForbiddenHost(Exception):
    """
    raised when e.g. trying to fetch a resource from a forbidden host
    """
    pass

# XXX this should be renamed as it has added more functionality
class NoKeepaliveHttp(HttpBase): 
    """
    This is an httplib2 http that does not keep connections dangling around.
    Its constructor also accepts a 'blacklist' kwarg in which a list of
    blacklisted hosts can be passed.
    """

    def __init__(self, *args, **kwargs):
        self.blacklist = kwargs.pop('blacklist', ())
        HttpBase.__init__(self, *args, **kwargs)

    def request(self, *args, **kwargs):
        if self.blacklist:
            uri = args[0]
            ip = gethostbyname(urlparse(uri).hostname)
            for badhost in self.blacklist:
                if gethostbyname(badhost) == ip:
                    raise ForbiddenHost('requests to %s are forbidden: %s' % (badhost, uri))

        try:
            return HttpBase.request(self, *args, **kwargs) 
        finally:
            self._close_everything()
    
    def _close_everything(self):
        for conn in self.connections.values():
            conn.close()
        self.connections = {}
