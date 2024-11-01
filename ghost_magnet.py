from machine import Pin


class Magnet(object):
    def __init__(self, pin=2):
        self.pin = pin
        self.is_open = False
        self.magnet_pin = Pin(self.pin, Pin.OUT, Pin.PULL_UP)
        self.close()

    def open(self):
        print("Opening magnet")
        self.is_open = True
        self.magnet_pin.on()

    def close(self):
        print("Closing magnet")
        self.is_open = False
        self.magnet_pin.off()
