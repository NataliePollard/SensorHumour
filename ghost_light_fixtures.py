import canopy

PatternRainbow = "CTP-eyJrZXkiOiIiLCJ2ZXJzaW9uIjoxLCJuYW1lIjoiTmV3IFBhdHRlcm4iLCJwYWxldHRlcyI6eyJQYWxldHRlMSI6W1swLFsxLDAsMF1dLFswLjE0LFsxLDAuODI3NDUwOTgwMzkyMTU2OCwwLjE0MTE3NjQ3MDU4ODIzNTNdXSxbMC4zMSxbMC4wNTA5ODAzOTIxNTY4NjI3NDQsMSwwXV0sWzAuNTIsWzAsMC45NDExNzY0NzA1ODgyMzUzLDAuODYyNzQ1MDk4MDM5MjE1N11dLFswLjY4LFswLDAuMjgyMzUyOTQxMTc2NDcwNiwxXV0sWzAuOCxbMC40MTE3NjQ3MDU4ODIzNTI5LDAsMC44Nzg0MzEzNzI1NDkwMTk2XV0sWzAuODksWzEsMCwwLjgxNTY4NjI3NDUwOTgwMzldXSxbMSxbMSwwLDBdXV19LCJwYXJhbXMiOnt9LCJsYXllcnMiOlt7ImVmZmVjdCI6InNwYXJrbGVzIiwib3BhY2l0eSI6MSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUGFsZXR0ZTEiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC41LCJvZmZzZXQiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC4zNiwibWluIjowLCJtYXgiOjF9fX19XX0"
PatternRainbow300 = "CTP-eyJrZXkiOiIiLCJ2ZXJzaW9uIjoxLCJuYW1lIjoiTmV3IFBhdHRlcm4iLCJwYWxldHRlcyI6eyJQYWxldHRlMSI6W1swLFsxLDAsMF1dLFswLjE0LFsxLDAuODI3NDUwOTgwMzkyMTU2OCwwLjE0MTE3NjQ3MDU4ODIzNTNdXSxbMC4zMSxbMC4wNTA5ODAzOTIxNTY4NjI3NDQsMSwwXV0sWzAuNTIsWzAsMC45NDExNzY0NzA1ODgyMzUzLDAuODYyNzQ1MDk4MDM5MjE1N11dLFswLjY4LFswLDAuMjgyMzUyOTQxMTc2NDcwNiwxXV0sWzAuOCxbMC40MTE3NjQ3MDU4ODIzNTI5LDAsMC44Nzg0MzEzNzI1NDkwMTk2XV0sWzAuODksWzEsMCwwLjgxNTY4NjI3NDUwOTgwMzldXSxbMSxbMSwwLDBdXV19LCJwYXJhbXMiOnt9LCJsYXllcnMiOlt7ImVmZmVjdCI6InNwYXJrbGVzIiwib3BhY2l0eSI6MSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUGFsZXR0ZTEiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC41LCJvZmZzZXQiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC4zNiwibWluIjowLCJtYXgiOjF9fX19XX0"
pattern_rainbow = canopy.Pattern(PatternRainbow)
pattern_rainbow300 = canopy.Pattern(PatternRainbow300)

scanner_fiber_off_pattern = pattern_rainbow
scanner_fiber_on_pattern = pattern_rainbow
scanner_fiber_scanning_pattern = pattern_rainbow

scanner_off_pattern = None
scanner_on_pattern = pattern_rainbow
scanner_scanning_pattern = pattern_rainbow

back_wall_off_pattern = None
back_wall_on_pattern = pattern_rainbow
back_wall_scanning_pattern = pattern_rainbow

inner_tube_off_pattern = None
inner_tube_on_pattern = pattern_rainbow
inner_tube_scanning_pattern = pattern_rainbow

outer_tube_off_pattern = None
outer_tube_on_pattern = pattern_rainbow
outer_tube_scanning_pattern = pattern_rainbow

pedastal_off_pattern = pattern_rainbow300
pedastal_on_pattern = pattern_rainbow300
pedastal_scanning_pattern = pattern_rainbow300


class BaseLightFixture(object):
    light_pattern = None

    def __init__(self, port=0, start=0, count=16, brightness=float(0.8)):
        self.segment = canopy.Segment(port, start, count)
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
    def __init__(self, port=0, start=0, count=16, brightness=float(1.0)):
        super().__init__(port, start, count, brightness)

    def off(self):
        self.light_pattern = scanner_fiber_off_pattern

    def on(self):
        self.light_pattern = scanner_fiber_on_pattern

    def scanning(self):
        self.light_pattern = scanner_fiber_scanning_pattern


class ScannerCanopyFixture(BaseLightFixture):
    def __init__(self, port=0, start=0, count=16, brightness=float(0.8)):
        super().__init__(port, start, count, brightness)
    
    def off(self):
        self.light_pattern = scanner_off_pattern

    def on(self):
        self.light_pattern = scanner_on_pattern

    def scanning(self):
        self.light_pattern = scanner_scanning_pattern


class PrinterBackWallFixture(BaseLightFixture):
    def __init__(self, port=0, start=0, count=16, brightness=float(0.8)):
        super().__init__(port, start, count, brightness)

    def off(self):
        self.light_pattern = back_wall_off_pattern

    def on(self):
        self.light_pattern = back_wall_on_pattern

    def scanning(self):
        self.light_pattern = back_wall_scanning_pattern


class InnerTubeLightFixture(BaseLightFixture):
    def __init__(self, port=0, start=0, count=16, brightness=float(0.8)):
        super().__init__(port, start, count, brightness)

    def off(self):
        self.light_pattern = inner_tube_off_pattern

    def on(self):
        self.light_pattern = inner_tube_on_pattern

    def scanning(self):
        self.light_pattern = inner_tube_scanning_pattern


class OuterTubeLightFixture(BaseLightFixture):
    def __init__(self, port=0, start=0, count=16, brightness=float(0.8)):
        super().__init__(port, start, count, brightness)

    def off(self):
        self.light_pattern = outer_tube_off_pattern

    def on(self):
        self.light_pattern = outer_tube_on_pattern

    def scanning(self):
        self.light_pattern = outer_tube_scanning_pattern


class PedastalLightFixture(BaseLightFixture):
    def __init__(self, port=0, start=0, count=16, brightness=float(0.8)):
        super().__init__(port, start, count, brightness)

    def off(self):
        self.light_pattern = pedastal_off_pattern

    def on(self):
        self.light_pattern = pedastal_on_pattern

    def scanning(self):
        self.light_pattern = pedastal_scanning_pattern
