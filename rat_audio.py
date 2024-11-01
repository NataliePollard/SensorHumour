from audio import Audio

TEST_WAV = "yoshiisland16khz.wav"
AMBIENT_WAV = "ambient-forest.wav"

AMBIENT_FILES_BY_NAME = {
    "artifact/city": "Artifact-Ambient-1.wav",
    "artifact/tank": "Artifact-Ambient-2.wav",
    "artifact/microwave": "Artifact-Ambient-3.wav",
    "artifact/bugs": "Artifact-Ambient-4.wav",
    "artifact/fish": "Artifact-Ambient-5.wav",
    "artifact/mushrooms": "Artifact-Ambient-6.wav",
    "artifact/volcano": "Artifact-Ambient-7.wav",
    "artifact/mobile": "Artifact-Ambient-8.wav",
    "dollhouse": "Artifact-Ambient-1.wav",
}

MICROWAVE_WAV = "Artifact-Microwave.wav"

CORRECT_WAV = "Artifact-Connected.wav"
INCORRECT_WAV = "Artifact-Incorrect.wav"
PENDING_WAV = "Artifact-Pending.wav"
DISCONNECT_WAV = "Artifact-Disconnect.wav"


class RatAudio(Audio):
    current_file = None
    ambient_wav = None
    ambient_voice = None
    correct_voice = None
    incorrect_voice = None
    pending_voice = None

    def _on_init(self, artifact_name):
        super()._on_init()
        self.ambient_voice = self.import_wav(
            AMBIENT_FILES_BY_NAME.get(artifact_name)
        )
        self.ambient_voice.loop = True
        self.ambient_voice.volume = 0.3
        self.correct_voice = self.import_wav(CORRECT_WAV)
        self.incorrect_voice = self.import_wav(INCORRECT_WAV)
        self.incorrect_voice.loop = True
        self.pending_voice = self.import_wav(PENDING_WAV)
        self.pending_voice.loop = True
        self.disconnect_voice = self.import_wav(DISCONNECT_WAV)

    def play_ambient(self):
        self.ambient_voice.stop()
        self.mixer.play(self.ambient_voice)

    def play_correct(self):
        self.incorrect_voice.stop()
        self.pending_voice.stop()
        self.disconnect_voice.stop()
        self.mixer.play(self.correct_voice)

    def play_incorrect(self):
        self.correct_voice.stop()
        self.pending_voice.stop()
        self.disconnect_voice.stop()
        self.mixer.play(self.incorrect_voice)

    def play_pending(self):
        self.incorrect_voice.stop()
        self.mixer.play(self.pending_voice)

    def play_disconnect(self):
        self.correct_voice.stop()
        self.incorrect_voice.stop()
        self.mixer.play(self.disconnect_voice)

