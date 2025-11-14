"""
Game Sensor Audio Controller

Plays the game music (5 minute file) when RFID tags are scanned.
Plays win celebration sounds based on which button was pressed.
"""
from audio import Audio
import asyncio

FADE_DURATION = 1.0  # Fade out over 1 second


class GameSensorAudio:
    def __init__(self, audio: Audio):
        self.audio = audio
        self.is_playing = False
        self.currently_playing = None  # Track which sound is currently playing

        # Load the game music
        self.game_music = None
        try:
            self.game_music = self.audio.import_wav("game_music.wav")
            if self.game_music is None:
                print("Warning: game_music.wav not found")
        except Exception as e:
            print(f"Error loading game_music.wav: {e}")

        # Load the win celebration sounds
        self.red_message = None
        try:
            self.red_message = self.audio.import_wav("sang_win_32000.wav")
            if self.red_message is None:
                print("Warning: sang_win_32000.wav not found")
        except Exception as e:
            print(f"Error loading sang_win_32000.wav: {e}")

        self.blue_message = None
        try:
            self.blue_message = self.audio.import_wav("flem_win_32000.wav")
            if self.blue_message is None:
                print("Warning: flem_win_32000.wav not found")
        except Exception as e:
            print(f"Error loading flem_win_32000.wav: {e}")

        self.purple_message = None
        try:
            self.purple_message = self.audio.import_wav("mel_win_32000.wav")
            if self.purple_message is None:
                print("Warning: mel_win_32000.wav not found")
        except Exception as e:
            print(f"Error loading mel_win_32000.wav: {e}")

        self.yellow_message = None
        try:
            self.yellow_message = self.audio.import_wav("cole_win_32000.wav")
            if self.yellow_message is None:
                print("Warning: cole_win_32000.wav not found")
        except Exception as e:
            print(f"Error loading cole_win_32000.wav: {e}")

        self.big_win_sang = None
        try:
            self.big_win_sang = self.audio.import_wav("sang_big_win.wav")
            if self.big_win_sang is None:
                print("Warning: sang_big_win.wav not found")
        except Exception as e:
            print(f"Error loading sang_big_win.wav: {e}")

        self.big_win_mel = None
        try:
            self.big_win_mel = self.audio.import_wav("mel_big_win.wav")
            if self.big_win_mel is None:
                print("Warning: mel_big_win.wav not found")
        except Exception as e:
            print(f"Error loading mel_big_win.wav: {e}")

        self.big_win_flem = None
        try:
            self.big_win_flem = self.audio.import_wav("flem_big_win.wav")
            if self.big_win_flem is None:
                print("Warning: flem_big_win.wav not found")
            else:
                print(f"Successfully loaded flem_big_win.wav: {self.big_win_flem}")
        except Exception as e:
            print(f"Error loading flem_big_win.wav: {e}")

        self.big_win_cole = None
        try:
            self.big_win_cole = self.audio.import_wav("cole_big_win.wav")
            if self.big_win_cole is None:
                print("Warning: cole_big_win.wav not found")
        except Exception as e:
            print(f"Error loading cole_big_win.wav: {e}")

    def play_correct(self):
        """Play the game music when an RFID tag is detected"""
        if self.game_music is not None:
            print("Playing game_music.wav")
            try:
                self.game_music.volume = 0.5  # Set to 50% volume
                self.audio.mixer.play(self.game_music)
                self.is_playing = True
            except Exception as e:
                print(f"Error playing game_music.wav: {e}")
        else:
            print("Warning: game_music.wav not loaded")

    async def fade_out(self):
        """Stop the game music"""
        if self.game_music is not None and self.is_playing:
            print("Stopping game music")
            try:
                self.game_music.stop()
                self.is_playing = False
            except Exception as e:
                print(f"Error stopping audio: {e}")

    def stop_sound(self):
        """Stop the game music immediately"""
        if self.game_music is not None:
            try:
                self.game_music.stop()
                self.is_playing = False
            except Exception as e:
                print(f"Error stopping audio: {e}")

    def play_win_sound(self, sound_attr, filename, button_name):
        """Play a win sound with the given audio attribute

        Args:
            sound_attr: The audio attribute to play (self.red_message, self.blue_message, etc.)
            filename: The filename for logging
            button_name: The button/win type name for tracking
        """
        if sound_attr is not None:
            print(f"Playing {filename}")
            try:
                sound_attr.volume = 0.5  # Set to 50% volume
                self.audio.mixer.play(sound_attr)
                self.currently_playing = button_name
            except Exception as e:
                print(f"Error playing {filename}: {e}")
        else:
            print(f"Warning: {filename} not loaded")

    def play_red_message(self):
        """Play the red message sound"""
        self.play_win_sound(self.red_message, "sang_win_32000.wav", "red_message")

    def play_blue_message(self):
        """Play the blue message sound"""
        self.play_win_sound(self.blue_message, "flem_win_32000.wav", "blue_message")

    def play_purple_message(self):
        """Play the purple message sound"""
        self.play_win_sound(self.purple_message, "mel_win_32000.wav", "purple_message")

    def play_yellow_message(self):
        """Play the yellow message sound"""
        self.play_win_sound(self.yellow_message, "cole_win_32000.wav", "yellow_message")

    async def play_big_win(self):
        """Play the big win sounds in sequence, one after another"""
        print("Playing big win sequence")
        big_win_clips = [
            (self.big_win_sang, "sang_big_win.wav", 3.93),
            (self.big_win_mel, "mel_big_win.wav", 3.32),
            (self.big_win_flem, "flem_big_win.wav", 5.15),
            (self.big_win_cole, "cole_big_win.wav", 6.20)
        ]

        for clip, filename, duration in big_win_clips:
            if clip is not None:
                print(f"Playing {filename}")
                try:
                    clip.volume = 0.5
                    self.audio.mixer.play(clip)
                    self.currently_playing = "big_win"
                    # Wait for the clip to finish playing using actual audio duration
                    await asyncio.sleep(duration + 0.2)
                except Exception as e:
                    print(f"Error playing {filename}: {e}")
            else:
                print(f"Warning: {filename} not loaded")
