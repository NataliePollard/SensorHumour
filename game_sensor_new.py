"""
Game Sensor RFID LED Controller - Simplified Version

Hourglass Game Experience:
- Scan hourglass tag to start 5-minute game
- Press button 1-4 to win and display color (red, blue, purple, yellow)
- Press button 5 to turn off lights
- When game is won, music stops and the matching color pattern displays

Hardware:
- Ring light: 16 LEDs on LED1_DATA
- Game strands: 172 LEDs on D6, 200 LEDs on D7
- Buttons: D1, D2, D3, D4, D5

Supported RFID tags:
- Hourglass tag 1 (484e1466080104e0) - Start game
- Hourglass tag 2 (bc591466080104e0) - Start game
"""
import asyncio
import fern
import time
from nfc import NfcWrapper
from audio import Audio
from game_sensor_audio import GameSensorAudio
from machine import Pin
from led_control import LEDStrip, PulsePattern, RainbowPattern, SparklePattern


# Define colors as RGB tuples (easier than base64!)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 100, 255)
COLOR_PURPLE = (200, 0, 255)
COLOR_YELLOW = (255, 200, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_OFF = (0, 0, 0)

# Chill sparkles - soft rainbow colors
COLOR_CHILL_BASE = (100, 100, 150)  # Soft white-blue


class GameSensor:
    """
    Hourglass Game System with simplified LED control
    """

    TAG_PATTERNS = {
        '484e1466080104e0': {  # Hourglass tag 1 - Game On pattern
            'duration': 300,  # 5 minutes
            'music_duration': 300,  # 5 minutes
        },
        'bc591466080104e0': {  # Hourglass tag 2 - Game On pattern
            'duration': 300,  # 5 minutes
            'music_duration': 300,  # 5 minutes
        },
    }

    def __init__(self):
        # LED setup
        self.ring_light = LEDStrip(fern.LED1_DATA, 16)
        self.strand_d6 = LEDStrip(fern.D6, 172)
        self.strand_d7 = LEDStrip(fern.D7, 200)

        # Audio setup
        self.audio = Audio()
        self.game_audio = GameSensorAudio(self.audio)

        # NFC setup
        self.nfc = NfcWrapper(self._tag_found, self._tag_lost)

        # Button setup - 5 game buttons
        self.button_pins = {
            'D1': Pin(fern.D1, Pin.IN, Pin.PULL_UP),   # Button 1 - Red
            'D2': Pin(fern.D2, Pin.IN, Pin.PULL_UP),   # Button 2 - Blue
            'D3': Pin(fern.D3, Pin.IN, Pin.PULL_UP),   # Button 3 - Purple
            'D4': Pin(fern.D4, Pin.IN, Pin.PULL_UP),   # Button 4 - Yellow
            'D5': Pin(fern.D5, Pin.IN, Pin.PULL_UP),   # Button 5 - Off
        }
        self.button_was_pressed = {pin: False for pin in self.button_pins}

        # Game state
        self.is_game_active = False
        self.sound_end_time = 0
        self.pattern_end_time = 0
        self.current_pattern = None

        # Default pattern
        self._set_default_pattern()

    def _set_default_pattern(self):
        """Set the default idle pattern (chill sparkles)"""
        self.ring_light.set_color(COLOR_CHILL_BASE)
        self.ring_light.write()

        self.strand_d6.set_color(COLOR_CHILL_BASE)
        self.strand_d6.write()

        self.strand_d7.set_color(COLOR_CHILL_BASE)
        self.strand_d7.write()

    async def start(self):
        """Initialize and start the system"""
        await self.nfc.start()
        self.audio.start()

        print("Starting LED strips")
        self._set_default_pattern()

        # Start the render loop
        asyncio.create_task(self._render_loop())
        print("Ready to scan RFID tags!")

    async def _tag_found(self, uid):
        """Called when an RFID tag is detected"""
        print(f"Tag scanned: {uid}")

        tag_config = self.TAG_PATTERNS.get(uid)
        if tag_config:
            duration = tag_config['duration']
            self.pattern_end_time = time.time() + duration

            # This is a hourglass tag - start the game
            self.sound_end_time = time.time() + tag_config['music_duration']
            self.is_game_active = True

            # Display game pattern on all LEDs
            self._display_game_pattern()

            # Play the game music
            self.game_audio.play_correct()
            print("Game is now ACTIVE! Press buttons to win!")
        else:
            print("Unknown tag - ignoring")

    def _tag_lost(self):
        """Called when tag is removed"""
        print("Tag removed")

    def _display_game_pattern(self):
        """Display the game on pattern (pulsing white)"""
        self.ring_light.set_color(COLOR_WHITE)
        self.ring_light.write()

        self.strand_d6.set_color(COLOR_WHITE)
        self.strand_d6.write()

        self.strand_d7.set_color(COLOR_WHITE)
        self.strand_d7.write()

    async def _handle_game_win(self, button_name):
        """Handle game win condition"""
        print(f"GAME WON via {button_name}!")
        self.is_game_active = False

        # Stop the music immediately
        asyncio.create_task(self.game_audio.fade_out())
        self.sound_end_time = 0

        # Display win pattern based on button pressed
        button_to_color = {
            'D1': COLOR_RED,        # Button 1 - Red
            'D2': COLOR_BLUE,       # Button 2 - Blue
            'D3': COLOR_PURPLE,     # Button 3 - Purple
            'D4': COLOR_YELLOW,     # Button 4 - Yellow
            'D5': COLOR_OFF,        # Button 5 - Off (turn off lights)
        }

        win_color = button_to_color.get(button_name, COLOR_CHILL_BASE)

        # Display the win color for 5 seconds
        self.ring_light.set_color(win_color)
        self.ring_light.write()

        self.strand_d6.set_color(win_color)
        self.strand_d6.write()

        self.strand_d7.set_color(win_color)
        self.strand_d7.write()

        # Set timeout to return to default after 5 seconds
        self.pattern_end_time = time.time() + 5
        print(f"Displaying {button_name} pattern for 5 seconds")

    async def _render_loop(self):
        """Main rendering loop - handles button presses and pattern timing"""
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

                # Check if sound period is over
                if self.sound_end_time > 0 and current_time > self.sound_end_time:
                    self.sound_end_time = 0
                    asyncio.create_task(self.game_audio.fade_out())
                    print("Sound fading out")

                # Check if pattern period is over (return to default)
                if self.pattern_end_time > 0 and current_time > self.pattern_end_time:
                    self.pattern_end_time = 0
                    self._set_default_pattern()
                    print("Pattern complete - back to chill sparkles")

                # Sleep briefly to prevent blocking
                await asyncio.sleep(0.05)

            except Exception as e:
                print(f"Error in render loop: {e}")
                await asyncio.sleep(0.1)


# Main entry point
async def main():
    sensor = GameSensor()
    await sensor.start()
    # Keep running
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
