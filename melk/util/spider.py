import logging 
import threading
from threading import Thread 
import httplib2 
from melk.util.taskqueue import TaskQueue as Queue 
from melk.util.threadpool import ThreadPool, OutputQueueMixin
import traceback 

log = logging.getLogger(__name__)

class SpiderJob:
    def __init__(self, url): 
        self.url = url

class SpiderResult: 
    def __init__(self, url, response, content):
        self.url = url
        self.response = response
        self.content = content


class Spider(ThreadPool, OutputQueueMixin):
    """
    fetches urls specified as SpiderJobs to 
    the input_queue and places
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
         @param output_queue optional Queue to put output into
        """
        ThreadPool.__init__(self, poolsize=poolsize)
        OutputQueueMixin.__init__(self, output_queue)

        self._cache = cache
        self._timeout = timeout
        self._output_changed_only = output_changed_only      

    def _do(self, job): 
        http_client = self._get_http_client()
        self._fetch(job.url, http_client) 


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
 
    def _get_http_client(self):
        # currently this is implemented as a thread local
        if not hasattr(self._local, 'http_client'):
            self._local.http_client = httplib2.Http(cache=self._cache, 
                                                   timeout=self._timeout)
        return self._local.http_client
