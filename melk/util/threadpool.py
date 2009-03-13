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

    implement the _do method or pass a single argument function 
    to the constructor to specify the processing of jobs
    placed on the input queue.
    
    By default it is assumed that jobs are 0 argument callables,
    a job is processed by calling it.
    """

    def __init__(self, poolsize=None,
                 processor=None,
                 output_queue=None):
        """
        poolsize - the number of threads to use to process jobs, defaults to 10
        processor - an optional 1 argument function which is used to process jobs
                    placed on the input queue. If none is specified, jobs are assumed
                    to be zero argument callables.
        output_queue - if specified, the return value of proccessing a job will be placed
                       on this output queue.
        """
        self.input_queue = Queue()
        self.output_queue = output_queue

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
                    rc = self._do(job)
                    if self.output_queue is not None:
                        self.output_queue.put(rc)
                finally:
                    self.input_queue.task_done()
            except:
                log.error(traceback.format_exc())

    def _do(self, job):
        return job()


class DeferredCall(object): 
    """
    """
    def __init__(self, call, *args, **kwargs):
        self.call = call
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        self.call(*self.args, **self.kwargs)

class ThreadPoolChain(object):
    """
    Simple helper for assembling and managing a chain of threadpools linked
    together by shared output/input queues.  Will not function property without
    at least one threadpool added.
    
    use as a normal threadpool: 
    add jobs to input_queue, start, join, receive output via output_queue 
    
    Should not be modified / appended to once it has been started or linked
    in with other chains.
    

    """

    def __init__(self):
        self._chain = []
        self.input_queue = None

    def append(self, threadpool, in_queue=None):
        """
        links threadpool to the end of the chain.  The output queue of the last
        threadpool added to the chain is set to the input queue of the given 
        threadpool. 
 
        threadpool - the threadpool to add to the chain
        in_queue - optional adapted version of the input queue of the threadpool,
        if not specified, threadpool.input_queue is used.
        """
        if in_queue is None:
            in_queue = threadpool.input_queue

        if len(self._chain) > 0:
            self._chain[-1].output_queue = in_queue
        else:
            self.input_queue = in_queue

        self._chain.append(threadpool)
        
    def _get_output_queue(self):
        if len(self._chain) > 0:
            return self._chain[-1].output_queue
        else:
            return None

    def _set_output_queue(self, val):
        self._chain[-1].output_queue = val

    output_queue = property(_get_output_queue, _set_output_queue)
    
    def start(self):
        for tp in self._chain:
            tp.start()

    def join(self):
        for tp in self._chain:
            tp.join()