from melk.util.threadpool import ThreadPool, OutputQueueMixin
from melk.util.taskqueue import TaskQueue


class BlackAdder(ThreadPool, OutputQueueMixin):

    def __init__(self):
        ThreadPool.__init__(self, poolsize=5)
        OutputQueueMixin.__init__(self, TaskQueue())

    def _do(self, job):
        self.output_queue.put(job + 1)



def test_threadpool_join():

    inputs = 20

    ba = BlackAdder()
    for i in range(inputs):
        ba.input_queue.put(i)

    ba.start()
    ba.join()
    
    assert ba.output_queue.qsize() == inputs
