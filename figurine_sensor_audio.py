"""
Figurine Sensor Audio Controller

Handles audio playback for the figurine sensor RFID tag detection.
"""
from audio import Audio
import asyncio

WATER_WAV = "water.wav"
FADE_DURATION = 1.0  # Fade out over 1 second


class FigurineSensorAudio:
    def __init__(self, audio: Audio):
        self.audio = audio
        self.water_voice = self.audio.import_wav(WATER_WAV)
        self.is_fading = False

    def play_correct(self):
        """Play the water sound when an RFID tag is detected"""
        if self.water_voice is not None:
            self.is_fading = False
            self.water_voice.stop()
            self.water_voice.volume = 1.0  # Start at full volume
            self.audio.mixer.play(self.water_voice)
        else:
            print("Warning: water.wav not found")

    async def fade_out(self):
        """Gradually fade out the water sound"""
        if self.water_voice is not None and not self.is_fading:
            self.is_fading = True
            steps = 20  # Number of volume steps
            step_duration = FADE_DURATION / steps

            for i in range(steps, 0, -1):
                volume = i / steps
                self.water_voice.volume = volume
                await asyncio.sleep(step_duration)

            self.water_voice.stop()
            self.is_fading = False

    def stop_sound(self):
        """Stop the water sound immediately"""
        if self.water_voice is not None:
            self.water_voice.stop()
