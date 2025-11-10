"""
Game Sensor Audio Controller

Plays the game music (5 minute file) when RFID tags are scanned.
"""
from audio import Audio
import asyncio

FADE_DURATION = 1.0  # Fade out over 1 second


class GameSensorAudio:
    def __init__(self, audio: Audio):
        self.audio = audio
        self.is_playing = False

        # Load the game music
        self.game_music = None
        try:
            self.game_music = self.audio.import_wav("game_music.wav")
            if self.game_music is None:
                print("Warning: game_music.wav not found")
        except Exception as e:
            print(f"Error loading game_music.wav: {e}")

    def play_correct(self):
        """Play the game music when an RFID tag is detected"""
        if self.game_music is not None:
            print("Playing game_music.wav")
            try:
                self.game_music.volume = 1.0  # Start at full volume
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
