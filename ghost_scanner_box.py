import time

import ghost_machine_base
from rat_relay import Relay
from ghost_scanner_audio import GhostScannerAudio
import ring_light


RELAY_ON_LENGTH = 10


class GhostScannerBox(ghost_machine_base.GhostMachine):

    def __init__(self, name):
        super().__init__(name, has_wifi=False)

        self.scanner_audio = GhostScannerAudio(self.audio, name)
        print("Scanner", name)
        self.name = name
        if name == "scanner1":
            self.relay = Relay(pin=1)
        else:
            self.relay = Relay(pin=2)
        self.relay_on_time = 0

    async def start(self):
        await super().start()
        print("starting", self.audio.mixer)
        self.scanner_audio.play_ambient()
        self._update_state(ghost_machine_base.EVENT_FINISHED_BOOT)

    def _update_rfid_data(self):
        super()._update_rfid_data()
        if self.name == "scanner1":
            self.current_tag_data.other1 = True
        elif self.name == "scanner2":
            self.current_tag_data.other2 = True
        elif self.name == "scanner3":
            self.current_tag_data.other3 = True

    def _can_connect_tag(self):
        return True  # self.current_mode == ghost_machine_base.MODE_FINISHED  # and self.current_tag and not self.current_tag_data.dollhouse

    def _on_state_change(self, event):
        super()._on_state_change(event)
        self.previous_tag = None

        # if self.has_invalid_tag:
        #     self.ring_light.set_mode(ring_light.MODE_INVALID)

        if event in [ghost_machine_base.EVENT_FINISHED_BOOT, ghost_machine_base.EVENT_RESET_COMMAND]:
            self.relay.off()
            print("Relay off")

        if event in [ghost_machine_base.EVENT_DONE_WRITING]:
            self.has_invalid_tag = True
            self.scanner_audio.play_correct()

        if self.has_invalid_tag:
            self.ring_light.set_mode(ring_light.MODE_INVALID)
        elif event in [ghost_machine_base.EVENT_CARD_FOUND]:
            self.ring_light.set_mode(ring_light.MODE_CONNECTED)
            self.relay.on()
            self.relay_on_time = time.time()
        elif event in [ghost_machine_base.EVENT_DONE_WRITING]:
            self.ring_light.set_mode(ring_light.MODE_INVALID)
        else:
            self.ring_light.set_mode(ring_light.MODE_WAITING)

    def _update_ring_light_pattern(self):
        pass
        # if self.has_invalid_tag:
        #     self.ring_light.set_mode(ring_light.MODE_INVALID)
        # elif not self.is_finished:
        #     self.ring_light.set_mode(ring_light.MODE_OFF)
        # elif self.is_writing_rfid:
        #     # self.ring_light.set_mode(ring_light.MODE_CONNECTED)
        #     pass
        # elif self.current_mode == ghost_machine_base.MODE_WAITING_FOR_TRASH:
        #     self.ring_light.set_mode(ring_light.MODE_WAITING)
        # elif self.current_mode == ghost_machine_base.MODE_HAS_TRASH:
        #     self.ring_light.set_mode(ring_light.MODE_CONNECTED)
        print("Updated light pattern to: ", self.ring_light.current_mode)

    def _draw_light_patterns(self):
        super()._draw_light_patterns()
        if self.relay_on_time > 0 and time.time() > self.relay_on_time + RELAY_ON_LENGTH:
            self.relay_on_time = 0
            self.relay.off()
