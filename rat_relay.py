from machine import Pin


class Relay(object):
    def __init__(self, pin=2):
        self.pin = Pin(pin, Pin.OUT)

    def on(self):
        self.pin.on()

    def off(self):
        self.pin.off()

    def is_on(self):
        return self.pin.value() == 1
