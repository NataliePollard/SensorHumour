from audio import Audio

AMBIENT_WAV = "Artifact-Ambient-1.wav"
READY_WAV = "Artifact-Ambient-2.wav"
PLAYING_WAV = "Artifact-Ambient-3.wav"


class GhostListeningAudio(object):
    audio = None

    def __init__(self, audio: Audio):
        self.audio = audio

        self.ambient_voice = self.audio.import_wav(AMBIENT_WAV)
        self.ambient_voice.loop = True
        self.ambient_voice.volume = 0.3

        self.ready_voice = self.audio.import_wav(READY_WAV)
        self.playing_voice = self.audio.import_wav(PLAYING_WAV)

    def _stop(self):
        self.ambient_voice.stop()
        self.playing_voice.stop()
        self.ready_voice.stop()

    def play_ambient(self):
        self._stop()
        self.audio.mixer.play(self.ambient_voice)

    def play_ready(self):
        self._stop()
        self.audio.mixer.play(self.ready_voice)

    def play_playing(self):
        self._stop()
        self.audio.mixer.play(self.playing_voice)
