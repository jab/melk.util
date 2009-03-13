from melk.util.threadpool import ThreadPool, ThreadPoolChain
from melk.util.taskqueue import TaskQueue, QueueInputAdapter


class BlackAdder(ThreadPool):

    def __init__(self):
        ThreadPool.__init__(self, poolsize=5, output_queue=TaskQueue())

    def _do(self, job):
        return job + 1


def test_threadpool_join():

    inputs = 20

    ba = BlackAdder()
    for i in range(inputs):
        ba.input_queue.put(i)

    ba.start()
    ba.join()

    assert ba.output_queue.qsize() == inputs

    outputs = []
    while ba.output_queue.qsize() > 0: 
        outputs.append(ba.output_queue.get())

    for i in range(1, inputs+1):
        assert i in outputs
        
def test_threadpool_chain():
    ba = ThreadPoolChain()
    
    # make a chain of 5 black adders
    for i in range(5):
        ba.append(BlackAdder())


    inputs = 20
    for i in range(inputs):
        ba.input_queue.put(i)

    ba.start()
    ba.join()

    assert ba.output_queue.qsize() == inputs

    outputs = []
    while ba.output_queue.qsize() > 0: 
        outputs.append(ba.output_queue.get())

    for i in range(5, inputs+5):
        assert i in outputs


def test_input_adapter():
    def to_int(val):
        return int(val)

    q = TaskQueue()
    a = QueueInputAdapter(q, to_int)
    
    inputs = 10
    for i in range(inputs):
        a.put("%d" % i)
    
    outputs = []
    while a.qsize() > 0: 
        outputs.append(a.get())
    
    for i in range(inputs):
        assert i in outputs


def test_threadpool_chain_adapters():
    class BlueAdder(ThreadPool):
        "like BlackAdder, but returns a string"
        def __init__(self):
            ThreadPool.__init__(self, poolsize=5, output_queue=TaskQueue())

        def _do(self, job):
            return "%d" % (job + 1)
    
    def adapt_blue_input(item):
        return int(item)

    ba = ThreadPoolChain()
    
    # make a chain of 5 blue adders
    for i in range(5):
        tp = BlueAdder()
        ba.append(tp, QueueInputAdapter(tp.input_queue, adapt_blue_input))

    inputs = 20
    for i in range(inputs):
        ba.input_queue.put(i)

    ba.start()
    ba.join()

    assert ba.output_queue.qsize() == inputs

    outputs = []
    while ba.output_queue.qsize() > 0: 
        outputs.append(ba.output_queue.get())

    for i in range(5, inputs+5):
        assert "%d" % i in outputs
    