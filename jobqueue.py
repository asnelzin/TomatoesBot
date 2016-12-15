import time

from queue import PriorityQueue, Empty
from threading import Event, Lock, Thread


class Job(object):
    job_queue = None

    def __init__(self, interval, task):
        self.interval = interval
        self.__task = task

    def __repr__(self):
        return 'Job(interval=%r, task=%r)' % (self.interval, self.__task)

    def run(self):
        self.__task(self)


class JobQueue(object):
    def __init__(self):
        self.__queue = PriorityQueue()
        self.__tick = Event()

        self.__start_lock = Lock()
        self.__running = False
        self.__thread = None  # :Thread

        self.__next_peek_lock = Lock()
        self.__next_peek = None  # :float

    def _main_loop(self):
        while self.__running:
            with self.__next_peek_lock:
                timeout = self.__next_peek and self.__next_peek - time.time()
                self.__next_peek = None
                self.__tick.clear()

            self.__tick.wait(timeout)

            self._tick()

    def _set_next_peek(self, t):
        with self.__next_peek_lock:
            if self.__next_peek is None or t < self.__next_peek:
                self.__next_peek = t
                self.__tick.set()

    def _tick(self):
        while True:
            now = time.time()

            try:
                t, job = self.__queue.get()
            except Empty:
                break

            if t > now:
                self.__queue.put((t, job))
                self._set_next_peek(t)
                break

            try:
                job.run()
            except:
                print('Error in job')

    def start(self):
        with self.__start_lock:
            if not self.__running:
                self.__running = True
                self.__thread = Thread(target=self._main_loop, name='job_queue')
                self.__thread.start()

    def put(self, job: Job):
        job.job_queue = self

        now = time.time()
        t = now + job.interval

        self.__queue.put((t, job))
        self._set_next_peek(t)
