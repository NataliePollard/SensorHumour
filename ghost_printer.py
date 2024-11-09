import ghost_machine_base
from ghost_printer_audio import PrinterAudio
import ghost_light_fixtures
from rat_relay import Relay


SCANNING_TIME = 8


class GhostPrinter(ghost_machine_base.GhostMachine):

    def __init__(self):
        super().__init__("printer")
        self.printer_audio = PrinterAudio(self.audio)
        self.relay = Relay(2)

    async def start(self):
        await super().start()
        self.light_patterns = [
            ghost_light_fixtures.ScannerFiberOpticFixture(start=38, count=4, port=1),
            ghost_light_fixtures.ScannerCanopyFixture(start=43, count=7, port=1),
            ghost_light_fixtures.PrinterBackWallFixture(start=9, count=25, port=1),
            # ghost_light_fixtures.InnerTubeLightFixture(start=50, count=100, port=1),
            # ghost_light_fixtures.OuterTubeLightFixture(start=152, count=200, port=1),
        ]

    def _update_rfid_data(self):
        super()._update_rfid_data()
        self.current_tag_data.printer = True
        # Reset all the data
        self.current_tag_data.audio = False
        self.current_tag_data.dollhouse = False
        self.current_tag_data.other1 = False
        self.current_tag_data.other2 = False
        self.current_tag_data.other3 = False
        self.current_tag_data.scale = False

    def _on_state_change(self, event):
        super()._on_state_change(event)

        if self.current_mode in [ghost_machine_base.MODE_INITIALIZING, ghost_machine_base.MODE_WAITING_FOR_TRASH]:
            for light_pattern in self.light_patterns:
                light_pattern.off()
        elif self.current_mode in [ghost_machine_base.MODE_HAS_TRASH, ghost_machine_base.MODE_FINISHED, ghost_machine_base.MODE_RUNNING]:
            for light_pattern in self.light_patterns:
                light_pattern.scanning()
        elif self.current_mode in [ghost_machine_base.MODE_READY_TO_PRINT]:
            for light_pattern in self.light_patterns:
                light_pattern.on()

        if self.current_mode in [ghost_machine_base.MODE_READY_TO_PRINT]:
            self.relay.on()
        elif self.current_mode in [ghost_machine_base.MODE_RUNNING]:
            self.relay.flicker()
        else:
            self.relay.off()

        if event == ghost_machine_base.EVENT_FINISHED_BOOT:
            self.printer_audio.play_ambient()
        elif event == ghost_machine_base.EVENT_SET_RUNNING:
            self.printer_audio.play_printing()

    def _draw_light_patterns(self):
        super()._draw_light_patterns()

        for light_pattern in self.light_patterns:
            light_pattern.draw()

        self.relay.tick()



