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
WAIT_AFTER_FILL = 60


class CityArtifact(Artifact):
    city_mode = CITY_MODE_FULL
    drain_relay = Relay(3)
    fill_relay = Relay(1)
    last_event_time = 0

    def __init__(self, name, second_light_pattern=None, second_pattern_num_pixels=70):
        super().__init__(
            name,
            relay_pin=5,
            magnet_pin=2,
            second_light_pattern=second_light_pattern,
            second_pattern_start_address=30,
            second_pattern_num_pixels=second_pattern_num_pixels,
        )
        self.start_draining()

    def _on_city_drain(self):
        self.start_filling()

    def _after_update_state(self):
        super()._after_update_state()
        # if self.current_mode == MODE_CONNECTED and (
        #     self.city_mode != CITY_MODE_FULL or self.city_mode != CITY_MODE_FILLING
        # ):
        #     self.start_filling()
        #     return
        # if (
        #     self.current_mode == MODE_INVALID
        #     or self.current_mode == MODE_WAITING
        #     or self.current_mode == MODE_OFF
        # ) and (
        #     self.city_mode != CITY_MODE_EMPTY or self.city_mode != CITY_MODE_DRAINING
        # ):
        #     self.start_draining()

    def _after_update_light_pattern(self):
        if (
            self.city_mode == CITY_MODE_FILLING
            or self.city_mode == CITY_MODE_FULL
            or self.city_mode == CITY_MODE_DRAINING
        ):
            self.second_light_pattern = self.second_light_pattern_to_use
        else:
            self.second_light_pattern = None

    def start_draining(self):
        print("Draining")
        self.city_mode = CITY_MODE_DRAINING
        self.drain_relay.on()
        self.fill_relay.off()
        self.last_event_time = time.time()

    def start_filling(self):
        print("Filling")
        self.city_mode = CITY_MODE_FILLING
        self.drain_relay.off()
        self.fill_relay.on()
        self.last_event_time = time.time()

    def stop(self):
        print("Stopping")
        self.drain_relay.off()
        self.fill_relay.off()
        self.last_event_time = time.time()
        if self.city_mode == CITY_MODE_FILLING or self.city_mode == CITY_MODE_DRAINING:
            self.city_mode = CITY_MODE_PARTIALLY_FULL

    def _update(self):
        super()._update()
        now = time.time()
        if self.city_mode == CITY_MODE_DRAINING:
            if self.last_event_time + DRAIN_TIME < now:
                self.city_mode = CITY_MODE_EMPTY
                self.drain_relay.off()
                self.last_event_time = now
                print("Done Draining")
        elif self.city_mode == CITY_MODE_FILLING:
            if self.last_event_time + FILL_TIME < now:
                self.city_mode = CITY_MODE_FULL
                self.fill_relay.off()
                self.last_event_time = now
                print("Done Filling")
        elif (
            self.city_mode == CITY_MODE_FULL
            and self.last_event_time + WAIT_AFTER_FILL < now
        ):
            self.start_draining()
