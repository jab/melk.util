from httplib2 import Http as HttpBase



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
        finally:
            self._close_everything()
    
    def _close_everything(self):
        for k, conn in self.connections.items():
                conn.close()
        self.connections = {}
