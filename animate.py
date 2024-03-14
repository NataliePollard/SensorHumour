import time


class param:
    def __init__(self, value=0, target=0, dt=0, min=0.0, max=1.0):
        self.value = float(value)
        self.tween(target, dt)

    def tween(self, target, dt):
        self.target = float(target)
        self.dt = dt
        self.start_time = time.time()

    def __float__(self):
        if self.target == self.value:
            return self.target
        progress = (time.time() - self.start_time) / self.dt
        if progress > 1:
            self.value = self.target
            return self.target
        else:
            return self.value + (self.target - self.value) * progress

    def __repr__(self):
        return str(float(self))
