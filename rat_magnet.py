from machine import Pin
import asyncio
import time


MAX_MAGNET_ON_TIME = 5
MAGNET_COOLDOWN_TIME = 5


class Magnet(object):
    def __init__(self, pin=2):
        self.pin = pin
        self.is_connected = False
        self.is_invalid = False
        self.is_cooling_down = False
        self.next_magnet_time = 0

    def connect(self, is_invalid=False):
        self.is_connected = True
        self.is_invalid = is_invalid

    def disconnect(self):
        self.is_connected = False
        self.is_invalid = False

    def start(self):
        print("Initing magnet")
        try:
            asyncio.create_task(self._magnet_loop())
        except:
            print("Magnet Failed to init")

    async def _magnet_loop(self):
        pin = Pin(self.pin, Pin.OUT, Pin.PULL_UP)
        pin.on()
        print("Magnet Initialized")
        while True:
            now = time.time()
            if pin.value() == 0 and now > self.next_magnet_time + MAX_MAGNET_ON_TIME:
                print("Magnet off too long, turning back on")
                pin.on()
                self.next_magnet_time = now + MAGNET_COOLDOWN_TIME
                self.is_cooling_down = True
            elif self.is_invalid and now > self.next_magnet_time and pin.value() == 1:
                print("magnet rejecting")
                pin.off()
                self.next_magnet_time = now
                self.is_cooling_down = False
            elif not self.is_connected and pin.value() == 0:
                print("Magnet engaging")
                pin.on()
                self.is_cooling_down = False
            await asyncio.sleep(0.1)
