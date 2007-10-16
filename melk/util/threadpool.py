from threading import Thread
from melk.util.taskqueue import TaskQueue as Queue
import logging

log = logging.getLogger(__name__)

class ThreadPool:
    
    def __init__(self, poolsize=10): 
        self.input_queue = Queue()
        
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
            
