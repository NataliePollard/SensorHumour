from audio import Audio

AMBIENT_WAV = "Dollhouse-ambiance.wav"
OPEN_WAV = "Artifact-Connected.wav"
QUIET_OPEN_WAV = "Artifact-Connected.wav"
FOUNDER_WAV = "Dollhouse-win.wav"
 
MOTIVATION_WAVS = [
    "Dollhouse-button1.wav",
    "Dollhouse-button2.wav",
    "Dollhouse-button3.wav",
]


class VaultDoorAudio(object):

    def __init__(self, audio: Audio):
        self.audio = audio

        self.ambient_voice = self.audio.import_wav(AMBIENT_WAV)
        self.ambient_voice.loop = True
        self.ambient_voice.volume = 0.5

        self.open_voice = self.audio.import_wav(OPEN_WAV)
        self.quiet_open_voice = self.audio.import_wav(QUIET_OPEN_WAV)
        self.founder_voice = self.audio.import_wav(FOUNDER_WAV)

        self.motivation_num = 0

        self.motivation_voices = [
            self.audio.import_wav(MOTIVATION_WAVS[0]),
            self.audio.import_wav(MOTIVATION_WAVS[0]),
            self.audio.import_wav(MOTIVATION_WAVS[0]),
        ]

    def stop_motivation(self):
        for voice in self.motivation_voices:
            voice.stop()

    def play_motivation(self):
        self.stop_motivation()
        self.audio.mixer.play(self.motivation_voices[self.motivation_num])
        self.motivation_num = (self.motivation_num + 1) % len(MOTIVATION_WAVS)

    def play_ambient(self):
        self.ambient_voice.stop()
        self.founder_voice.stop()
        self.open_voice.stop()
        # self.audio.mixer.play(self.ambient_voice)

    def play_open(self):
        self.open_voice.stop()
        self.quiet_open_voice.stop()
        self.audio.mixer.play(self.open_voice)

    def play_quiet_open(self):
        self.open_voice.stop()
        self.quiet_open_voice.stop()
        self.audio.mixer.play(self.quiet_open_voice)

    def play_founder(self):
        self.open_voice.stop()
        self.audio.mixer.play(self.founder_voice)
