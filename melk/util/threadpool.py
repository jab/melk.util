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
    items placed in it's input queue. 

    implement the _do method or passed
    as a single argument function 
    to the constructor to specify the
    processing.
    """

    def __init__(self, poolsize=DEFAULT_POOLSIZE, 
                 processor=None): 
        self.input_queue = Queue()

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


class OutputQueueMixin(object): 
    
    def __init__(self, output_queue): 
        if output_queue is None:
            self.output_queue = Queue()
        else:
            self.output_queue = output_queue
