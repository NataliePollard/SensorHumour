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
        add_event_detection(self.button_pin, callback=self.__on_press)
        if button_light_pin > 0:
            GPIO.setup(self.button_light_pin, GPIO.OUT)

    def __on_press(self, value):
        now = time.time()
        if now > self.waiting:
            self.waiting = time.time() + WAIT_TIME
            if self.callback:
                self.callback()
