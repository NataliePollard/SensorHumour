import time


class FPS:
    def __init__(self, verbose=False):
        self._count = 0
        self._last_calc = 0
        self._fps = 0
        self.verbose = verbose

    def tick(self):
        now = time.ticks_ms()
        delta = time.ticks_diff(now, self._last_calc)
        self._count += 1

        if  delta >= 1000:
            # print("Ticks diff: ", ticks_diff)
            # print("Accum: ", self._accum)
            # print("Count: ", self._count)
            self._fps = self._count / (delta / 1000)
            self._count = 0
            self._last_calc = now

            if self.verbose:
                print("FPS: ", self._fps)

    @property
    def fps(self):
        return self._fps
