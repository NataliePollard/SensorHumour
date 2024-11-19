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
        self.listening_audio.play_ambient()

    def _update_rfid_data(self):
        super()._update_rfid_data()
        self.current_tag_data.audio = True

    def _on_state_change(self, event):
        super()._on_state_change(event)

        if self.current_mode in [ghost_machine_base.MODE_INITIALIZING, ghost_machine_base.MODE_WAITING_FOR_TRASH]:
            for light_pattern in self.light_patterns:
                light_pattern.off()
        elif self.current_mode in [ghost_machine_base.MODE_HAS_TRASH, ghost_machine_base.MODE_FINISHED]:
            for light_pattern in self.light_patterns:
                light_pattern.scanning()
        elif self.current_mode in [ghost_machine_base.MODE_RUNNING]:
            for light_pattern in self.light_patterns:
                light_pattern.on()

    def _draw_light_patterns(self):
        super()._draw_light_patterns()

        for light_pattern in self.light_patterns:
            light_pattern.draw()



