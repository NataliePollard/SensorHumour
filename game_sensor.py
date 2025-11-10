"""
Game Sensor RFID LED Controller

Hourglass Game Experience:
- Scan hourglass tag to start 5-minute game
- Press button 1-4 to win and display color (red, blue, purple, yellow)
- Press button 5 to turn off lights
- When game is won, music stops and the matching color pattern displays on ring and both strands

Hardware:
- Ring light: 16 LEDs on LED1_DATA
- Game strands: 200 LEDs each on D6 and D7 (same pattern on both)
- Buttons: D1, D2, D3, D4, D5

Supported RFID tags:
- Hourglass tag 1 (484e1466080104e0) - Start game
- Hourglass tag 2 (bc591466080104e0) - Start game
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

PATTERN_RED_STRAND = canopy.Pattern('CTP-eyJrZXkiOiJyZWQtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJyZWQtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMCwxLDBdXSxbMC4yMixbMC4xMjk0MTE3NjQ3MDU4ODIzNywwLjkyMTU2ODYyNzQ1MDk4MDMsMC41MzcyNTQ5MDE5NjA3ODQzXV0sWzAuNDgsWzAsMCwwXV0sWzAuOTksWzAsMCwwXV1dLCJfYmxhY2std2hpdGUiOltbMCxbMCwwLDBdXSxbMSxbMSwxLDFdXV19LCJwYXJhbXMiOnsic2l6ZSI6InNwZWVkIiwic3BlZWQiOjAuMSwiZGVuc2l0eSI6eyJ0eXBlIjoicnNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJncmFkaWVudCIsIm9wYWNpdHkiOjAuMjQsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6InByaW1hcnkiLCJpbnB1dHMiOnsib2Zmc2V0IjoiZGVuc2l0eSIsInNpemUiOjAuMjMsInJvdGF0aW9uIjowfX1dfQ')
PATTERN_BLUE_STRAND = canopy.Pattern('CTP-eyJrZXkiOiJyZWQtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJyZWQtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMCwwLjA5ODAzOTIxNTY4NjI3NDUxLDAuNTgwMzkyMTU2ODYyNzQ1MV1dLFswLjIyLFswLjIyMzUyOTQxMTc2NDcwNTksMC4xMjk0MTE3NjQ3MDU4ODIzNywwLjkyMTU2ODYyNzQ1MDk4MDNdXSxbMC40OCxbMCwwLDBdXSxbMC45OSxbMCwwLDBdXV0sIl9ibGFjay13aGl0ZSI6W1swLFswLDAsMF1dLFsxLFsxLDEsMV1dXX0sInBhcmFtcyI6eyJzaXplIjoic3BlZWQiLCJzcGVlZCI6MC4xLCJkZW5zaXR5Ijp7InR5cGUiOiJyc2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjUsIm1pbiI6MCwibWF4IjoxfX19LCJsYXllcnMiOlt7ImVmZmVjdCI6ImdyYWRpZW50Iiwib3BhY2l0eSI6MC4yNCwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoicHJpbWFyeSIsImlucHV0cyI6eyJvZmZzZXQiOiJkZW5zaXR5Iiwic2l6ZSI6MC4yMywicm90YXRpb24iOjB9fV19')
PATTERN_PURPLE_STRAND = canopy.Pattern('CTP-eyJrZXkiOiJyZWQtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJyZWQtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMCwwLjQ5NDExNzY0NzA1ODgyMzU1LDAuNTgwMzkyMTU2ODYyNzQ1MV1dLFswLjIxLFswLjEyOTQxMTc2NDcwNTg4MjM3LDAuNjMxMzcyNTQ5MDE5NjA3OCwwLjkyMTU2ODYyNzQ1MDk4MDNdXSxbMC40OCxbMCwwLDBdXSxbMC45OSxbMCwwLDBdXV0sIl9ibGFjay13aGl0ZSI6W1swLFswLDAsMF1dLFsxLFsxLDEsMV1dXX0sInBhcmFtcyI6eyJzaXplIjoic3BlZWQiLCJzcGVlZCI6MC4xLCJkZW5zaXR5Ijp7InR5cGUiOiJyc2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjUsIm1pbiI6MCwibWF4IjoxfX19LCJsYXllcnMiOlt7ImVmZmVjdCI6ImdyYWRpZW50Iiwib3BhY2l0eSI6MC4yNCwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoicHJpbWFyeSIsImlucHV0cyI6eyJvZmZzZXQiOiJkZW5zaXR5Iiwic2l6ZSI6MC4yMywicm90YXRpb24iOjB9fV19')
PATTERN_YELLOW_STRAND = canopy.Pattern('CTP-eyJrZXkiOiJyZWQtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJyZWQtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMixbMC41ODAzOTIxNTY4NjI3NDUxLDAuMzM3MjU0OTAxOTYwNzg0MzQsMF1dLFswLjIxLFswLjg2NjY2NjY2NjY2NjY2NjcsMSwwXV0sWzAuNDgsWzAsMCwwXV0sWzAuOTksWzAsMCwwXV1dLCJfYmxhY2std2hpdGUiOltbMCxbMCwwLDBdXSxbMSxbMSwxLDFdXV19LCJwYXJhbXMiOnsic2l6ZSI6InNwZWVkIiwic3BlZWQiOjAuMSwiZGVuc2l0eSI6eyJ0eXBlIjoicnNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJncmFkaWVudCIsIm9wYWNpdHkiOjAuMjQsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6InByaW1hcnkiLCJpbnB1dHMiOnsib2Zmc2V0IjoiZGVuc2l0eSIsInNpemUiOjAuMjMsInJvdGF0aW9uIjowfX1dfQ')


class GameSensor:
    """
    Hourglass Game System:
    - Two hourglass tags trigger a 5-minute game with music
    - Ring light (16 LEDs) and two game strands on D6/D7 (200 LEDs each)
    - Both game strands always display the same pattern
    - 5 buttons (D1-D5) for game interaction:
      D1 = Red win pattern
      D2 = Blue win pattern
      D3 = Purple win pattern
      D4 = Yellow win pattern
      D5 = Turn off lights
    """
    TAG_PATTERNS = {
        '484e1466080104e0': {  # Hourglass tag 1 - Game On pattern
            'ring': PATTERN_GAME_ON,
            'duration': 300,  # 5 minutes (300 seconds)
            'music_duration': 300,  # 5 minutes (music duration)
        },
        'bc591466080104e0': {  # Hourglass tag 2 - Game On pattern
            'ring': PATTERN_GAME_ON,
            'duration': 300,  # 5 minutes (300 seconds)
            'music_duration': 300,  # 5 minutes (music duration)
        },
    }

    def __init__(self):
        self.num_leds_ring = 16  # Ring light has 16 LEDs
        self.num_leds_strand = 200  # LED strands on D6 and D7 have 200 LEDs each

        # Audio setup
        self.audio = Audio()
        self.game_audio = GameSensorAudio(self.audio)

        # NFC setup
        self.nfc = NfcWrapper(self._tag_found, self._tag_lost)

        # Button setup - 5 game buttons (D1, D2, D3, D4, D5)
        self.button_pins = {
            'D1': Pin(fern.D1, Pin.IN, Pin.PULL_UP),   # Button 1 - Red
            'D2': Pin(fern.D2, Pin.IN, Pin.PULL_UP),   # Button 2 - Blue
            'D3': Pin(fern.D3, Pin.IN, Pin.PULL_UP),   # Button 3 - Purple
            'D4': Pin(fern.D4, Pin.IN, Pin.PULL_UP),   # Button 4 - Yellow
            'D5': Pin(fern.D5, Pin.IN, Pin.PULL_UP),   # Button 5 - Off
        }
        self.button_was_pressed = {pin: False for pin in self.button_pins}

        # Game state
        self.is_game_active = False  # True when hourglass tag has been scanned within 5 minutes

        # LED state
        self.current_pattern_ring = PATTERN_AMBIENT_RAINBOW  # Ring light pattern
        self.pattern_end_time = 0
        self.sound_end_time = 0  # Track when to stop playing the sound
        self.win_pattern = None  # Pattern to display on D6/D7 when game is won

        # Canopy setup
        self.ring_light_segment = None
        self.params = None

    async def start(self):
        """Initialize and start the system"""
        await self.nfc.start()
        self.audio.start()

        print("Starting LED strips")
        # Initialize 8 LED data pins - LED1_DATA for ring light, LED2_DATA/D6/D7 for color strands, D6 for game on
        # D1, D2, D3, D4, D5 are used for game buttons
        # Use max LED count for initialization
        max_leds = max(self.num_leds_ring, self.num_leds_strand)
        canopy.init([fern.LED1_DATA, fern.LED2_DATA, fern.D6, fern.D7], max_leds)

        # Create segments for rendering
        self.ring_light_segment = canopy.Segment(0, 0, self.num_leds_ring)  # Ring light on LED1_DATA (16 LEDs)
        self.game_strand_d6_segment = canopy.Segment(2, 0, self.num_leds_strand)  # Game strand on D6 (200 LEDs)
        self.game_strand_d7_segment = canopy.Segment(3, 0, self.num_leds_strand)  # Game strand on D7 (200 LEDs)
        self.params = canopy.Params()
        print(f"LED segments created: Ring light on LED1_DATA ({self.num_leds_ring} LEDs), Game strands on D6/D7 ({self.num_leds_strand} LEDs each)")

        # Start the render loop
        asyncio.create_task(self._render_loop())
        print("Ready to scan RFID tags!")

    async def _tag_found(self, uid):
        """Called when an RFID tag is detected"""
        print(f"Tag scanned: {uid}")

        tag_config = self.TAG_PATTERNS.get(uid)
        if tag_config:
            self.current_pattern_ring = tag_config['ring']
            duration = tag_config['duration']
            self.pattern_end_time = time.time() + duration

            # Check if this is a hourglass tag (has music_duration set)
            if 'music_duration' in tag_config:
                # Hourglass tag - play music for specified duration (5 minutes = 300 seconds)
                self.sound_end_time = time.time() + tag_config['music_duration']
                self.is_game_active = True  # Game buttons are now active
                print("Game is now ACTIVE! Press buttons to win!")

            # Play the game music
            self.game_audio.play_correct()
            print(f"Playing pattern for tag {uid} for {duration}s")
        else:
            print("Unknown tag - ignoring")

    def _tag_lost(self):
        """Called when tag is removed"""
        print("Tag removed")

    async def _handle_game_win(self, button_name):
        """Handle game win condition - stop music and display color for 5 seconds"""
        print(f"GAME WON via {button_name}!")
        self.is_game_active = False

        # Stop the music immediately
        asyncio.create_task(self.game_audio.fade_out())
        self.sound_end_time = 0

        # Set the pattern based on which button was pressed
        button_to_pattern = {
            'D1': (PATTERN_RED, PATTERN_RED_STRAND),        # Button 1 - Red
            'D2': (PATTERN_BLUE, PATTERN_BLUE_STRAND),      # Button 2 - Blue
            'D3': (PATTERN_PURPLE, PATTERN_PURPLE_STRAND),  # Button 3 - Purple
            'D4': (PATTERN_YELLOW, PATTERN_YELLOW_STRAND),  # Button 4 - Yellow
            'D5': (None, None),                              # Button 5 - Off
        }

        ring_pattern, strand_pattern = button_to_pattern.get(button_name, (PATTERN_AMBIENT_RAINBOW, PATTERN_AMBIENT_RAINBOW))

        self.current_pattern_ring = ring_pattern if ring_pattern else None
        self.win_pattern = strand_pattern
        self.pattern_end_time = time.time() + 5  # Display win pattern for 5 seconds

    async def _render_loop(self):
        """Main rendering loop - handles LED pattern updates"""
        while True:
            try:
                current_time = time.time()

                # Check all 5 game buttons with debouncing
                if self.is_game_active:
                    for button_name, button_pin in self.button_pins.items():
                        button_is_pressed = button_pin.value() == 0  # Button pressed (LOW when pushed with PULL_UP)
                        if button_is_pressed and not self.button_was_pressed[button_name]:
                            # Button transitioned from not pressed to pressed
                            print(f"Button {button_name} pressed!")
                            await self._handle_game_win(button_name)
                        self.button_was_pressed[button_name] = button_is_pressed

                # Check if sound period is over - fade out the water sound
                if self.sound_end_time > 0 and current_time > self.sound_end_time:
                    self.sound_end_time = 0
                    asyncio.create_task(self.game_audio.fade_out())
                    print("Sound fading out")

                # Check if pattern period is over
                if self.pattern_end_time > 0 and current_time > self.pattern_end_time:
                    self.pattern_end_time = 0
                    self.current_pattern_ring = PATTERN_AMBIENT_RAINBOW
                    self.win_pattern = None  # Clear win pattern after timeout
                    print("Pattern complete - back to ambient rainbow")

                # Update LEDs
                canopy.clear()

                # Ring light shows current pattern (RFID triggered or ambient rainbow)
                if self.current_pattern_ring:
                    canopy.draw(self.ring_light_segment, self.current_pattern_ring, params=self.params)

                # D6 and D7 strands - show game win pattern or game on pattern
                if self.win_pattern:
                    # Game was won - display the win pattern on both D6 and D7
                    canopy.draw(self.game_strand_d6_segment, self.win_pattern, params=self.params)
                    canopy.draw(self.game_strand_d7_segment, self.win_pattern, params=self.params)
                else:
                    # Game is running or ambient - display appropriate pattern
                    canopy.draw(self.game_strand_d6_segment, PATTERN_AMBIENT_RAINBOW, params=self.params)
                    canopy.draw(self.game_strand_d7_segment, PATTERN_AMBIENT_RAINBOW, params=self.params)

                canopy.render()

            except Exception as e:
                print(f"Render loop error: {e}")

            await asyncio.sleep(0.05)  # 20 FPS
