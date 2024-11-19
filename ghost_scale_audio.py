from audio import Audio

AMBIENT_ONE_WAV = "ESP-ambience1.wav"
AMBIENT_TWO_WAV = "ESP-ambience2.wav"
READY_WAV = "Artifact-Pending.wav"


class GhostScaleAudio(object):
    audio = None

    def __init__(self, audio: Audio, name):
        self.audio = audio

        if name == "scaleOne":
            self.ambient_voice = self.audio.import_wav(AMBIENT_ONE_WAV)
        else:
            self.ambient_voice = self.audio.import_wav(AMBIENT_TWO_WAV)
        self.ambient_voice.loop = True
        self.ambient_voice.volume = 0.3

        self.ready_voice = self.audio.import_wav(READY_WAV)
        self.ready_voice.volume = 0.5

    def _stop(self):
        # self.ambient_voice.stop()
        self.ready_voice.stop()

    def play_ambient(self):
        self._stop()
        self.ambient_voice.stop()
        self.audio.mixer.play(self.ambient_voice)

    def play_ready(self):
        # self._stop()
        self.ready_voice.stop()
        self.audio.mixer.play(self.ready_voice)
