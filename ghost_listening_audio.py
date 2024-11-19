from audio import Audio

AMBIENT_WAV = "ESP-ambience2.wav"


class GhostListeningAudio(object):
    audio = None

    def __init__(self, audio: Audio):
        self.audio = audio

        self.ambient_voice = self.audio.import_wav(AMBIENT_WAV)
        self.ambient_voice.loop = True
        self.ambient_voice.volume = 0.3

    def _stop(self):
        self.ambient_voice.stop()

    def play_ambient(self):
        self._stop()
        self.audio.mixer.play(self.ambient_voice)
