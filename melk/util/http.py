from httplib2 import Http as HttpBase
from socket import gethostbyname
from urlparse import urlparse
import logging

log = logging.getLogger(__name__)

class ForbiddenUrlError(Exception):
    """
    raised when e.g. trying to fetch a resource from a forbidden host
    """
    pass

class NoKeepaliveHttp(HttpBase): 
    """
    this is an httplib2 http that does not 
    keep connections dangling around
    """

    def __init__(self, *args, **kwargs):
        HttpBase.__init__(self, *args, **kwargs)

    def request(self, *args, **kwargs):
        url = args[0]
        hostname = urlparse(url).hostname
        if gethostbyname(hostname) == gethostbyname('localhost'):
            raise ForbiddenUrlError('requests to localhost are forbidden: %s' % url)

        try:
            return HttpBase.request(self, *args, **kwargs) 
        finally:
            self._close_everything()
    
    def _close_everything(self):
        for conn in self.connections.values():
            conn.close()
        self.connections = {}
