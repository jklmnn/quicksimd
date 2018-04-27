
import time
import threading
import queue

class Simd:

    inq = queue.Queue()
    outq = queue.Queue()
    active = True
    threads = set()

    def __init__(self, setup, task):
        """__init__

        :param setup: setup(static) function takes thread global arguments, returns thread local data
        :param task: task(local, data) function takes thread local data and single date, returns single date or None
        """
        self.setup = setup
        self.task = task

    def _worker(self, static):
        thread_local = self.setup(static)
        while self.active:
            result = self.task(thread_local, self.inq.get(block=True, timeout=None))
            if not result == None:
                self.outq.put(result)

    def run(self, num, static):
        """run

        start task execution

        :param num: number of parallel tasks
        :param static: global static data
        """
        self.active = True
        for i in range(num):
            t = threading.Thread(target=self._worker, args=(static,))
            self.threads.add(t)
            t.start()

    def stop(self):
        """stop

        stop task execution
        """
        self.active = False
        for t in threads:
            t.join()
            self.threads.remove(t)

    def get(self, block=True, timeout=None):
        """get

        get single execution result

        :param block: block if no result is available
        :param timeout: timeout for block
        """
        return self.outq.get(block=block, timeout=timeout)

    def results(self, block=True, timeout=None):
        """results

        get all results

        :param block: block if no result is available
        :param timeout: timeout for block
        """
        while True:
            try:
                yield self.get(block, timeout)
            except queue.Empty:
                return

    def put(self, val):
        """put

        put data to be processed by task

        :param val:
        """
        self.inq.put(val)

    def take(self, gen, max_in, wait=1):
        """take

        take items from a generator
        :param gen: generator
        :param max_in: maximal number of items in the input queue
        :param wait: time to wait if input queue is full (max_in)
        """
        for item in gen:
            self.put(item)
            if self.inq.qsize() > max_in:
                time.sleep(wait)

    def take_background(self, gen, max_in, wait=1):
        """take_background

        run take in a separate thread
        :param gen:
        :param max_in:
        :param wait:
        """
        threading.Thread(target=self.take, args=(gen, max_in, wait)).start()

