"""
Figurine Sensor RFID LED Controller

When an RFID tag is scanned, all LED strands display the corresponding flowing water animation
for 5 seconds with accompanying water sound fade-out, then return to the ambient rainbow sparkle pattern.

Supported RFID tags:
- Red tag (88ab1466080104e0) - Red flowing water animation
- Blue tag (e29f1466080104e0) - Blue flowing water animation
- Purple tag (24941466080104e0) - Purple flowing water animation
- Yellow tag (2bb71466080104e0) - Yellow flowing water animation
"""
import asyncio
import canopy
import fern
import time
from nfc import NfcWrapper
from audio import Audio
from figurine_sensor_audio import FigurineSensorAudio


# LED patterns
PATTERN_RED = canopy.Pattern('CTP-eyJrZXkiOiJyZWQtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJyZWQtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMSwwLDBdXSxbMC41MixbMC45MjE1Njg2Mjc0NTA5ODAzLDAuMTI5NDExNzY0NzA1ODgyMzcsMC41MzcyNTQ5MDE5NjA3ODQzXV0sWzAuOTksWzAsMCwwXV1dLCJfYmxhY2std2hpdGUiOltbMCxbMCwwLDBdXSxbMSxbMSwxLDFdXV19LCJwYXJhbXMiOnsic2l6ZSI6InNwZWVkIiwic3BlZWQiOjAuMSwiZGVuc2l0eSI6eyJ0eXBlIjoicnNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJncmFkaWVudCIsIm9wYWNpdHkiOjAuMjQsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6InByaW1hcnkiLCJpbnB1dHMiOnsib2Zmc2V0IjoiZGVuc2l0eSIsInNpemUiOjAuNSwicm90YXRpb24iOjB9fV19')
PATTERN_BLUE = canopy.Pattern('CTP-eyJrZXkiOiJibHVlLWZsb3ciLCJ2ZXJzaW9uIjowLCJuYW1lIjoiYmx1ZS1mbG93IiwicGFsZXR0ZXMiOnsicHJpbWFyeSI6W1swLjAxLFswLjAxOTYwNzg0MzEzNzI1NDksMCwwLjYzOTIxNTY4NjI3NDUwOThdXSxbMC41MixbMC4xMjk0MTE3NjQ3MDU4ODIzNywwLjUyMTU2ODYyNzQ1MDk4MDQsMC45MjE1Njg2Mjc0NTA5ODAzXV0sWzAuOTksWzAsMCwwXV1dLCJfYmxhY2std2hpdGUiOltbMCxbMCwwLDBdXSxbMSxbMSwxLDFdXV19LCJwYXJhbXMiOnsic2l6ZSI6InNwZWVkIiwic3BlZWQiOjAuMSwiZGVuc2l0eSI6eyJ0eXBlIjoicnNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJncmFkaWVudCIsIm9wYWNpdHkiOjAuMjQsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6InByaW1hcnkiLCJpbnB1dHMiOnsib2Zmc2V0IjoiZGVuc2l0eSIsInNpemUiOjAuNSwicm90YXRpb24iOjB9fV19')
PATTERN_PURPLE = canopy.Pattern('CTP-eyJrZXkiOiJwdXJwbGUtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJwdXJwbGUtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMC41NjQ3MDU4ODIzNTI5NDEyLDAsMV1dLFswLjUyLFswLjc4ODIzNTI5NDExNzY0NywwLjEyOTQxMTc2NDcwNTg4MjM3LDAuOTIxNTY4NjI3NDUwOTgwM11dLFswLjk5LFswLDAsMF1dXSwiX2JsYWNrLXdoaXRlIjpbWzAsWzAsMCwwXV0sWzEsWzEsMSwxXV1dfSwicGFyYW1zIjp7InNpemUiOiJzcGVlZCIsInNwZWVkIjowLjEsImRlbnNpdHkiOnsidHlwZSI6InJzYXciLCJpbnB1dHMiOnsidmFsdWUiOjAuNSwibWluIjowLCJtYXgiOjF9fX0sImxheWVycyI6W3siZWZmZWN0IjoiZ3JhZGllbnQiLCJvcGFjaXR5IjowLjI0LCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJwcmltYXJ5IiwiaW5wdXRzIjp7Im9mZnNldCI6ImRlbnNpdHkiLCJzaXplIjowLjUsInJvdGF0aW9uIjowfX1dfQ')
PATTERN_YELLOW = canopy.Pattern('CTP-eyJrZXkiOiJ5ZWxsb3ctZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJ5ZWxsb3ctZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMSwwLjg2NjY2NjY2NjY2NjY2NjcsMF1dLFswLjMsWzAuNTQ5MDE5NjA3ODQzMTM3MywwLjMwOTgwMzkyMTU2ODYyNzQ2LDAuMDgyMzUyOTQxMTc2NDcwNTldXSxbMC42LFswLjAxMTc2NDcwNTg4MjM1Mjk0MSwwLjAwNzg0MzEzNzI1NDkwMTk2LDAuMDAzOTIxNTY4NjI3NDUwOThdXSxbMC45OSxbMCwwLDBdXV0sIl9ibGFjay13aGl0ZSI6W1swLFswLDAsMF1dLFsxLFsxLDEsMV1dXX0sInBhcmFtcyI6eyJzaXplIjoic3BlZWQiLCJzcGVlZCI6MC4xLCJkZW5zaXR5Ijp7InR5cGUiOiJyc2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjUsIm1pbiI6MCwibWF4IjoxfX19LCJsYXllcnMiOlt7ImVmZmVjdCI6ImdyYWRpZW50Iiwib3BhY2l0eSI6MC4yNCwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoicHJpbWFyeSIsImlucHV0cyI6eyJvZmZzZXQiOiJkZW5zaXR5Iiwic2l6ZSI6MC41LCJyb3RhdGlvbiI6MH19XX0')
PATTERN_AMBIENT_RAINBOW = canopy.Pattern("CTP-eyJrZXkiOiJyYWluYm93IiwidmVyc2lvbiI6MCwibmFtZSI6Ik5ldyBQYXR0ZXJuIiwicGFsZXR0ZXMiOnsiUGFsZXR0ZTEiOltbMCxbMSwwLDBdXSxbMC4xNCxbMSwwLjgyNzQ1MDk4MDM5MjE1NjgsMC4xNDExNzY0NzA1ODgyMzUzXV0sWzAuMzEsWzAuMDUwOTgwMzkyMTU2ODYyNzQ0LDEsMF1dLFswLjUyLFswLDAuOTQxMTc2NDcwNTg4MjM1MywwLjg2Mjc0NTA5ODAzOTIxNTddXSxbMC42OCxbMCwwLjI4MjM1Mjk0MTE3NjQ3MDYsMV1dLFswLjgsWzAuNDExNzY0NzA1ODgyMzUyOSwwLDAuODc4NDMxMzcyNTQ5MDE5Nl1dLFswLjg5LFsxLDAsMC44MTU2ODYyNzQ1MDk4MDM5XV0sWzEsWzEsMCwwXV1dfSwicGFyYW1zIjp7fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjEsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6IlBhbGV0dGUxIiwiaW5wdXRzIjp7ImRlbnNpdHkiOjAuNSwib2Zmc2V0Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMzYsIm1pbiI6MCwibWF4IjoxfX19fV19")

