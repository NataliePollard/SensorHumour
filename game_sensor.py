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

PATTERN_GAME_ON = canopy.Pattern('CTP-eyJrZXkiOiJnYW1lLW9uIiwidmVyc2lvbiI6MCwibmFtZSI6ImdhbWUtb24iLCJwYWxldHRlcyI6eyJwcmltYXJ5IjpbWzAuMDEsWzEsMCwwXV0sWzAuMzMsWzEsMC44NjcsMF1dLFswLjY2LFswLDAsMV1dLFswLjk5LFswLjU2NSwwLDFdXV0sIl9ibGFjay13aGl0ZSI6W1swLFswLDAsMF1dLFsxLFsxLDEsMV1dXX0sInBhcmFtcyI6eyJzaXplIjoic3BlZWQiLCJzcGVlZCI6MC4xLCJkZW5zaXR5Ijp7InR5cGUiOiJyc2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjUsIm1pbiI6MCwibWF4IjoxfX19LCJsYXllcnMiOlt7ImVmZmVjdCI6ImdyYWRpZW50Iiwib3BhY2l0eSI6MC4yNCwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoicHJpbWFyeSIsImlucHV0cyI6eyJvZmZzZXQiOiJkZW5zaXR5Iiwic2l6ZSI6MC41LCJyb3RhdGlvbiI6MH19XX0=')
PATTERN_GAME_ON_D6D7 = canopy.Pattern('CTP-eyJrZXkiOiJnYW1lLW9uIiwidmVyc2lvbiI6MCwibmFtZSI6ImdhbWUtb24iLCJwYWxldHRlcyI6eyJwcmltYXJ5IjpbWzAuMDEsWzEsMCwwXV0sWzAuMzMsWzAuNTY1LDAsMV1dLFswLjY2LFswLDEsMF1dLFswLjk5LFsxLDAuODY3LDBdXV0sIl9ibGFjay13aGl0ZSI6W1swLFswLDAsMF1dLFsxLFsxLDEsMV1dXX0sInBhcmFtcyI6eyJzaXplIjoic3BlZWQiLCJzcGVlZCI6MC4xLCJkZW5zaXR5Ijp7InR5cGUiOiJyc2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjUsIm1pbiI6MCwibWF4IjoxfX19LCJsYXllcnMiOlt7ImVmZmVjdCI6ImdyYWRpZW50Iiwib3BhY2l0eSI6MC4yNCwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoicHJpbWFyeSIsImlucHV0cyI6eyJvZmZzZXQiOiJkZW5zaXR5Iiwic2l6ZSI6MC41LCJyb3RhdGlvbiI6MH19XX0=')

