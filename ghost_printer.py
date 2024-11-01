import ghost_machine_base
from ghost_printer_audio import PrinterAudio
import ghost_light_fixtures


SCANNING_TIME = 8


class GhostPrinter(ghost_machine_base.GhostMachine):

    next_event_time = -1

    def __init__(self):
        super().__init__("printer")
        self.printer_audio = PrinterAudio(self.audio)

    async def start(self):
        await super().start()
        self.light_patterns = [ 
            ghost_light_fixtures.ScannerFiberOpticFixture(start=0, end=16),
            ghost_light_fixtures.ScannerCanopyFixture(start=0, end=16),
            ghost_light_fixtures.PrinterBackWallFixture(start=0, end=16),
            ghost_light_fixtures.InnerTubeLightFixture(start=0, end=16),
            ghost_light_fixtures.OuterTubeLightFixture(start=0, end=16),
        ]

    def _on_state_change(self, event):
        super()._on_state_change(event)

        if event == ghost_machine_base.EVENT_FINISHED_BOOT:
            self.printer_audio.play_ambient()
            for light_pattern in self.light_patterns:
                light_pattern.off()
        elif event == ghost_machine_base.EVENT_CARD_FOUND:
            self.printer_audio.play_ready()
            self.next_event_time = -1
            for light_pattern in self.light_patterns:
                light_pattern.on()
        elif event == ghost_machine_base.EVENT_WRITE_NFC:
            self.printer_audio.play_printing()
            self.next_event_time = self.time + SCANNING_TIME
            for light_pattern in self.light_patterns:
                light_pattern.scanning()

    def _draw_light_patterns(self):
        super._draw_light_patterns()

        if self.next_event_time > 0 and self.time < self.next_event_time:
            self.next_event_time = -1
            for light_pattern in self.light_patterns:
                light_pattern.off()

        for light_pattern in self.light_patterns:
            light_pattern.draw()