# LED strand color-corrected patterns (compensating for LED strip color imbalance)
# Red channel is very weak on the LED strand, so these patterns boost red significantly
PATTERN_RED_STRAND = canopy.Pattern('CTP-eyJrZXkiOiJyZWQtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJyZWQtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMCwxLDBdXSxbMC41MixbMC4xMjk0MTE3NjQ3MDU4ODIzNywwLjkyMTU2ODYyNzQ1MDk4MDMsMC41MzcyNTQ5MDE5NjA3ODQzXV0sWzAuOTksWzAsMCwwXV1dLCJfYmxhY2std2hpdGUiOltbMCxbMCwwLDBdXSxbMSxbMSwxLDFdXV19LCJwYXJhbXMiOnsic2l6ZSI6InNwZWVkIiwic3BlZWQiOjAuMSwiZGVuc2l0eSI6eyJ0eXBlIjoicnNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJncmFkaWVudCIsIm9wYWNpdHkiOjAuMjQsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6InByaW1hcnkiLCJpbnB1dHMiOnsib2Zmc2V0IjoiZGVuc2l0eSIsInNpemUiOjAuNSwicm90YXRpb24iOjB9fV19')
PATTERN_BLUE_STRAND = canopy.Pattern('CTP-eyJrZXkiOiJibHVlLWZsb3ciLCJ2ZXJzaW9uIjowLCJuYW1lIjoiYmx1ZS1mbG93IiwicGFsZXR0ZXMiOnsicHJpbWFyeSI6W1swLjAxLFswLDAuMDE5NjA3ODQzMTM3MjU0OSwwLjYzOTIxNTY4NjI3NDUwOThdXSxbMC41MixbMC41MjE1Njg2Mjc0NTA5ODA0LDAuMTI5NDExNzY0NzA1ODgyMzcsMC45MjE1Njg2Mjc0NTA5ODAzXV0sWzAuOTksWzAsMCwwXV1dLCJfYmxhY2std2hpdGUiOltbMCxbMCwwLDBdXSxbMSxbMSwxLDFdXV19LCJwYXJhbXMiOnsic2l6ZSI6InNwZWVkIiwic3BlZWQiOjAuMSwiZGVuc2l0eSI6eyJ0eXBlIjoicnNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJncmFkaWVudCIsIm9wYWNpdHkiOjAuMjQsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6InByaW1hcnkiLCJpbnB1dHMiOnsib2Zmc2V0IjoiZGVuc2l0eSIsInNpemUiOjAuNSwicm90YXRpb24iOjB9fV19')
PATTERN_PURPLE_STRAND = canopy.Pattern('CTP-eyJrZXkiOiJwdXJwbGUtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJwdXJwbGUtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMCwwLjU2NDcwNTg4MjM1Mjk0MTIsMV1dLFswLjUyLFswLjEyOTQxMTc2NDcwNTg4MjM3LDAuNzg4MjM1Mjk0MTE3NjQ3LDAuOTIxNTY4NjI3NDUwOTgwM11dLFswLjk5LFswLDAsMF1dXSwiX2JsYWNrLXdoaXRlIjpbWzAsWzAsMCwwXV0sWzEsWzEsMSwxXV1dfSwicGFyYW1zIjp7InNpemUiOiJzcGVlZCIsInNwZWVkIjowLjEsImRlbnNpdHkiOnsidHlwZSI6InJzYXciLCJpbnB1dHMiOnsidmFsdWUiOjAuNSwibWluIjowLCJtYXgiOjF9fX0sImxheWVycyI6W3siZWZmZWN0IjoiZ3JhZGllbnQiLCJvcGFjaXR5IjowLjI0LCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJwcmltYXJ5IiwiaW5wdXRzIjp7Im9mZnNldCI6ImRlbnNpdHkiLCJzaXplIjowLjUsInJvdGF0aW9uIjowfX1dfQ')