# Fast sparkles patterns (different effect - sparkles with high density variation)
FAST_SPARKLES_RED = canopy.Pattern('CTP-eyJrZXkiOiJmYXN0LXNwYXJrbGVzIiwidmVyc2lvbiI6MCwibmFtZSI6ImZhc3Qtc3BhcmtsZXMiLCJwYWxldHRlcyI6eyJQcmltYXJ5IjpbWzAsWzEsMSwxXV0sWzAuNDksWzEsMC4zMDk4MDM5MjE1Njg2Mjc0NiwwLjMwOTgwMzkyMTU2ODYyNzQ2XV0sWzEsWzEsMCwwXV1dfSwicGFyYW1zIjp7InNwZWVkIjowLjEsInNpemUiOiJzcGVlZCIsImRlbnNpdHkiOnsidHlwZSI6InNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC41OCwibWluIjowLCJtYXgiOjF9fX0sImxheWVycyI6W3siZWZmZWN0Ijoic3BhcmtsZXMiLCJvcGFjaXR5IjowLjUsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6IlByaW1hcnkiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC44LCJvZmZzZXQiOiJkZW5zaXR5In19XX0')
FAST_SPARKLES_YELLOW = canopy.Pattern('CTP-eyJrZXkiOiJmYXN0LXNwYXJrbGVzIiwidmVyc2lvbiI6MCwibmFtZSI6ImZhc3Qtc3BhcmtsZXMiLCJwYWxldHRlcyI6eyJQcmltYXJ5IjpbWzAsWzEsMSwxXV0sWzAuNDksWzEsMC44NjcsMF1dLFsxLFsxLDAuODY3LDBdXV19LCJwYXJhbXMiOnsic3BlZWQiOjAuMSwic2l6ZSI6InNwZWVkIiwiZGVuc2l0eSI6eyJ0eXBlIjoic2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjU4LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjAuNSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUHJpbWFyeSIsImlucHV0cyI6eyJkZW5zaXR5IjowLjgsIm9mZnNldCI6ImRlbnNpdHkifX1dfQ==')
FAST_SPARKLES_BLUE = canopy.Pattern('CTP-eyJrZXkiOiJmYXN0LXNwYXJrbGVzIiwidmVyc2lvbiI6MCwibmFtZSI6ImZhc3Qtc3BhcmtsZXMiLCJwYWxldHRlcyI6eyJQcmltYXJ5IjpbWzAsWzEsMSwxXV0sWzAuNDksWzAuMDIsMCwwLjYzOV1dLFsxLFswLjAyLDAsMC42MzldXV19LCJwYXJhbXMiOnsic3BlZWQiOjAuMSwic2l6ZSI6InNwZWVkIiwiZGVuc2l0eSI6eyJ0eXBlIjoic2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjU4LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjAuNSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUHJpbWFyeSIsImlucHV0cyI6eyJkZW5zaXR5IjowLjgsIm9mZnNldCI6ImRlbnNpdHkifX1dfQ==')
FAST_SPARKLES_PURPLE = canopy.Pattern('CTP-eyJrZXkiOiJmYXN0LXNwYXJrbGVzIiwidmVyc2lvbiI6MCwibmFtZSI6ImZhc3Qtc3BhcmtsZXMiLCJwYWxldHRlcyI6eyJQcmltYXJ5IjpbWzAsWzEsMSwxXV0sWzAuNDksWzAuNTY1LDAsMV1dLFsxLFswLjU2NSwwLDFdXV19LCJwYXJhbXMiOnsic3BlZWQiOjAuMSwic2l6ZSI6InNwZWVkIiwiZGVuc2l0eSI6eyJ0eXBlIjoic2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjU4LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjAuNSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUHJpbWFyeSIsImlucHV0cyI6eyJkZW5zaXR5IjowLjgsIm9mZnNldCI6ImRlbnNpdHkifX1dfQ==')

# Corrected patterns for D6/D7 strands (compensate for LED hardware color channel issue)
# D6/D7 strands have a color mapping issue where:
# - Yellow displays as Purple
# - Purple displays as Yellow
# - Blue displays as Green
# - Red displays correctly
# These corrected patterns swap the colors to compensate
FAST_SPARKLES_YELLOW_D6D7 = canopy.Pattern('CTP-eyJrZXkiOiJmYXN0LXNwYXJrbGVzIiwidmVyc2lvbiI6MCwibmFtZSI6ImZhc3Qtc3BhcmtsZXMiLCJwYWxldHRlcyI6eyJQcmltYXJ5IjpbWzAsWzEsMSwxXV0sWzAuNDksWzAuNTY1LDAsMV1dLFsxLFswLjU2NSwwLDFdXV19LCJwYXJhbXMiOnsic3BlZWQiOjAuMSwic2l6ZSI6InNwZWVkIiwiZGVuc2l0eSI6eyJ0eXBlIjoic2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjU4LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjAuNSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUHJpbWFyeSIsImlucHV0cyI6eyJkZW5zaXR5IjowLjgsIm9mZnNldCI6ImRlbnNpdHkifX1dfQ==')
FAST_SPARKLES_BLUE_D6D7 = canopy.Pattern('CTP-eyJrZXkiOiJmYXN0LXNwYXJrbGVzIiwidmVyc2lvbiI6MCwibmFtZSI6ImZhc3Qtc3BhcmtsZXMiLCJwYWxldHRlcyI6eyJQcmltYXJ5IjpbWzAsWzEsMSwxXV0sWzAuNDksWzAsMC42MzksMF1dLFsxLFswLDAuNjM5LDBdXV19LCJwYXJhbXMiOnsic3BlZWQiOjAuMSwic2l6ZSI6InNwZWVkIiwiZGVuc2l0eSI6eyJ0eXBlIjoic2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjU4LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjAuNSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUHJpbWFyeSIsImlucHV0cyI6eyJkZW5zaXR5IjowLjgsIm9mZnNldCI6ImRlbnNpdHkifX1dfQ==')
FAST_SPARKLES_PURPLE_D6D7 = canopy.Pattern('CTP-eyJrZXkiOiJmYXN0LXNwYXJrbGVzIiwidmVyc2lvbiI6MCwibmFtZSI6ImZhc3Qtc3BhcmtsZXMiLCJwYWxldHRlcyI6eyJQcmltYXJ5IjpbWzAsWzEsMSwxXV0sWzAuNDksWzEsMC44NjcsMF1dLFsxLFsxLDAuODY3LDBdXV19LCJwYXJhbXMiOnsic3BlZWQiOjAuMSwic2l6ZSI6InNwZWVkIiwiZGVuc2l0eSI6eyJ0eXBlIjoic2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjU4LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjAuNSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUHJpbWFyeSIsImlucHV0cyI6eyJkZW5zaXR5IjowLjgsIm9mZnNldCI6ImRlbnNpdHkifX1dfQ==')

