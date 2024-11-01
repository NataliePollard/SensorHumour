import canopy

scanner_fiber_on_pattern = None
scanner_fiber_scanning_pattern = None

scanner_off_pattern = None
scanner_on_pattern = None
scanner_scanning_pattern = None

back_wall_off_pattern = None
back_wall_on_pattern = None
back_wall_scanning_pattern = None

inner_tube_on_pattern = None
inner_tube_scanning_pattern = None

outer_tube_on_pattern = None
outer_tube_scanning_pattern = None


class BaseLightFixture(object):
    light_pattern = None

    def __init__(self, port=0, start=0, end=16, brightness=float(0.8)):
        self.segment = canopy.Segment(port, start, end)
        self.params = canopy.Params()
        self.brightness = brightness

    def draw(self):
        if self.light_pattern:
            canopy.draw(
                self.segment,
                self.light_pattern,
                alpha=self.brightness,
                params=self.params,
            )


class ScannerFiberOpticFixture(BaseLightFixture):
    def __init__(self, port=0, start=0, end=16, brightness=float(1.0)):
        super().__init__(port, start, end, brightness)

    def off(self):
        self.light_pattern = None

    def on(self):
        self.light_pattern = scanner_fiber_on_pattern

    def scanning(self):
        self.light_pattern = scanner_fiber_scanning_pattern


class ScannerCanopyFixture(BaseLightFixture):
    def __init__(self, port=0, start=0, end=16, brightness=float(0.8)):
        super().__init__(port, start, end, brightness)
    
    def off(self):
        self.light_pattern = scanner_off_pattern

    def on(self):
        self.light_pattern = scanner_on_pattern

    def scanning(self):
        self.light_pattern = scanner_scanning_pattern


class PrinterBackWallFixture(BaseLightFixture):
    def __init__(self, port=0, start=0, end=16, brightness=float(0.8)):
        super().__init__(port, start, end, brightness)

    def off(self):
        self.light_pattern = back_wall_off_pattern

    def on(self):
        self.light_pattern = back_wall_on_pattern

    def scanning(self):
        self.light_pattern = back_wall_scanning_pattern


class InnerTubeLightFixture(BaseLightFixture):
    def __init__(self, port=0, start=0, end=16, brightness=float(0.8)):
        super().__init__(port, start, end, brightness)

    def off(self):
        self.light_pattern = None

    def on(self):
        self.light_pattern = inner_tube_on_pattern

    def scanning(self):
        self.light_pattern = inner_tube_scanning_pattern


class OuterTubeLightFixture(BaseLightFixture):
    def __init__(self, port=0, start=0, end=16, brightness=float(0.8)):
        super().__init__(port, start, end, brightness)

    def off(self):
        self.light_pattern = None

    def on(self):
        self.light_pattern = outer_tube_on_pattern

    def scanning(self):
        self.light_pattern = outer_tube_scanning_pattern
