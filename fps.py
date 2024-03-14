import time


class FPS:
    def __init__(self, verbose=False):
        self._accum = 0
        self._count = 0
        self._last_calc = 0
        self._fps = 0
        self.verbose = verbose

    def tick(self):
        now = time.ticks_ms()
        delta = time.ticks_diff(now, self._last_calc)
        self._accum += delta
        self._count += 1

        if time.ticks_diff(now, self._last_calc) > 1000:
            self._fps = 1000 / (self._accum / self._count)
            self._accum = 0
            self._count = 0
            self._last_calc = now

            if self.verbose:
                print("FPS: ", self._fps)

    @property
    def fps(self):
        return self._fps
