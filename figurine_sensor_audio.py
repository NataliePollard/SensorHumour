"""
Figurine Sensor Audio Controller

Handles audio playback for the figurine sensor RFID tag detection.
"""
from audio import Audio

WATER_WAV = "water.wav"


class FigurineSensorAudio:
    def __init__(self, audio: Audio):
        self.audio = audio
        self.water_voice = self.audio.import_wav(WATER_WAV)

    def play_correct(self):
        """Play the water sound when an RFID tag is detected"""
        if self.water_voice is not None:
            self.water_voice.stop()
            self.audio.mixer.play(self.water_voice)
        else:
            print("Warning: water.wav not found")

    def stop_sound(self):
        """Stop the water sound"""
        if self.water_voice is not None:
            self.water_voice.stop()
