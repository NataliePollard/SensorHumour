from audio import Audio

AMBIENT_WAV = "ESP-ambience3.wav"
SCANNING_WAV = "GhostPrinter-scanning.wav"
READY_WAV = "GhostPrinter-ready_to_print.wav"
PRINTING_WAV = "GhostPrinter-printing.wav"


class PrinterAudio(object):
    audio = None

    def __init__(self, audio: Audio):
        self.audio = audio

        self.ambient_voice = self.audio.import_wav(AMBIENT_WAV)
        self.ambient_voice.loop = True
        self.ambient_voice.volume = 0.3

        self.scanning_voice = self.audio.import_wav(SCANNING_WAV)
        self.scanning_voice.volume = 0.7
        self.ready_voice = self.audio.import_wav(READY_WAV)
        self.ready_voice.loop = True
        self.ready_voice.volume = 0.7
        self.printing_voice = self.audio.import_wav(PRINTING_WAV)
        self.printing_voice.volume = 0.7

    def _stop(self):
        # self.ambient_voice.stop()
        # self.scanning_voice.stop()
        self.printing_voice.stop()
        self.ready_voice.stop()
        self.ambient_voice.volume = 0.1

    def play_ambient(self):
        self._stop()
        self.audio.mixer.play(self.ambient_voice)
        print("Playing ambient")

    def restart_ambient(self):
        self.ambient_voice.volume = 0.3
    
    def play_scanning(self):
        self._stop()
        self.audio.mixer.play(self.scanning_voice)
        print("Playing scanning")

    def play_ready(self):
        self._stop()
        self.audio.mixer.play(self.ready_voice)
        print("Playing ready")

    def play_printing(self):
        self._stop()
        self.audio.mixer.play(self.printing_voice)
        print("Playing printing")
