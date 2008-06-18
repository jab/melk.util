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
from Queue import Queue

if hasattr(Queue, 'join'):
    TaskQueue = Queue
else:
    # this is for python2.4, breaks python2.5 which adopts this
    class TaskQueue(Queue):
        """
        Recipe from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/475160
        this is a part of python 2.5, should probably check for it there
        """

        def __init__(self):
            Queue.__init__(self)
            self.all_tasks_done = threading.Condition(self.mutex)
            self.unfinished_tasks = 0

        def _put(self, item):
            Queue._put(self, item)
            self.unfinished_tasks += 1

        def task_done(self):
            """Indicate that a formerly enqueued task is complete.

            Used by Queue consumer threads.  For each get() used to fetch a task,
            a subsequent call to task_done() tells the queue that the processing
            on the task is complete.

            If a join() is currently blocking, it will resume when all items
            have been processed (meaning that a task_done() call was received
            for every item that had been put() into the queue).

            Raises a ValueError if called more times than there were items
            placed in the queue.
            """
            self.all_tasks_done.acquire()
            try:
                unfinished = self.unfinished_tasks - 1
                if unfinished <= 0:
                    if unfinished < 0:
                        raise ValueError('task_done() called too many times')
                    self.all_tasks_done.notifyAll()
                self.unfinished_tasks = unfinished
            finally:
                self.all_tasks_done.release()

        def join(self):
            """Blocks until all items in the Queue have been gotten and processed.

            The count of unfinished tasks goes up whenever an item is added to the
            queue. The count goes down whenever a consumer thread calls task_done()
            to indicate the item was retrieved and all work on it is complete.

            When the count of unfinished tasks drops to zero, join() unblocks.
            """
            self.all_tasks_done.acquire()
            try:
                while self.unfinished_tasks:
                    self.all_tasks_done.wait()
            finally:
                self.all_tasks_done.release()


class QueueProxy: 
    """
    """
    def __init__(self, queue): 
        self._queue = queue

    def __getattr__(self, name): 
        return getattr(self._queue, name)

class QueueInputAdapter(QueueProxy): 
    """
    wraps a Queue and performs an arbitrary transformation
    of inputs before pushing (on the pushing thread)
    """
    def __init__(self, queue, input_adaptation=None):
        if input_adaptation is not None:
            self._transform = input_adaptation

    def _put(self, item): 
        xitem = self._transform(item)
        return self._queue.put(xitem)

