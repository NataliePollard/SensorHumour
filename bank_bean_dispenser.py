from machine import Pin
import asyncio
import time


CLICK_INTERVAL_S = 0.5


class BeanDispenser(object):
    def __init__(self, pin=2):
        self.pin = pin
        self.next_click_time = 0
        self.amount = 0

    def dispense(self, amount=1):
        self.amount = amount


    def start(self):
        print("Initing Dispenser")
        try:
            asyncio.create_task(self._dispenser_loop())
        except:
            print("Dispenser Failed to init")

    async def _dispenser_loop(self):
        pin = Pin(self.pin, Pin.OUT, Pin.PULL_UP)
        pin.on()
        print("Dispenser Initialized")
        while True:
            now = time.time()
            if self.amount > 0 and now > self.next_click_time:
                print("Dispensing bean")
                pin.off()
                await asyncio.sleep(0.1)
                pin.on()
                self.amount -= 1
                self.next_click_time = now + CLICK_INTERVAL_S
            await asyncio.sleep(0.1)