# Rainbow sparkles pattern - cycles through red, yellow, green, and purple with white gaps
# Uses same sparkles effect and parameters as single-color patterns for consistency
FAST_SPARKLES_RAINBOW = canopy.Pattern('CTP-eyJrZXkiOiJmYXN0LXNwYXJrbGVzLXJhaW5ib3ciLCJ2ZXJzaW9uIjowLCJuYW1lIjoiZmFzdC1zcGFya2xlcy1yYWluYm93IiwicGFsZXR0ZXMiOnsiUHJpbWFyeSI6W1swLjAsWzEsMSwxXV0sWzAuMTIsWzEsMCwwXV0sWzAuMjUsWzEsMC44NjcsMF1dLFswLjM3LFswLDEsMF1dLFswLjUsWzAuNTY1LDAsMV1dLFswLjYyLFsxLDEsMV1dLFswLjc1LFsxLDAsMF1dLFswLjg3LFsxLDEsMV1dLFsxLjAsWzEsMSwxXV1dfSwicGFyYW1zIjp7InNwZWVkIjowLjEsInNpemUiOiJzcGVlZCIsImRlbnNpdHkiOnsidHlwZSI6InNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC41OCwibWluIjowLCJtYXgiOjF9fX0sImxheWVycyI6W3siZWZmZWN0Ijoic3BhcmtsZXMiLCJvcGFjaXR5IjowLjUsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6IlByaW1hcnkiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC44LCJvZmZzZXQiOiJkZW5zaXR5In19XX0=')
FAST_SPARKLES_RAINBOW_D6D7 = canopy.Pattern('CTP-eyJrZXkiOiJmYXN0LXNwYXJrbGVzLXJhaW5ib3ciLCJ2ZXJzaW9uIjowLCJuYW1lIjoiZmFzdC1zcGFya2xlcy1yYWluYm93IiwicGFsZXR0ZXMiOnsiUHJpbWFyeSI6W1swLjAsWzEsMSwxXV0sWzAuMTIsWzEsMCwwXV0sWzAuMjUsWzAuNTY1LDAsMV1dLFswLjM3LFswLDAuNjM5LDBdXSxbMC41LFsxLDAuODY3LDBdXSxbMC42MixbMSwxLDFdXSxbMC43NSxbMSwwLDBdXSxbMC44NyxbMSwxLDFdXSxbMS4wLFsxLDEsMV1dXX0sInBhcmFtcyI6eyJzcGVlZCI6MC4xLCJzaXplIjoic3BlZWQiLCJkZW5zaXR5Ijp7InR5cGUiOiJzYXciLCJpbnB1dHMiOnsidmFsdWUiOjAuNTgsIm1pbiI6MCwibWF4IjoxfX19LCJsYXllcnMiOlt7ImVmZmVjdCI6InNwYXJrbGVzIiwib3BhY2l0eSI6MC41LCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQcmltYXJ5IiwiaW5wdXRzIjp7ImRlbnNpdHkiOjAuOCwib2Zmc2V0IjoiZGVuc2l0eSJ9fV19')

