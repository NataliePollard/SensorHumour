from audio import Audio

AMBIENT_WAV = "Artifact-Ambient-1.wav"
READY_WAV = "Artifact-Ambient-2.wav"


class GhostScaleAudio(object):
    audio = None

    def __init__(self, audio: Audio):
        self.audio = audio

        self.ambient_voice = self.audio.import_wav(AMBIENT_WAV)
        self.ambient_voice.loop = True
        self.ambient_voice.volume = 0.3

        self.ready_voice = self.audio.import_wav(READY_WAV)

    def _stop(self):
        self.ambient_voice.stop()
        self.ready_voice.stop()

    def play_ambient(self):
        self._stop()
        self.audio.mixer.play(self.ambient_voice)

    def play_ready(self):
        self._stop()
        self.audio.mixer.play(self.ready_voice)
