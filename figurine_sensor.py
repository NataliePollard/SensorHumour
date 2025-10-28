"""
Figurine Sensor RFID LED Controller

When an RFID tag is scanned, the ring light displays the corresponding animated pattern
for 5 seconds with accompanying water sound, then returns to the ambient rainbow sparkle pattern.

Supported RFID tags:
- Red tag (88ab1466080104e0) - Red flowing water animation
- Blue tag (e29f1466080104e0) - Solid blue
- Purple tag (24941466080104e0) - Purple flowing water animation
- Yellow tag (2bb71466080104e0) - Solid yellow
"""
import asyncio
import canopy
import fern
import time
from nfc import NfcWrapper
from audio import Audio
from figurine_sensor_audio import FigurineSensorAudio


# Ring light LED patterns
RING_PATTERN_RED = canopy.Pattern('CTP-eyJrZXkiOiJyZWQtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJyZWQtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMCxbMSwwLDBdXSxbMC4xNSxbMSwxLDBdXSxbMC4zLFswLDEsMF1dLFswLjUsWzAsMSwxXV0sWzAuNyxbMCwwLDFdXSxbMC44NSxbMSwwLDFdXSxbMSxbMSwwLDBdXV0sIl9ibGFjay13aGl0ZSI6W1swLFswLDAsMF1dLFsxLFsxLDEsMV1dXSwiUGFsZXR0ZTMiOltbMCxbMCwwLDBdXSxbMC4zMyxbMCwwLDBdXSxbMC42NixbMC41MDE5NjA3ODQzMTM3MjU1LDAsMC4wNzQ1MDk4MDM5MjE1Njg2M11dLFsxLFswLjUwOTgwMzkyMTU2ODYyNzQsMC4wNzg0MzEzNzI1NDkwMTk2LDAuMTMzMzMzMzMzMzMzMzMzMzNdXV19LCJwYXJhbXMiOnsic3BlZWQiOjAuMzEsInNpemUiOiJzcGVlZCIsImRlbnNpdHkiOnsidHlwZSI6InNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC4xOSwibWluIjowLCJtYXgiOjF9fX0sImxheWVycyI6W3siZWZmZWN0IjoicGxhc21hIiwib3BhY2l0eSI6MSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUGFsZXR0ZTMiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC40Nywib2Zmc2V0IjoiZGVuc2l0eSIsImNlbnRlcl94IjowLjUsImNlbnRlcl95IjowLjV9fV19')
RING_PATTERN_BLUE = canopy.Pattern('CTP-eyJpZCI6ImJsdWUiLCJ2ZXJzaW9uIjoxLCJuYW1lIjoiQmx1ZSIsInBhbGV0dGVzIjp7IlBhbGV0dGUxIjpbWzAsWzAuMTY5LDAuOTA2LDAuODQ0XV1dfSwicGFyYW1zIjp7fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzb2xpZCIsIm9wYWNpdHkiOjEsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6IlBhbGV0dGUxIiwiaW5wdXRzIjp7Im9mZnNldCI6MH19XX0')
RING_PATTERN_PURPLE = canopy.Pattern('CTP-eyJrZXkiOiJwdXJwbGUtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJwdXJwbGUtZmxvdyIsInBhbGV0dGVzIjp7IlBhbGV0dGUzIjpbWzAsWzAsMCwwXV0sWzAuMTUsWzAsMCwwXV0sWzAuMzksWzAuNTIxNTY4NjI3NDUwOTgwNCwwLjA5NDExNzY0NzA1ODgyMzUzLDAuNzg4MjM1Mjk0MTE3NjQ3XV0sWzAuNjEsWzAuMTgwMzkyMTU2ODYyNzQ1MSwwLjAxOTYwNzg0MzEzNzI1NDksMC4zMDE5NjA3ODQzMTM3MjU0N11dLFswLjk5LFswLDAsMF1dXX0sInBhcmFtcyI6eyJkZW5zaXR5Ijp7InR5cGUiOiJzYXciLCJpbnB1dHMiOnsidmFsdWUiOjAuNSwibWluIjowLCJtYXgiOjF9fX0sImxheWVycyI6W3siZWZmZWN0IjoicGlud2hlZWwiLCJvcGFjaXR5IjowLjgxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQYWxldHRlMyIsImlucHV0cyI6eyJvZmZzZXQiOiJkZW5zaXR5Iiwic2l6ZSI6MC4zOCwiY2VudGVyX3giOjAuNSwiY2VudGVyX3kiOjAuNX19XX0')
RING_PATTERN_YELLOW = canopy.Pattern('CTP-eyJpZCI6InllbGxvdyIsInZlcnNpb24iOjEsIm5hbWUiOiJZZWxsb3ciLCJwYWxldHRlcyI6eyJQYWxldHRlMSI6W1swLFswLjk1NywwLjcyMSwwLjE1M11dXX0sInBhcmFtcyI6e30sImxheWVycyI6W3siZWZmZWN0Ijoic29saWQiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQYWxldHRlMSIsImlucHV0cyI6eyJvZmZzZXQiOjB9fV19')
RING_PATTERN_AMBIENT_RAINBOW = canopy.Pattern("CTP-eyJrZXkiOiJyYWluYm93IiwidmVyc2lvbiI6MCwibmFtZSI6Ik5ldyBQYXR0ZXJuIiwicGFsZXR0ZXMiOnsiUGFsZXR0ZTEiOltbMCxbMSwwLDBdXSxbMC4xNCxbMSwwLjgyNzQ1MDk4MDM5MjE1NjgsMC4xNDExNzY0NzA1ODgyMzUzXV0sWzAuMzEsWzAuMDUwOTgwMzkyMTU2ODYyNzQ0LDEsMF1dLFswLjUyLFswLDAuOTQxMTc2NDcwNTg4MjM1MywwLjg2Mjc0NTA5ODAzOTIxNTddXSxbMC42OCxbMCwwLjI4MjM1Mjk0MTE3NjQ3MDYsMV1dLFswLjgsWzAuNDExNzY0NzA1ODgyMzUyOSwwLDAuODc4NDMxMzcyNTQ5MDE5Nl1dLFswLjg5LFsxLDAsMC44MTU2ODYyNzQ1MDk4MDM5XV0sWzEsWzEsMCwwXV1dfSwicGFyYW1zIjp7fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjEsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6IlBhbGV0dGUxIiwiaW5wdXRzIjp7ImRlbnNpdHkiOjAuNSwib2Zmc2V0Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMzYsIm1pbiI6MCwibWF4IjoxfX19fV19")
TEST_PATTERN = canopy.Pattern('CTP-eyJrZXkiOiJzb2xpZC1yZWQiLCJ2ZXJzaW9uIjowLCJuYW1lIjoic29saWQgcmVkIiwicGFsZXR0ZXMiOnsicHJpbWFyeSI6W1swLFsxLDAsMF1dLFswLjE1LFsxLDEsMF1dLFswLjMsWzAsMSwwXV0sWzAuNSxbMCwxLDFdXSxbMC43LFswLDAsMV1dLFswLjg1LFsxLDAsMV1dLFsxLFsxLDAsMF1dXSwiX2JsYWNrLXdoaXRlIjpbWzAsWzAsMCwwXV0sWzEsWzEsMSwxXV1dfSwicGFyYW1zIjp7InNwZWVkIjowLjEsInNpemUiOiJzcGVlZCIsImRlbnNpdHkiOnsidHlwZSI6InNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzb2xpZCIsIm9wYWNpdHkiOjEsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6InByaW1hcnkiLCJpbnB1dHMiOnsib2Zmc2V0Ijoic3BlZWQifX0seyJlZmZlY3QiOiJncmFkaWVudCIsIm9wYWNpdHkiOjAuNSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoicHJpbWFyeSIsImlucHV0cyI6eyJvZmZzZXQiOiJkZW5zaXR5Iiwic2l6ZSI6MC41LCJyb3RhdGlvbiI6MH19XX0')


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
        self.figurine_audio = FigurineSensorAudio(self.audio)

        # NFC setup
        self.nfc = NfcWrapper(self._tag_found, self._tag_lost)

        # Ring light configuration
        self.pattern_duration = 5.0  # How long to show pattern after tag scan

        # Ring light state
        self.current_pattern = RING_PATTERN_AMBIENT_RAINBOW  # Start with rainbow sparkles
        self.pattern_end_time = 0
        self.sound_end_time = 0  # Track when to stop playing the sound

        # Canopy setup
        self.ring_light_segment = None
        self.led_strand_segment = None
        self.d1_segment = None
        self.params = None

    async def start(self):
        """Initialize and start the system"""
        await self.nfc.start()
        self.audio.start()

        print("Starting LED strips")
        # Initialize three LED data pins - LED1 for ring light, LED2 for LED strand, D1 for test strand
        canopy.init([fern.LED1_DATA, fern.LED2_DATA, fern.D1], self.num_leds)

        # Create segments for rendering
        self.ring_light_segment = canopy.Segment(0, 0, self.num_leds)  # Ring light on LED1_DATA
        self.led_strand_segment = canopy.Segment(1, 0, 100)  # LED strand on LED2_DATA (100 LEDs)
        self.d1_segment = canopy.Segment(2, 0, 100)  # D1 test strand (100 LEDs)
        self.params = canopy.Params()
        print("LED segments created: Ring light, LED strand, and D1 test strand")

        # Start the render loop
        asyncio.create_task(self._render_loop())
        print("Ready to scan RFID tags!")

    async def _tag_found(self, uid):
        """Called when an RFID tag is detected"""
        print(f"Tag scanned: {uid}")

        pattern = self.TAG_PATTERNS.get(uid)
        if pattern:
            self.current_pattern = pattern
            self.pattern_end_time = time.time() + self.pattern_duration
            self.sound_end_time = time.time() + self.pattern_duration  # Play sound for same duration
            self.figurine_audio.play_correct()
            print(f"Playing pattern for tag {uid}")
        else:
            print("Unknown tag - ignoring")

    def _tag_lost(self):
        """Called when tag is removed"""
        print("Tag removed")

    async def _render_loop(self):
        """Main rendering loop - handles ring light LED pattern updates"""
        while True:
            try:
                current_time = time.time()

                # Check if sound period is over - fade out the water sound
                if self.sound_end_time > 0 and current_time > self.sound_end_time:
                    self.sound_end_time = 0
                    asyncio.create_task(self.figurine_audio.fade_out())
                    print("Sound fading out")

                # Check if pattern period is over
                if self.pattern_end_time > 0 and current_time > self.pattern_end_time:
                    self.pattern_end_time = 0
                    self.current_pattern = RING_PATTERN_AMBIENT_RAINBOW
                    print("Pattern complete - back to rainbow sparkles")

                # Update LEDs - all strands react to RFID tags
                canopy.clear()

                # Ring light shows current pattern (RFID triggered or ambient rainbow)
                if self.current_pattern:
                    canopy.draw(self.ring_light_segment, self.current_pattern, params=self.params)

                # LED strand and D1 strand show test pattern when idle, or sync with ring light when RFID scanned
                if self.pattern_end_time > 0:
                    # RFID tag is active - all strands show the same pattern as ring light
                    canopy.draw(self.led_strand_segment, self.current_pattern, params=self.params)
                    canopy.draw(self.d1_segment, self.current_pattern, params=self.params)
                else:
                    # Idle - both LED strand and D1 strand show test pattern
                    canopy.draw(self.led_strand_segment, TEST_PATTERN, params=self.params)
                    canopy.draw(self.d1_segment, TEST_PATTERN, params=self.params)

                canopy.render()

            except Exception as e:
                print(f"Render loop error: {e}")

            await asyncio.sleep(0.05)  # 20 FPS