class FigurineSensor:
    # RFID tag to pattern mapping (ring light and LED strand versions)
    TAG_PATTERNS_RING = {
        '88ab1466080104e0': PATTERN_RED,
        'e29f1466080104e0': PATTERN_BLUE,
        '24941466080104e0': PATTERN_PURPLE,
        '2bb71466080104e0': PATTERN_YELLOW,
    }

    TAG_PATTERNS_STRAND = {
        '88ab1466080104e0': PATTERN_RED_STRAND,
        'e29f1466080104e0': PATTERN_BLUE_STRAND,
        '24941466080104e0': PATTERN_PURPLE_STRAND,
        '2bb71466080104e0': PATTERN_YELLOW,  # Yellow uses same pattern on both
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

        # LED state
        self.current_pattern_ring = PATTERN_AMBIENT_RAINBOW  # Ring light pattern
        self.current_pattern_strand = PATTERN_AMBIENT_RAINBOW  # LED strand pattern
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

        pattern_ring = self.TAG_PATTERNS_RING.get(uid)
        pattern_strand = self.TAG_PATTERNS_STRAND.get(uid)
        if pattern_ring and pattern_strand:
            self.current_pattern_ring = pattern_ring
            self.current_pattern_strand = pattern_strand
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
        """Main rendering loop - handles LED pattern updates"""
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
                    self.current_pattern_ring = PATTERN_AMBIENT_RAINBOW
                    self.current_pattern_strand = PATTERN_AMBIENT_RAINBOW
                    print("Pattern complete - back to ambient rainbow")

                # Update LEDs
                canopy.clear()

                # Ring light shows current pattern (RFID triggered or ambient rainbow)
                canopy.draw(self.ring_light_segment, self.current_pattern_ring, params=self.params)

                # D1 strand always shows current ring light pattern
                canopy.draw(self.d1_segment, self.current_pattern_ring, params=self.params)

                # LED strand only lights up when RFID is scanned (uses color-corrected pattern)
                if self.pattern_end_time > 0:
                    canopy.draw(self.led_strand_segment, self.current_pattern_strand, params=self.params)

                canopy.render()

            except Exception as e:
                print(f"Render loop error: {e}")

            await asyncio.sleep(0.05)  # 20 FPS