# Slow pastel sparkles pattern for idle state (default)
# Soft pastel rainbow with gentle sparkle animation
SLOW_PASTEL_SPARKLES = canopy.Pattern('CTP-eyJrZXkiOiJwYXN0ZWwtc3BhcmtsZXMiLCJ2ZXJzaW9uIjowLCJuYW1lIjoicGFzdGVsLXNwYXJrbGVzIiwicGFsZXR0ZXMiOnsiUGFsZXR0ZTIiOltbMC4wMSxbMC45MTc2NDcwNTg4MjM1Mjk0LDAuNzI5NDExNzY0NzA1ODgyMywxXV0sWzAuMzIsWzAuNTMzMzMzMzMzMzMzMzMzMywwLjQ1MDk4MDM5MjE1Njg2Mjc1LDFdXSxbMC42OCxbMSwwLjg5ODAzOTIxNTY4NjI3NDUsMC40OTAxOTYwNzg0MzEzNzI1M11dLFsxLFsxLDAuNDExNzY0NzA1ODgyMzUyOSwwLjQxMTc2NDcwNTg4MjM1MjldXV19LCJwYXJhbXMiOnsic3BlZWQiOjAuMSwic2l6ZSI6InNwZWVkIiwiZGVuc2l0eSI6eyJ0eXBlIjoic2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjM2LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjAuOCwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUGFsZXR0ZTIiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC42NSwib2Zmc2V0IjoiZGVuc2l0eSJ9fV19')
SLOW_PASTEL_SPARKLES_D6D7 = canopy.Pattern('CTP-eyJrZXkiOiJwYXN0ZWwtc3BhcmtsZXMtZDZkNyIsInZlcnNpb24iOjAsIm5hbWUiOiJwYXN0ZWwtc3BhcmtsZXMtZDZkNyIsInBhbGV0dGVzIjp7IlBhbGV0dGUyIjpbWzAuMDEsWzAuNDExNzY0NzA1ODgyMzUyOSwwLjQxMTc2NDcwNTg4MjM1MjksMV1dLFswLjMyLFswLjcyMzEzNzI1NDkwMTk2MDgsMC43MzcyNTQ5MDE5NjA3ODQ0LDFdXSxbMC42OCxbMCwwLjg5ODAzOTIxNTY4NjI3NDUsMC41NjA3ODQzMTM3MjU0OTAyXV0sWzEsWzEsMC43MzAzOTIxNTY4NjI3NDUxLDAuNTYyNzQ1MDk4MDM5MjE1N11dXX0sInBhcmFtcyI6eyJzcGVlZCI6MC4xLCJzaXplIjoic3BlZWQiLCJkZW5zaXR5Ijp7InR5cGUiOiJzYXciLCJpbnB1dHMiOnsidmFsdWUiOjAuMzYsIm1pbiI6MCwibWF4IjoxfX19LCJsYXllcnMiOlt7ImVmZmVjdCI6InNwYXJrbGVzIiwib3BhY2l0eSI6MC44LCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQYWxldHRlMiIsImlucHV0cyI6eyJkZW5zaXR5IjowLjY1LCJvZmZzZXQiOiJkZW5zaXR5In19XX0=')


# Pattern pair class to keep ring and strand patterns always in sync
class PatternPair:
    """
    Holds a ring light pattern and its corresponding D6/D7 strand pattern.
    If no strand pattern is provided, uses the ring pattern as default.
    """
    def __init__(self, ring_pattern, strand_pattern=None):
        self.ring = ring_pattern
        self.strand = strand_pattern if strand_pattern is not None else ring_pattern


