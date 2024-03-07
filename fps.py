import time


class FPS:
    def __init__(self, verbose=False):
        self.last = 0
        self.accum = 0
        self.count = 0
        self.last_calc = 0
        self.fps = 0
        self.verbose = verbose

    def tick(self):
        now = time.ticks_ms()
        delta = time.ticks_diff(now, self.last)
        self.last = now
        self.accum += delta
        self.count += 1

        if time.ticks_diff(now, self.last_calc) > 1000:
            self.fps = 1000 / (self.accum / self.count)
            if self.verbose:
                print("FPS: ", self.fps)
            self.accum = 0
            self.count = 0
            self.last_calc = now
