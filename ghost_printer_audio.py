from audio import Audio

AMBIENT_WAV = "Artifact-Ambient-1.wav"
READY_WAV = "Artifact-Ambient-2.wav"
PRINTING_WAV = "Artifact-Ambient-3.wav"


class PrinterAudio(object):
    audio = None

    def __init__(self, audio: Audio):
        self.audio = audio

        self.ambient_voice = self.audio.import_wav(AMBIENT_WAV)
        self.ambient_voice.loop = True
        self.ambient_voice.volume = 0.3

        self.ready_voice = self.audio.import_wav(READY_WAV)
        self.printing_voice = self.audio.import_wav(PRINTING_WAV)

    def _stop(self):
        self.ambient_voice.stop()
        self.printing_voice.stop()
        self.ready_voice.stop()

    def play_ambient(self):
        self._stop()
        self.audio.mixer.play(self.ambient_voice)

    def play_ready(self):
        self._stop()
        self.audio.mixer.play(self.ready_voice)

    def play_printing(self):
        self._stop()
        self.audio.mixer.play(self.printing_voice)
