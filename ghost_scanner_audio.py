from audio import Audio

AMBIENT_ONE_WAV = "ESP-ambience1.wav"
AMBIENT_TWO_WAV = "ESP-ambience2.wav"
AMBIENT_THREE_WAV = "ESP-ambience3.wav"
CORRECT_WAV = "Artifact-Connected.wav"


class GhostScannerAudio(object):
    audio = None

    def __init__(self, audio: Audio, name):
        self.audio = audio
        if self.audio.mixer:
            if name == "scanner1":
                self.ambient_voice = self.audio.import_wav(AMBIENT_ONE_WAV)
            elif name == "scanner2":
                self.ambient_voice = self.audio.import_wav(AMBIENT_TWO_WAV)
            elif name == "scanner3":
                self.ambient_voice = self.audio.import_wav(AMBIENT_THREE_WAV)
            self.ambient_voice.loop = True
            self.ambient_voice.volume = 0.2

            self.correct_voice = self.audio.import_wav(CORRECT_WAV)
            self.correct_voice.volume = 0.7

    def _stop(self):
        if self.audio.mixer:
            self.ambient_voice.stop()

    def play_ambient(self):
        if self.audio.mixer:
            self._stop()
            self.audio.mixer.play(self.ambient_voice)

    def play_correct(self):
        if self.audio.mixer:
            self.correct_voice.stop()
            self.audio.mixer.play(self.correct_voice)
