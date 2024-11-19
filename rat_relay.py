from machine import Pin
import time
import random


def now():
    return time.ticks_ms()


class Relay(object):
    flickering = False
    flicker_duration = 0.1
    flicker_sleep_duration = 0.1
    last_flicker_event = 0
    state = False

    def __init__(self, pin=1, pull_up=False):
        self.pin = Pin(pin, Pin.OUT, Pin.PULL_UP if pull_up else Pin.PULL_DOWN)

    def on(self):
        self.flickering = False
        self.state = True
        self.pin.on()

    def off(self):
        self.flickering = False
        self.state = False
        self.pin.off()

    def get_flicker_on_duration(self):
        return random.random() * 300
    
    def get_flicker_off_duration(self):
        if random.random() > 0.3:
            return random.uniform(50, 300)
        return random.uniform(500, 5000)

    def flicker(self):
        # print("Flickering")
        self.flickering = True
        self.next_flicker_event = now() + self.get_flicker_off_duration()
        self.pin.off()

    def is_on(self):
        return self.pin.value() == 1

    def tick(self):
        if self.flickering:
            if self.state:
                if now() > self.next_flicker_event:
                    # print("Flicker off")
                    self.pin.off()
                    self.state = False
                    self.next_flicker_event = now() + self.get_flicker_off_duration()

            else:
                if now() > self.next_flicker_event:
                    # print("Flicker on")
                    self.pin.on()
                    self.state = True
                    self.next_flicker_event = now() + self.get_flicker_on_duration()
