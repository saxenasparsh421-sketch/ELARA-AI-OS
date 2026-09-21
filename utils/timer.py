import time


class Timer:

    def __init__(self):
        self.start = time.perf_counter()

    def stop(self):
        return round(time.perf_counter() - self.start, 2)