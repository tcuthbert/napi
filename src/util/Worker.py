import sys

import threading

__all__ = ["thread_runner"]

class Worker(threading.Thread):
    def __init__(self, func, *args, **kwargs):
        "docstring"
        super(Worker, self).__init__()
        self.proc = func
        self.daemon = True

    def run(self):
        try:
            self.proc()
        except (KeyboardInterrupt, SystemExit):
            pass


def thread_runner(n_threads, func):
    "docstring"
    if n_threads > 5:
        raise ValueError

    thread_queue = []
    for iii in xrange(n_threads):
        thread_queue.append(Worker(print_test_var))
    for t in thread_queue:
        t.start()
    try:
        for t in thread_queue:
            while t.is_alive():
                t.join(7)
    except (KeyboardInterrupt, SystemExit):
        print 'exitting thread..'


def main():
    return

if __name__ == '__main__':
   main()
