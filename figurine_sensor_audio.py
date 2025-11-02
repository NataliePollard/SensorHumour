"""
Figurine Sensor Audio Controller

Handles audio playback for the figurine sensor RFID tag detection.
Cycles through multiple water sound variations for variety.
"""
from audio import Audio
import asyncio

WATER_SOUNDS = ["water_1.wav", "water_2.wav", "water_3.wav", "water_4.wav"]
FADE_DURATION = 1.0  # Fade out over 1 second


class FigurineSensorAudio:
    def __init__(self, audio: Audio):
        self.audio = audio

        # Load all water sound variations
        self.water_voices = []
        for sound_file in WATER_SOUNDS:
            voice = self.audio.import_wav(sound_file)
            if voice is not None:
                self.water_voices.append(voice)
            else:
                print(f"Warning: {sound_file} not found")

        self.current_sound_index = 0
        self.is_fading = False

    def play_correct(self):
        """Play the next water sound when an RFID tag is detected"""
        if len(self.water_voices) > 0:
            self.is_fading = False

            # Get the current sound to play
            current_voice = self.water_voices[self.current_sound_index]

            # Stop all sounds first
            for voice in self.water_voices:
                voice.stop()

            # Play the current sound
            current_voice.volume = 1.0  # Start at full volume
            self.audio.mixer.play(current_voice)

            # Cycle to next sound for next time
            self.current_sound_index = (self.current_sound_index + 1) % len(self.water_voices)
        else:
            print("Warning: No water sound files loaded")

    async def fade_out(self):
        """Gradually fade out the water sound"""
        if len(self.water_voices) > 0 and not self.is_fading:
            self.is_fading = True
            steps = 20  # Number of volume steps
            step_duration = FADE_DURATION / steps

            for i in range(steps, 0, -1):
                volume = i / steps
                # Fade out all voices
                for voice in self.water_voices:
                    voice.volume = volume
                await asyncio.sleep(step_duration)

            # Stop all voices
            for voice in self.water_voices:
                voice.stop()
            self.is_fading = False

    def stop_sound(self):
        """Stop all water sounds immediately"""
        for voice in self.water_voices:
            voice.stop()
