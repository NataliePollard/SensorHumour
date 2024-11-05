import time

import ghost_machine_base
from ghost_listening_audio import GhostListeningAudio
import ghost_light_fixtures


SCANNING_TIME = 8

PEDASTAL_LIGHTS_START = 0
PEDASTAL_LIGHTS = 313 * 0
SCANNER_CANOPY_LIGHTS_START = PEDASTAL_LIGHTS_START + PEDASTAL_LIGHTS
SCANNER_CANOPY_LIGHTS = 7
SCANNER_FIBER_LIGHTS_START = SCANNER_CANOPY_LIGHTS_START + SCANNER_CANOPY_LIGHTS
SCANNER_FIBER_LIGHTS = 4


class GhostListeningMachine(ghost_machine_base.GhostMachine):

    next_event_time = -1

    def __init__(self):
        super().__init__("listening")
        self.listening_audio = GhostListeningAudio(self.audio)

    async def start(self):
        await super().start()
        self.light_patterns = [
            ghost_light_fixtures.ScannerFiberOpticFixture(start=SCANNER_FIBER_LIGHTS_START, count=SCANNER_FIBER_LIGHTS, port=1),
            ghost_light_fixtures.ScannerCanopyFixture(start=SCANNER_CANOPY_LIGHTS_START, count=SCANNER_CANOPY_LIGHTS, port=1),
            # ghost_light_fixtures.PedastalLightFixture(start=PEDASTAL_LIGHTS_START, end=PEDASTAL_LIGHTS, port=1),
        ]

    def _on_state_change(self, event):
        super()._on_state_change(event)

        if event == ghost_machine_base.EVENT_FINISHED_BOOT:
            print("Starting Ambient State")
            self.listening_audio.play_ambient()
            for light_pattern in self.light_patterns:
                light_pattern.off()
        elif event == ghost_machine_base.EVENT_CARD_FOUND:
            print("Starting Ready State")
            self.listening_audio.play_ready()
            self.next_event_time = -1
            for light_pattern in self.light_patterns:
                light_pattern.on()
        elif event == ghost_machine_base.EVENT_WRITE_NFC:
            print("Starting Writing State")
            self.listening_audio.play_playing()
            self.next_event_time = time.time() + SCANNING_TIME
            for light_pattern in self.light_patterns:
                light_pattern.scanning()

    def _draw_light_patterns(self):
        super()._draw_light_patterns()

        if self.next_event_time > 0 and time.time() < self.next_event_time:
            self.next_event_time = -1
            print("Turning off lights")
            for light_pattern in self.light_patterns:
                light_pattern.off()

        for light_pattern in self.light_patterns:
            light_pattern.draw()



