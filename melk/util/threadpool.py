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

import threading
from threading import Thread
import traceback
from melk.util.taskqueue import TaskQueue as Queue
import logging

log = logging.getLogger(__name__)

DEFAULT_POOLSIZE = 10

class ThreadPool:
    """
    Simple threadpool that processes
    items placed in its input queue. 

    implement the _do method or passed
    as a single argument function 
    to the constructor to specify the
    processing.
    """

    def __init__(self, poolsize=None,
                 processor=None): 
        self.input_queue = Queue()
        if poolsize is None:
            poolsize = DEFAULT_POOLSIZE
 
        if processor is not None:
            self._do = processor

        self._local = threading.local()

        self._threads = []
        for i in range(poolsize):
            t = Thread(target=self._worker)
            t.setDaemon(True)
            self._threads.append(t)

    def start(self):
        for t in self._threads:
            t.start()
    
    def join(self):
        self.input_queue.join()
            

    def _worker(self):
        while(True):
            try:
                job = self.input_queue.get()
                try:
                    self._do(job)
                finally:
                    self.input_queue.task_done()
            except:
                log.error(traceback.format_exc())

    def _do(self, job):
        job()


class DeferredCall(object): 
    """
    """
    def __init__(self, call, *args, **kwargs):
        self.call = call
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        self.call(*self.args, **self.kwargs)
        
class CallPool(ThreadPool):
    """
    This is a ThreadPool which assumes that 0 
    argument callables have been placed on the input_queue, 
    eg the DeferredCall above.
    """
    def __init__(self, poolsize=None):
        ThreadPool.__init__(self, poolsize=poolsize)

    def _do(self, job):
        job()


class OutputQueueMixin(object): 
    """
    just a simple mixin to add an 
    ouput queue to a ThreadPool subclass
    """
    def __init__(self, output_queue): 
        if output_queue is None:
            self.output_queue = Queue()
        else:
            self.output_queue = output_queue
