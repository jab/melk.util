# Copyright (C) 2007 The Open Planning Project
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301
# USA

import logging 
import threading
from threading import Thread 
from melk.util.http import NoKeepaliveHttp as Http
from melk.util.taskqueue import TaskQueue as Queue 
from melk.util.threadpool import ThreadPool, OutputQueueMixin, DEFAULT_POOLSIZE
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
                 poolsize=DEFAULT_POOLSIZE,
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
        log.debug("fetching %s" % url)

        result = http_client.request(url, "GET")
        if result is None: # there must have been an error
            return

        response, content = result

        if response.fromcache and self._output_changed_only:
#            log.info("%s unchanged" % url)
            return
        
        if response.status == 200 or (response.status == 304 and not self._output_changed_only):
#            log.info("%s updated" % url)
            self.output_queue.put(SpiderResult(url, response, content))
#        else:
#            log.info("status of %s was %d" % (url, response.status))
 
    def _get_http_client(self):
        # currently this is implemented as a thread local
        if not hasattr(self._local, 'http_client'):
            self._local.http_client = Http(cache=self._cache, 
                                           timeout=self._timeout)
        return self._local.http_client
