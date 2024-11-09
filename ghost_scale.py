import ghost_machine_base
from ghost_scale_audio import GhostScaleAudio
import ghost_light_fixtures


SCANNING_TIME = 8


class GhostScale(ghost_machine_base.GhostMachine):

    def __init__(self, id):
        super().__init__(id)
        self.scale_audio = GhostScaleAudio(self.audio)

    async def start(self):
        await super().start()
        self.light_patterns = [
            # ghost_light_fixtures.ScannerFiberOpticFixture(start=38, count=4, port=1),
            # ghost_light_fixtures.ScannerCanopyFixture(start=43, count=7, port=1),
            # ghost_light_fixtures.PrinterBackWallFixture(start=9, count=25, port=1),
            # ghost_light_fixtures.InnerTubeLightFixture(start=50, count=100, port=1),
            # ghost_light_fixtures.OuterTubeLightFixture(start=152, count=200, port=1),
        ]

    def _update_rfid_data(self):
        super()._update_rfid_data()
        self.current_tag_data.scale = True

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

        if event == ghost_machine_base.EVENT_FINISHED_BOOT:
            self.scale_audio.play_ambient()
        elif event == ghost_machine_base.MODE_HAS_TRASH:
            self.scale_audio.play_ready()

    def _draw_light_patterns(self):
        super()._draw_light_patterns()

        for light_pattern in self.light_patterns:
            light_pattern.draw()



