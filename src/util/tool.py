import threading
import time


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


class Timer:
    def __init__(self):
        self.start = time.time()

    def restart(self):
        self.start = time.time()

    def get_time_hhmmss(self):
        end = time.time()
        m, s = divmod(end - self.start, 60)
        h, m = divmod(m, 60)
        time_str = "%02d:%02d:%02d" % (h, m, s)
        return time_str


class AtomicCounter:
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def value(self):
        with self._lock:
            return self.value

    def increment(self, num=1):
        with self._lock:
            self.value += num
            return self.value
