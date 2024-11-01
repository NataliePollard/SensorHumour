import time
from machine import Pin

WAIT_TIME = 0.2


class Button(object):
    button_pin = -1
    callback = None
    waiting = 0

    def __init__(self, button_pin, callback=None):
        self.button_pin = button_pin
        self.callback = callback

        self.pin = Pin(self.button_pin, Pin.IN, Pin.PULL_UP)
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self.__on_press, hard=True)

    def __on_press(self, value):
        now = time.time()
        if now > self.waiting:
            self.waiting = time.time() + WAIT_TIME
            if self.callback:
                self.callback()
