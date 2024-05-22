from rat_artifact import *
from rat_relay import Relay
import time

CITY_MODE_DRAINING = 1
CITY_MODE_EMPTY = 2
CITY_MODE_FILLING = 3
CITY_MODE_FULL = 4
CITY_MODE_PARTIALLY_FULL = 5

FILL_TIME = 60
DRAIN_TIME = 60


class CityArtifact(Artifact):
    city_mode = CITY_MODE_FULL
    drain_relay = Relay(2)
    fill_relay = Relay(3)
    last_event_time = 0

    def __init__(self, name):
        super().__init__(name, relay_pin=4)
        self.start_draining()

    def _after_update_state(self):
        super()._after_update_state()
        if self.current_mode == MODE_CONNECTED and (
            self.city_mode != CITY_MODE_FULL or self.city_mode != CITY_MODE_FILLING
        ):
            self.start_filling()
            return
        if (
            self.current_mode == MODE_INVALID
            or self.current_mode == MODE_WAITING
            or self.current_mode == MODE_OFF
        ) and (
            self.city_mode != CITY_MODE_EMPTY or self.city_mode != CITY_MODE_DRAINING
        ):
            self.start_draining()

    def start_draining(self):
        self.city_mode = CITY_MODE_DRAINING
        self.last_event_time = time.time()

    def start_filling(self):
        self.city_mode = CITY_MODE_FILLING
        self.last_event_time = time.time()

    def stop(self):
        self.drain_relay.off()
        self.fill_relay.off()
        self.last_event_time = time.time()
        if self.city_mode == CITY_MODE_FILLING or self.city_mode == CITY_MODE_DRAINING:
            self.city_mode = CITY_MODE_PARTIALLY_FULL

    def _update(self):
        super()._update()
        now = time.time()
        if self.city_mode == CITY_MODE_DRAINING:
            if self.last_event_time + DRAIN_TIME > now:
                self.city_mode = CITY_MODE_EMPTY
                self.drain_relay.off()
        if self.city_mode == CITY_MODE_FILLING:
            if self.last_event_time + FILL_TIME > now:
                self.city_mode = CITY_MODE_FULL
                self.fill_relay.off()
