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
from melk.util.threadpool import ThreadPool
import traceback 

log = logging.getLogger(__name__)


class SpiderJob:
    def __init__(self, url, **kw):
        """
        construct a job that fetches a specific url. 
        url - the url to fetch. 

        All additional keyword arguments may be used to customize 
        the Http constructor if necessary.  These will only be used
        if no http_client is specified to __call__.
        """
        self.url = url
        self.http_args = dict(kw)

    def __call__(self, http_client=None):
        log.debug("fetching %s..." % self.url)
        if http_client is None:
            http_client = DefaultHttp(**self.http_args)

        response, content = http_client.request(self.url, "GET")
        log.debug("%s -> %s fromcache=%s" % (self.url, response.status, response.fromcache))
        return SpiderResult(self.url, response, content)

class SpiderResult: 
    def __init__(self, url, response=None, content=None):
        self.url = url
        self.response = response
        self.content = content

class Spider(ThreadPool):
    """
    fetches urls specified as SpiderJobs to the input_queue and places
    SpiderResults in output_queue (if provided)
    """

    def __init__(self, cache=None, **kw):
        """
        @param cache a folder to use as a cache or an httplib2 cache
        """
        ThreadPool.__init__(self, **kw)

        self._cache = cache

    def _do(self, job):
        return job(self._get_http_client()) 

    def _get_http_client(self):
        # this is implemented as a thread local
        if not hasattr(self._local, 'http_client'):
            self._local.http_client = self._make_http_client()
        return self._local.http_client

    def _make_http_client(self):
        """
        override to customize http clients used.
        """
        return DefaultHttp(cache=self._cache)

DEFAULT_HTTP_ARGS = {
    'timeout': 15
}

def DefaultHttp(**kw):
    ctor_args = dict(DEFAULT_HTTP_ARGS)
    ctor_args.update(kw)
    h = Http(**ctor_args)
    h.force_exception_to_status_code = True
    return h