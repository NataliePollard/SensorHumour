"""
Figurine Sensor RFID LED Controller

When an RFID tag is scanned, the ring light flashes the corresponding color pattern
for 5 seconds, then returns to an ambient rainbow sparkle pattern.

Supported RFID tags:
- Red tag (88ab1466080104e0)
- Blue tag (e29f1466080104e0)
- Purple tag (24941466080104e0)
- Yellow tag (2bb71466080104e0)
"""
import asyncio
import canopy
import fern
import time
from nfc import NfcWrapper
from audio import Audio
from bank_vault_audio import VaultDoorAudio


# Ring light LED patterns
RING_PATTERN_RED = canopy.Pattern('CTP-eyJrZXkiOiJyZWQtZmxhc2giLCJ2ZXJzaW9uIjowLCJuYW1lIjoicmVkLWZsYXNoIiwicGFsZXR0ZXMiOnsiUGFsZXR0ZTEiOltbMCxbMCwwLDBdXSxbMSxbMC44NTg4MjM1Mjk0MTE3NjQ3LDAsMF1dXX0sInBhcmFtcyI6eyJvbiBhbmQgb2ZmIjp7InR5cGUiOiJzcXVhcmUiLCJpbnB1dHMiOnsidmFsdWUiOjAuNSwibWluIjowLCJtYXgiOjF9fX0sImxheWVycyI6W3siZWZmZWN0Ijoic29saWQiLCJvcGFjaXR5Ijp7InR5cGUiOiJzcXVhcmUiLCJpbnB1dHMiOnsidmFsdWUiOjAuNzMsIm1pbiI6MCwibWF4IjoxfX0sImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6IlBhbGV0dGUxIiwiaW5wdXRzIjp7Im9mZnNldCI6MC41fX1dfQ')
RING_PATTERN_BLUE = canopy.Pattern('CTP-eyJpZCI6ImJsdWUiLCJ2ZXJzaW9uIjoxLCJuYW1lIjoiQmx1ZSIsInBhbGV0dGVzIjp7IlBhbGV0dGUxIjpbWzAsWzAuMTY5LDAuOTA2LDAuODQ0XV1dfSwicGFyYW1zIjp7fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzb2xpZCIsIm9wYWNpdHkiOjEsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6IlBhbGV0dGUxIiwiaW5wdXRzIjp7Im9mZnNldCI6MH19XX0')
RING_PATTERN_PURPLE = canopy.Pattern('CTP-eyJpZCI6InB1cnBsZSIsInZlcnNpb24iOjEsIm5hbWUiOiJQdXJwbGUiLCJwYWxldHRlcyI6eyJQYWxldHRlMSI6W1swLFswLjM2OSwwLjA5NCwwLjYyOV1dXX0sInBhcmFtcyI6e30sImxheWVycyI6W3siZWZmZWN0Ijoic29saWQiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQYWxldHRlMSIsImlucHV0cyI6eyJvZmZzZXQiOjB9fV19')
RING_PATTERN_YELLOW = canopy.Pattern('CTP-eyJpZCI6InllbGxvdyIsInZlcnNpb24iOjEsIm5hbWUiOiJZZWxsb3ciLCJwYWxldHRlcyI6eyJQYWxldHRlMSI6W1swLFswLjk1NywwLjcyMSwwLjE1M11dXX0sInBhcmFtcyI6e30sImxheWVycyI6W3siZWZmZWN0Ijoic29saWQiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQYWxldHRlMSIsImlucHV0cyI6eyJvZmZzZXQiOjB9fV19')
RING_PATTERN_AMBIENT_RAINBOW = canopy.Pattern("CTP-eyJrZXkiOiJyYWluYm93IiwidmVyc2lvbiI6MCwibmFtZSI6Ik5ldyBQYXR0ZXJuIiwicGFsZXR0ZXMiOnsiUGFsZXR0ZTEiOltbMCxbMSwwLDBdXSxbMC4xNCxbMSwwLjgyNzQ1MDk4MDM5MjE1NjgsMC4xNDExNzY0NzA1ODgyMzUzXV0sWzAuMzEsWzAuMDUwOTgwMzkyMTU2ODYyNzQ0LDEsMF1dLFswLjUyLFswLDAuOTQxMTc2NDcwNTg4MjM1MywwLjg2Mjc0NTA5ODAzOTIxNTddXSxbMC42OCxbMCwwLjI4MjM1Mjk0MTE3NjQ3MDYsMV1dLFswLjgsWzAuNDExNzY0NzA1ODgyMzUyOSwwLDAuODc4NDMxMzcyNTQ5MDE5Nl1dLFswLjg5LFsxLDAsMC44MTU2ODYyNzQ1MDk4MDM5XV0sWzEsWzEsMCwwXV1dfSwicGFyYW1zIjp7fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjEsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6IlBhbGV0dGUxIiwiaW5wdXRzIjp7ImRlbnNpdHkiOjAuNSwib2Zmc2V0Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMzYsIm1pbiI6MCwibWF4IjoxfX19fV19")


