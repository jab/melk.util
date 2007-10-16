import logging 
from threading import Thread 
import httplib2 
from melk.util.taskqueue import TaskQueue as Queue 
from melk.util.threadpool import ThreadPool
import traceback 

log = logging.getLogger(__name__)


class SpiderResult: 
    def __init__(self, url, response, content):
        self.url = url
        self.response = response
        self.content = content

class Spider(ThreadPool):
    """
    fetches urls in input_queue and puts 
    SpiderResults in output_queue
    """

    def __init__(self,
                 cache=None, 
                 timeout=60,
                 poolsize=10,
                 output_changed_only=True,
                 output_queue=None):
        """
        @param cache a folder to use as a cache or an httplib2 cache
        @param poolsize number of worker threads to use for fetching
        @param output_changed_only only put modified content on the 
               output queue (requires cache)
         @param output_queue optional Queue to put output in
        """
        ThreadPool.__init__(self, poolsize=poolsize)

        self._cache = cache
        self._timeout = timeout
        self._output_changed_only = output_changed_only
              
        if output_queue is None:
            self.output_queue = Queue()
        else:
            self.output_queue = output_queue

    def _fetch(self, url, http_client):
        log.info("fetching %s" % url)

        response, content = http_client.request(url, "GET")

        if response.fromcache:
            log.info("%s unchanged" % url)
            if self._output_changed_only:
                return 

        if response.status == 200:
            log.info("%s updated" % url)
            self.output_queue.put(SpiderResult(url, response, content))
        else:
            log.info("status of %s was %d" % (url, response.status))
                
        
    def _worker(self): 
        http_client = httplib2.Http(cache=self._cache, 
                                    timeout=self._timeout)
        while(True):
            try:
                url = self.input_queue.get()
                try:
                    self._fetch(url, http_client)
                finally:
                    self.input_queue.task_done()
            except:
                log.error(traceback.format_exc())
