from httplib2 import Http as HttpBase
import logging

log = logging.getLogger(__name__)


class NoKeepaliveHttp(HttpBase): 
    """
    this is an httplib2 http that does not 
    keep connections dangling around
    """

    def __init__(self, *args, **kwargs):
        HttpBase.__init__(self, *args, **kwargs)

    def request(self, *args, **kwargs):
        try:
            return HttpBase.request(self, *args, **kwargs) 
        except Exception, e:
            log.error("Error making request: %s" % str(e))
        finally:
            self._close_everything()
    
    def _close_everything(self):
        for conn in self.connections.values():
            conn.close()
        self.connections = {}
