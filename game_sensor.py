"""
Game Sensor RFID LED Controller

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
from game_sensor_audio import GameSensorAudio
from machine import Pin


# LED patterns
PATTERN_RED = canopy.Pattern('CTP-eyJrZXkiOiJyZWQtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJyZWQtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMSwwLDBdXSxbMC41MixbMC45MjE1Njg2Mjc0NTA5ODAzLDAuMTI5NDExNzY0NzA1ODgyMzcsMC41MzcyNTQ5MDE5NjA3ODQzXV0sWzAuOTksWzAsMCwwXV1dLCJfYmxhY2std2hpdGUiOltbMCxbMCwwLDBdXSxbMSxbMSwxLDFdXV19LCJwYXJhbXMiOnsic2l6ZSI6InNwZWVkIiwic3BlZWQiOjAuMSwiZGVuc2l0eSI6eyJ0eXBlIjoicnNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJncmFkaWVudCIsIm9wYWNpdHkiOjAuMjQsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6InByaW1hcnkiLCJpbnB1dHMiOnsib2Zmc2V0IjoiZGVuc2l0eSIsInNpemUiOjAuNSwicm90YXRpb24iOjB9fV19')
PATTERN_BLUE = canopy.Pattern('CTP-eyJrZXkiOiJibHVlLWZsb3ciLCJ2ZXJzaW9uIjowLCJuYW1lIjoiYmx1ZS1mbG93IiwicGFsZXR0ZXMiOnsicHJpbWFyeSI6W1swLjAxLFswLjAxOTYwNzg0MzEzNzI1NDksMCwwLjYzOTIxNTY4NjI3NDUwOThdXSxbMC41MixbMC4xMjk0MTE3NjQ3MDU4ODIzNywwLjUyMTU2ODYyNzQ1MDk4MDQsMC45MjE1Njg2Mjc0NTA5ODAzXV0sWzAuOTksWzAsMCwwXV1dLCJfYmxhY2std2hpdGUiOltbMCxbMCwwLDBdXSxbMSxbMSwxLDFdXV19LCJwYXJhbXMiOnsic2l6ZSI6InNwZWVkIiwic3BlZWQiOjAuMSwiZGVuc2l0eSI6eyJ0eXBlIjoicnNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJncmFkaWVudCIsIm9wYWNpdHkiOjAuMjQsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6InByaW1hcnkiLCJpbnB1dHMiOnsib2Zmc2V0IjoiZGVuc2l0eSIsInNpemUiOjAuNSwicm90YXRpb24iOjB9fV19')
PATTERN_PURPLE = canopy.Pattern('CTP-eyJrZXkiOiJwdXJwbGUtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJwdXJwbGUtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMC41NjQ3MDU4ODIzNTI5NDEyLDAsMV1dLFswLjUyLFswLjc4ODIzNTI5NDExNzY0NywwLjEyOTQxMTc2NDcwNTg4MjM3LDAuOTIxNTY4NjI3NDUwOTgwM11dLFswLjk5LFswLDAsMF1dXSwiX2JsYWNrLXdoaXRlIjpbWzAsWzAsMCwwXV0sWzEsWzEsMSwxXV1dfSwicGFyYW1zIjp7InNpemUiOiJzcGVlZCIsInNwZWVkIjowLjEsImRlbnNpdHkiOnsidHlwZSI6InJzYXciLCJpbnB1dHMiOnsidmFsdWUiOjAuNSwibWluIjowLCJtYXgiOjF9fX0sImxheWVycyI6W3siZWZmZWN0IjoiZ3JhZGllbnQiLCJvcGFjaXR5IjowLjI0LCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJwcmltYXJ5IiwiaW5wdXRzIjp7Im9mZnNldCI6ImRlbnNpdHkiLCJzaXplIjowLjUsInJvdGF0aW9uIjowfX1dfQ')
PATTERN_YELLOW = canopy.Pattern('CTP-eyJrZXkiOiJ5ZWxsb3ctZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJ5ZWxsb3ctZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMSwwLjg2NjY2NjY2NjY2NjY2NjcsMF1dLFswLjMsWzAuNTQ5MDE5NjA3ODQzMTM3MywwLjMwOTgwMzkyMTU2ODYyNzQ2LDAuMDgyMzUyOTQxMTc2NDcwNTldXSxbMC42LFswLjAxMTc2NDcwNTg4MjM1Mjk0MSwwLjAwNzg0MzEzNzI1NDkwMTk2LDAuMDAzOTIxNTY4NjI3NDUwOThdXSxbMC45OSxbMCwwLDBdXV0sIl9ibGFjay13aGl0ZSI6W1swLFswLDAsMF1dLFsxLFsxLDEsMV1dXX0sInBhcmFtcyI6eyJzaXplIjoic3BlZWQiLCJzcGVlZCI6MC4xLCJkZW5zaXR5Ijp7InR5cGUiOiJyc2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjUsIm1pbiI6MCwibWF4IjoxfX19LCJsYXllcnMiOlt7ImVmZmVjdCI6ImdyYWRpZW50Iiwib3BhY2l0eSI6MC4yNCwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoicHJpbWFyeSIsImlucHV0cyI6eyJvZmZzZXQiOiJkZW5zaXR5Iiwic2l6ZSI6MC41LCJyb3RhdGlvbiI6MH19XX0')
PATTERN_AMBIENT_RAINBOW = canopy.Pattern("CTP-eyJrZXkiOiJyYWluYm93IiwidmVyc2lvbiI6MCwibmFtZSI6Ik5ldyBQYXR0ZXJuIiwicGFsZXR0ZXMiOnsiUGFsZXR0ZTEiOltbMCxbMSwwLDBdXSxbMC4xNSxbMCwwLDBdXSxbMC4yOSxbMSwwLjgyNzQ1MDk4MDM5MjE1NjgsMC4xNDExNzY0NzA1ODgyMzUzXV0sWzAuNDMsWzAsMCwwXV0sWzAuNTksWzAuMDc0NTA5ODAzOTIxNTY4NjMsMC42MzEzNzI1NDkwMTk2MDc4LDBdXSxbMC43MyxbMCwwLDBdXSxbMC44NyxbMC4zMzcyNTQ5MDE5NjA3ODQzNCwwLDAuNDU4ODIzNTI5NDExNzY0N11dLFsxLFswLDAsMF1dXX0sInBhcmFtcyI6e30sImxheWVycyI6W3siZWZmZWN0Ijoic3BhcmtsZXMiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQYWxldHRlMSIsImlucHV0cyI6eyJkZW5zaXR5IjowLjUsIm9mZnNldCI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjM2LCJtaW4iOjAsIm1heCI6MX19fX1dfQ")

PATTERN_GAME_ON = canopy.Pattern('CTP-eyJrZXkiOiJnYW1lLW9uIiwidmVyc2lvbiI6MCwibmFtZSI6ImdhbWUtb24iLCJwYWxldHRlcyI6eyJwcmltYXJ5IjpbWzAsWzEsMCwwXV0sWzAuMjEsWzEsMCwwXV0sWzAuMjEsWzAuMjgyMzUyOTQxMTc2NDcwNiwxLDBdXSxbMC40NSxbMC4xMTM3MjU0OTAxOTYwNzg0MywwLjQ1ODgyMzUyOTQxMTc2NDcsMF1dLFswLjQ2LFswLjc2NDcwNTg4MjM1Mjk0MTEsMCwxXV0sWzAuNjIsWzAuNDUwOTgwMzkyMTU2ODYyNzUsMC4xNjQ3MDU4ODIzNTI5NDExNywwLjQ1MDk4MDM5MjE1Njg2Mjc1XV0sWzAuNzUsWzAuNTYsMC4xMywwLjM2XV0sWzAuNzYsWzAuNjcwNTg4MjM1Mjk0MTE3NiwwLjY0MzEzNzI1NDkwMTk2MDgsMC4xMDE5NjA3ODQzMTM3MjU0OV1dLFswLjk4LFswLjk2LDAuNzMsMC4wMV1dLFsxLFsxLDAsMC4xNjg2Mjc0NTA5ODAzOTIxN11dXSwiX2JsYWNrLXdoaXRlIjpbWzAsWzAsMCwwXV0sWzEsWzEsMSwxXV1dfSwicGFyYW1zIjp7InNwZWVkIjowLjEsInNpemUiOiJzcGVlZCIsImRlbnNpdHkiOnsidHlwZSI6InNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC4xNSwibWluIjowLCJtYXgiOjF9fX0sImxheWVycyI6W3siZWZmZWN0Ijoic29saWQiLCJvcGFjaXR5IjowLjUsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6InByaW1hcnkiLCJpbnB1dHMiOnsib2Zmc2V0IjoiZGVuc2l0eSJ9fV19')

# LED strand color-corrected patterns (compensating for LED strip color imbalance)
# Red channel is very weak on the LED strand, so these patterns boost red significantly
PATTERN_RED_STRAND = canopy.Pattern('CTP-eyJrZXkiOiJyZWQtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJyZWQtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMCwxLDBdXSxbMC4yMixbMC4xMjk0MTE3NjQ3MDU4ODIzNywwLjkyMTU2ODYyNzQ1MDk4MDMsMC41MzcyNTQ5MDE5NjA3ODQzXV0sWzAuNDgsWzAsMCwwXV0sWzAuOTksWzAsMCwwXV1dLCJfYmxhY2std2hpdGUiOltbMCxbMCwwLDBdXSxbMSxbMSwxLDFdXV19LCJwYXJhbXMiOnsic2l6ZSI6InNwZWVkIiwic3BlZWQiOjAuMSwiZGVuc2l0eSI6eyJ0eXBlIjoicnNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJncmFkaWVudCIsIm9wYWNpdHkiOjAuMjQsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6InByaW1hcnkiLCJpbnB1dHMiOnsib2Zmc2V0IjoiZGVuc2l0eSIsInNpemUiOjAuMjMsInJvdGF0aW9uIjowfX1dfQ')
PATTERN_BLUE_STRAND = canopy.Pattern('CTP-eyJrZXkiOiJyZWQtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJyZWQtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMCwwLjA5ODAzOTIxNTY4NjI3NDUxLDAuNTgwMzkyMTU2ODYyNzQ1MV1dLFswLjIyLFswLjIyMzUyOTQxMTc2NDcwNTksMC4xMjk0MTE3NjQ3MDU4ODIzNywwLjkyMTU2ODYyNzQ1MDk4MDNdXSxbMC40OCxbMCwwLDBdXSxbMC45OSxbMCwwLDBdXV0sIl9ibGFjay13aGl0ZSI6W1swLFswLDAsMF1dLFsxLFsxLDEsMV1dXX0sInBhcmFtcyI6eyJzaXplIjoic3BlZWQiLCJzcGVlZCI6MC4xLCJkZW5zaXR5Ijp7InR5cGUiOiJyc2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjUsIm1pbiI6MCwibWF4IjoxfX19LCJsYXllcnMiOlt7ImVmZmVjdCI6ImdyYWRpZW50Iiwib3BhY2l0eSI6MC4yNCwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoicHJpbWFyeSIsImlucHV0cyI6eyJvZmZzZXQiOiJkZW5zaXR5Iiwic2l6ZSI6MC4yMywicm90YXRpb24iOjB9fV19')
PATTERN_PURPLE_STRAND = canopy.Pattern('CTP-eyJrZXkiOiJyZWQtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJyZWQtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMCwwLjQ5NDExNzY0NzA1ODgyMzU1LDAuNTgwMzkyMTU2ODYyNzQ1MV1dLFswLjIxLFswLjEyOTQxMTc2NDcwNTg4MjM3LDAuNjMxMzcyNTQ5MDE5NjA3OCwwLjkyMTU2ODYyNzQ1MDk4MDNdXSxbMC40OCxbMCwwLDBdXSxbMC45OSxbMCwwLDBdXV0sIl9ibGFjay13aGl0ZSI6W1swLFswLDAsMF1dLFsxLFsxLDEsMV1dXX0sInBhcmFtcyI6eyJzaXplIjoic3BlZWQiLCJzcGVlZCI6MC4xLCJkZW5zaXR5Ijp7InR5cGUiOiJyc2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjUsIm1pbiI6MCwibWF4IjoxfX19LCJsYXllcnMiOlt7ImVmZmVjdCI6ImdyYWRpZW50Iiwib3BhY2l0eSI6MC4yNCwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoicHJpbWFyeSIsImlucHV0cyI6eyJvZmZzZXQiOiJkZW5zaXR5Iiwic2l6ZSI6MC4yMywicm90YXRpb24iOjB9fV19')
PATTERN_YELLOW_STRAND = canopy.Pattern('CTP-eyJrZXkiOiJyZWQtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJyZWQtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMixbMC41ODAzOTIxNTY4NjI3NDUxLDAuMzM3MjU0OTAxOTYwNzg0MzQsMF1dLFswLjIxLFswLjg2NjY2NjY2NjY2NjY2NjcsMSwwXV0sWzAuNDgsWzAsMCwwXV0sWzAuOTksWzAsMCwwXV1dLCJfYmxhY2std2hpdGUiOltbMCxbMCwwLDBdXSxbMSxbMSwxLDFdXV19LCJwYXJhbXMiOnsic2l6ZSI6InNwZWVkIiwic3BlZWQiOjAuMSwiZGVuc2l0eSI6eyJ0eXBlIjoicnNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJncmFkaWVudCIsIm9wYWNpdHkiOjAuMjQsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6InByaW1hcnkiLCJpbnB1dHMiOnsib2Zmc2V0IjoiZGVuc2l0eSIsInNpemUiOjAuMjMsInJvdGF0aW9uIjowfX1dfQ')


class GameSensor:
    # RFID tag to pattern mapping and strand assignment
    # Each tag triggers its pattern on the ring light and one specific strand
    TAG_PATTERNS = {
        '88ab1466080104e0': {  # Red tag
            'ring': PATTERN_RED,
            'strand': PATTERN_RED_STRAND,
            'strand_index': 0,  # LED2_DATA
        },
        'e29f1466080104e0': {  # Blue tag
            'ring': PATTERN_BLUE,
            'strand': PATTERN_BLUE_STRAND,
            'strand_index': 1,  # D1
        },
        '24941466080104e0': {  # Purple tag
            'ring': PATTERN_PURPLE,
            'strand': PATTERN_PURPLE_STRAND,
            'strand_index': 2,  # D5
        },
        '2bb71466080104e0': {  # Yellow tag
            'ring': PATTERN_YELLOW,
            'strand': PATTERN_YELLOW_STRAND,
            'strand_index': 3,  # D3
        },
        '484e1466080104e0': {  # Hourglass tag 1 - Game On pattern
            'ring': PATTERN_GAME_ON,
            'strand': None,
            'strand_index': -1,  # No strand
            'duration': 300,  # 5 minutes (300 seconds)
            'music_duration': 300,  # 5 minutes (music duration)
        },
        'bc591466080104e0': {  # Hourglass tag 2 - Game On pattern
            'ring': PATTERN_GAME_ON,
            'strand': None,
            'strand_index': -1,  # No strand
            'duration': 300,  # 5 minutes (300 seconds)
            'music_duration': 300,  # 5 minutes (music duration)
        },
    }

    def __init__(self, name="game_sensor"):
        self.name = name
        self.num_leds_ring = 16  # Ring light has 16 LEDs
        self.num_leds_strand = 400  # LED strand has 400 LEDs

        # Audio setup
        self.audio = Audio()
        self.game_audio = GameSensorAudio(self.audio)

        # NFC setup
        self.nfc = NfcWrapper(self._tag_found, self._tag_lost)

        # Button setup on D2 pin (D1 is used for LED strand data)
        self.button = Pin(fern.D2, Pin.IN, Pin.PULL_UP)
        self.button_press_count = 0
        self.button_was_pressed = False

        # Ring light configuration
        self.pattern_duration = 10.0  # How long to show pattern after tag scan

        # LED state
        self.current_pattern_ring = PATTERN_AMBIENT_RAINBOW  # Ring light pattern
        self.current_pattern_strand = PATTERN_AMBIENT_RAINBOW  # LED strand pattern
        self.active_strand_index = -1  # Which strand should be lit (-1 means none)
        self.pattern_end_time = 0
        self.sound_end_time = 0  # Track when to stop playing the sound
        self.pattern_start_time = 0  # Track when pattern started for brightness scaling
        self.brightness_scale = 1.0  # Scale factor for LED brightness (0.0 to 1.0)

        # Canopy setup
        self.ring_light_segment = None
        self.strand_segments = []  # LED2_DATA, D1, D2, D3 strands
        self.params = None

    async def start(self):
        """Initialize and start the system"""
        await self.nfc.start()
        self.audio.start()

        print("Starting LED strips")
        # Initialize 6 LED data pins - LED1_DATA for ring light, LED2_DATA/D1/D5/D3 for color strands, D6 for ambient rainbow
        # Use max LED count for initialization
        max_leds = max(self.num_leds_ring, self.num_leds_strand)
        canopy.init([fern.LED1_DATA, fern.LED2_DATA, fern.D1, fern.D5, fern.D3, fern.D6], max_leds)

        # Create segments for rendering
        self.ring_light_segment = canopy.Segment(0, 0, self.num_leds_ring)  # Ring light on LED1_DATA (16 LEDs)
        self.strand_segments = [
            canopy.Segment(1, 0, self.num_leds_strand),  # Red strand on LED2_DATA (400 LEDs)
            canopy.Segment(2, 0, self.num_leds_strand),  # Blue strand on D1 (400 LEDs)
            canopy.Segment(3, 0, self.num_leds_strand),  # Purple strand on D5 (400 LEDs)
            canopy.Segment(4, 0, self.num_leds_strand),  # Yellow strand on D3 (400 LEDs)
        ]
        self.ambient_strand_segment = canopy.Segment(5, 0, self.num_leds_strand)  # Game On pattern strand on D6 (400 LEDs)
        self.params = canopy.Params()
        print(f"LED segments created: Ring light on LED1_DATA ({self.num_leds_ring} LEDs), 4 color strands on LED2_DATA/D1/D5/D3 ({self.num_leds_strand} LEDs each), Game On strand on D6 ({self.num_leds_strand} LEDs)")

        # Start the render loop
        asyncio.create_task(self._render_loop())
        print("Ready to scan RFID tags!")

    async def _tag_found(self, uid):
        """Called when an RFID tag is detected"""
        print(f"Tag scanned: {uid}")

        tag_config = self.TAG_PATTERNS.get(uid)
        if tag_config:
            self.current_pattern_ring = tag_config['ring']
            self.current_pattern_strand = tag_config['strand']
            self.active_strand_index = tag_config['strand_index']
            # Use custom duration if provided, otherwise use default pattern_duration
            duration = tag_config.get('duration', self.pattern_duration)
            self.pattern_start_time = time.time()
            self.pattern_end_time = self.pattern_start_time + duration

            # Check if this is a hourglass tag (has music_duration set)
            if 'music_duration' in tag_config:
                # Hourglass tag - play music for specified duration (5 minutes = 300 seconds)
                self.sound_end_time = time.time() + tag_config['music_duration']
            else:
                self.sound_end_time = time.time() + duration

            # Play the game music
            self.game_audio.play_correct()
            print(f"Playing pattern for tag {uid} on strand {self.active_strand_index} for {duration}s")
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

                # Check button press with debouncing
                button_is_pressed = self.button.value() == 0  # Button pressed (LOW when pushed with PULL_UP)
                if button_is_pressed and not self.button_was_pressed:
                    # Button transitioned from not pressed to pressed
                    self.button_press_count += 1
                    print(f"Button pressed! Count: {self.button_press_count}")
                    # Turn ring light to yellow pattern for 5 seconds
                    self.current_pattern_ring = PATTERN_YELLOW
                    self.pattern_end_time = time.time() + 5.0
                self.button_was_pressed = button_is_pressed

                # Check if sound period is over - fade out the water sound
                if self.sound_end_time > 0 and current_time > self.sound_end_time:
                    self.sound_end_time = 0
                    asyncio.create_task(self.game_audio.fade_out())
                    print("Sound fading out")

                # Check if pattern period is over
                if self.pattern_end_time > 0 and current_time > self.pattern_end_time:
                    self.pattern_end_time = 0
                    self.active_strand_index = -1  # Turn off all strands
                    self.current_pattern_ring = PATTERN_AMBIENT_RAINBOW
                    self.current_pattern_strand = PATTERN_AMBIENT_RAINBOW
                    print("Pattern complete - back to ambient rainbow")

                # Update LEDs
                canopy.clear()

                # Ring light shows current pattern (RFID triggered or ambient rainbow)
                canopy.draw(self.ring_light_segment, self.current_pattern_ring, params=self.params)

                # Game On pattern strand on D6 always displays
                canopy.draw(self.ambient_strand_segment, PATTERN_GAME_ON, params=self.params)

                # Only the active strand lights up when RFID is scanned
                if self.pattern_end_time > 0 and self.active_strand_index >= 0:
                    canopy.draw(self.strand_segments[self.active_strand_index], self.current_pattern_strand, params=self.params)

                canopy.render()

            except Exception as e:
                print(f"Render loop error: {e}")

            await asyncio.sleep(0.05)  # 20 FPS
