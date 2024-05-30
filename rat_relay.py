from machine import Pin


class Relay(object):
    def __init__(self, pin=1, pull_up=False):
        self.pin = Pin(pin, Pin.OUT, Pin.PULL_UP if pull_up else Pin.PULL_DOWN)

    def on(self):
        self.pin.on()

    def off(self):
        self.pin.off()

    def is_on(self):
        return self.pin.value() == 1