# Define pattern pairs to ensure ring and strand lights stay synchronized
PATTERN_PAIR_GAME_ON = PatternPair(PATTERN_GAME_ON, PATTERN_GAME_ON_D6D7)
PATTERN_PAIR_RED = PatternPair(FAST_SPARKLES_RED)  # Red has same pattern for ring and strands
PATTERN_PAIR_BLUE = PatternPair(FAST_SPARKLES_BLUE, FAST_SPARKLES_BLUE_D6D7)
PATTERN_PAIR_PURPLE = PatternPair(FAST_SPARKLES_PURPLE, FAST_SPARKLES_PURPLE_D6D7)
PATTERN_PAIR_YELLOW = PatternPair(FAST_SPARKLES_YELLOW, FAST_SPARKLES_YELLOW_D6D7)
PATTERN_PAIR_RAINBOW = PatternPair(FAST_SPARKLES_RAINBOW, FAST_SPARKLES_RAINBOW_D6D7)
PATTERN_PAIR_SLOW_PASTEL = PatternPair(SLOW_PASTEL_SPARKLES, SLOW_PASTEL_SPARKLES_D6D7)


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
    # Both hourglass tags trigger the same game configuration
    GAME_CONFIG = {
        'ring': PATTERN_GAME_ON,
        'duration': 300,  # 5 minutes (300 seconds)
        'music_duration': 300,  # 5 minutes (music duration)
    }

    TAG_PATTERNS = {
        '484e1466080104e0': GAME_CONFIG,  # Hourglass tag 1
        'bc591466080104e0': GAME_CONFIG,  # Hourglass tag 2
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
        self.current_pattern_ring = SLOW_PASTEL_SPARKLES  # Ring light pattern
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
        # Initialize 8 LED data pins - LED1_DATA for ring light, D6/D7 for color strands, D6 for game on
        # D1, D2, D3, D4, D5 are used for game buttons
        # Use max LED count for initialization
        max_leds = max(self.num_leds_ring, self.num_leds_strand)
        canopy.init([fern.LED1_DATA, fern.D6, fern.D7], max_leds)

        # Create segments for rendering
        self.ring_light_segment = canopy.Segment(0, 0, self.num_leds_ring)  # Ring light on LED1_DATA (16 LEDs)
        self.game_strand_d6_segment = canopy.Segment(1, 0, self.num_leds_strand)  # Game strand on D6 (200 LEDs)
        self.game_strand_d7_segment = canopy.Segment(2, 0, self.num_leds_strand)  # Game strand on D7 (200 LEDs)
        self.params = canopy.Params()
        print(f"LED segments created: Ring light on LED1_DATA ({self.num_leds_ring} LEDs), Game strands on D6/D7 ({self.num_leds_strand} LEDs each)")

        # Start the render loop
        asyncio.create_task(self._render_loop())
        print("Ready to scan RFID tags!")

    def set_pattern_pair(self, pattern_pair):
        """Set both ring and strand patterns from a pattern pair to keep them synchronized"""
        self.current_pattern_ring = pattern_pair.ring
        self.win_pattern = pattern_pair.strand

    async def _tag_found(self, uid):
        """Called when an RFID tag is detected"""
        print(f"Tag scanned: {uid}")

        tag_config = self.TAG_PATTERNS.get(uid)
        if tag_config:
            # Set both ring and strand patterns from the pattern pair
            self.set_pattern_pair(PATTERN_PAIR_GAME_ON)
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

        # Set the pattern pair based on which button was pressed
        button_to_pattern_pair = {
            'D1': PATTERN_PAIR_RED,      # Button 1 - Red
            'D2': PATTERN_PAIR_BLUE,     # Button 2 - Blue (with D6/D7 correction)
            'D3': PATTERN_PAIR_PURPLE,   # Button 3 - Purple (with D6/D7 correction)
            'D4': PATTERN_PAIR_YELLOW,   # Button 4 - Yellow (with D6/D7 correction)
            'D5': PATTERN_PAIR_RAINBOW,  # Button 5 - Rainbow (with D6/D7 correction)
        }

        pattern_pair = button_to_pattern_pair.get(button_name, PATTERN_PAIR_SLOW_PASTEL)

        # Set both ring and strand patterns from the pattern pair
        self.set_pattern_pair(pattern_pair)

        # Play the appropriate win sound
        if button_name == 'D1':
            self.game_audio.play_red_message()
        elif button_name == 'D2':
            self.game_audio.play_blue_message()
        elif button_name == 'D3':
            self.game_audio.play_purple_message()
        elif button_name == 'D4':
            self.game_audio.play_yellow_message()
        elif button_name == 'D5':
            # Run big win audio in background task to avoid blocking render loop
            asyncio.create_task(self.game_audio.play_big_win())

        # Set pattern duration based on button type
        if button_name == 'D5':
            # Big win: played 4 audio clips with total duration ~18.6s (3.93+3.32+5.15+6.20 + 0.2 gap after each)
            self.pattern_end_time = time.time() + 19
        else:
            # Color wins: play for 5 seconds
            self.pattern_end_time = time.time() + 5

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
                    self.set_pattern_pair(PATTERN_PAIR_SLOW_PASTEL)
                    print("Pattern complete - back to slow pastel sparkles")

                # Update LEDs
                canopy.clear()

                # Ring light shows current pattern (RFID triggered or ambient)
                if self.current_pattern_ring:
                    canopy.draw(self.ring_light_segment, self.current_pattern_ring, params=self.params)

                # D6 and D7 strands - show game win pattern or idle pattern
                if self.win_pattern:
                    # Game was won - display the win pattern on both D6 and D7
                    canopy.draw(self.game_strand_d6_segment, self.win_pattern, params=self.params)
                    canopy.draw(self.game_strand_d7_segment, self.win_pattern, params=self.params)
                else:
                    # Game is not active - display slow pastel sparkles pattern (default)
                    canopy.draw(self.game_strand_d6_segment, SLOW_PASTEL_SPARKLES_D6D7, params=self.params)
                    canopy.draw(self.game_strand_d7_segment, SLOW_PASTEL_SPARKLES_D6D7, params=self.params)

                canopy.render()

            except Exception as e:
                print(f"Render loop error: {e}")

            await asyncio.sleep(0.05)  # 20 FPS
