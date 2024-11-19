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

    def __init__(self, button_pin, callback=None):
        self.button_pin = button_pin
        self.callback = callback

        self.pin = Pin(self.button_pin, Pin.IN, Pin.PULL_UP)
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self.__on_press)

    def __on_press(self, pin):
        now = time.time() * 1000
        print("Button pressed", pin)
        if now > self.waiting:
            self.waiting = now + WAIT_TIME_MS
            self.button_press_time = now

    async def run(self):
        while True:
            await asyncio.sleep(0.00001)
            if self.button_press_time > 0:  # and time.time() * 1000 > self.button_press_time + PRESS_DURATION_MS:
                state = self.pin.value()
                self.button_press_time = 0
                print("Button State", state)
                if state == 0:
                    if self.callback:
                        self.callback(1)
                else:
                    print("Button not held long enough")
