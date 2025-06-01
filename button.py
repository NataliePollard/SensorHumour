import time
from machine import Pin
import asyncio

WAIT_TIME_MS = 200
PRESS_DURATION_MS = 0


class Button(object):
    button_pin = -1
    callback = None
    waiting = 0
    button_press_time = 0

    def __init__(self, button_pin, callback=None, wait_time_ms=WAIT_TIME_MS, pull_up=True, light_pin=None):
        self.button_pin = button_pin
        self.callback = callback
        self.wait_time_ms = wait_time_ms
        self.waiting = 0
        self.button_press_time = 0
        self.pull_up = pull_up
        self.light_pin = light_pin
        if light_pin is not None:
            self.light = Pin(light_pin, Pin.OUT)
            self.light.on()
        if pull_up:
            self.pin = Pin(self.button_pin, Pin.IN, Pin.PULL_UP)
        else:
            self.pin = Pin(self.button_pin, Pin.IN, Pin.PULL_DOWN)
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self.__on_press)

    def set_light(self, state):
        if self.light_pin is not None:
            if state:
                self.light.on()
            else:
                self.light.off()

    def is_pressed(self):
        if self.pull_up:
            return self.pin.value() == 0
        else:
            return self.pin.value() == 1

    def __on_press(self, pin):
        now = time.time() * 1000
        print("Button pressed", pin)
        if self.wait_time_ms <= 0:
            self.button_press_time = 0
            if self.callback:
                self.callback(1)
        elif self.waiting == 0:
            self.waiting = now + self.wait_time_ms
            self.button_press_time = now

    async def run(self):
        while True:
            await asyncio.sleep(0.00001)
            if self.button_press_time > 0:  # and time.time() * 1000 > self.button_press_time + PRESS_DURATION_MS:
                state = self.pin.value()
                self.button_press_time = 0
                self.waiting = 0
                print("Button State", state)
                if self.is_pressed():
                    if self.callback:
                        self.callback(1)
                else:
                    print("Button not held long enough")