class FigurineSensor:
    # RFID tag to ring light pattern mapping
    TAG_PATTERNS = {
        '88ab1466080104e0': RING_PATTERN_RED,
        'e29f1466080104e0': RING_PATTERN_BLUE,
        '24941466080104e0': RING_PATTERN_PURPLE,
        '2bb71466080104e0': RING_PATTERN_YELLOW,
    }

    def __init__(self, name="figurine_sensor"):
        self.name = name
        self.num_leds = 100

        # Audio setup
        self.audio = Audio()
        self.vault_audio = VaultDoorAudio(self.audio)

        # NFC setup
        self.nfc = NfcWrapper(self._tag_found, self._tag_lost)

        # Ring light configuration
        self.flash_duration = 5.0  # How long to show flash pattern after tag scan
        self.flash_interval = 0.125  # How fast to toggle flash on/off

        # Ring light state
        self.current_pattern = RING_PATTERN_AMBIENT_RAINBOW  # Start with rainbow sparkles
        self.flash_end_time = 0
        self.flash_on = False

        # Canopy setup
        self.segment = None
        self.params = None

    async def start(self):
        """Initialize and start the system"""
        await self.nfc.start()
        self.audio.start()

        print("Starting LED strip")
        canopy.init([fern.LED1_DATA, fern.LED2_DATA], self.num_leds)

        # Create segment and params for rendering
        self.segment = canopy.Segment(0, 0, self.num_leds)
        self.params = canopy.Params()

        # Start the render loop
        asyncio.create_task(self._render_loop())
        print("Ready to scan RFID tags!")

    async def _tag_found(self, uid):
        """Called when an RFID tag is detected"""
        print(f"Tag scanned: {uid}")

        pattern = self.TAG_PATTERNS.get(uid)
        if pattern:
            self.current_pattern = pattern
            self.flash_end_time = time.time() + self.flash_duration
            self.flash_on = True
            print(f"Flashing pattern for tag {uid}")
        else:
            print("Unknown tag - ignoring")

    def _tag_lost(self):
        """Called when tag is removed"""
        print("Tag removed")

    async def _render_loop(self):
        """Main rendering loop - handles ring light LED pattern updates"""
        last_toggle_time = time.time()

        while True:
            try:
                current_time = time.time()

                # Check if flash period is over
                if self.flash_end_time > 0 and current_time > self.flash_end_time:
                    self.flash_end_time = 0
                    self.current_pattern = RING_PATTERN_AMBIENT_RAINBOW
                    self.flash_on = False
                    print("Flash complete - back to rainbow sparkles")

                # Toggle flash state every interval (only when flashing)
                if self.flash_end_time > 0 and (current_time - last_toggle_time) > self.flash_interval:
                    self.flash_on = not self.flash_on
                    last_toggle_time = current_time

                # Update ring light LEDs
                canopy.clear()

                if self.flash_end_time > 0:
                    # Currently flashing - show pattern only when flash is "on"
                    if self.flash_on and self.current_pattern:
                        canopy.draw(self.segment, self.current_pattern, params=self.params)
                else:
                    # Not flashing - show ambient pattern continuously
                    if self.current_pattern:
                        canopy.draw(self.segment, self.current_pattern, params=self.params)

                canopy.render()

            except Exception as e:
                print(f"Render loop error: {e}")

            await asyncio.sleep(0.05)  # 20 FPS
