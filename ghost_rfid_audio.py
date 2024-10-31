from audio import Audio

TEST_WAV = "yoshiisland16khz.wav"
AMBIENT_WAV = "ambient-forest.wav"

AMBIENT_FILES_BY_NAME = {
    "dollhouse": "Artifact-Ambient-1.wav",
}

CORRECT_WAV = "Artifact-Connected.wav"
INCORRECT_WAV = "Artifact-Incorrect.wav"
READY_TO_WRITE_WAV = "Artifact-Pending.wav"
DISCONNECT_WAV = "Artifact-Disconnect.wav"

WRITING_WAV = "Artifact-Pending.wav"


class RFIDAudio(object):
    audio = None

    current_file = None
    correct_voice = None
    incorrect_voice = None
    ready_to_write_voice = None

    def init(self, audio: Audio):
        self.audio = audio

        self.correct_voice = self.audio.import_wav(CORRECT_WAV)
        self.incorrect_voice = self.audio.import_wav(INCORRECT_WAV)
        self.incorrect_voice.loop = True
        self.ready_to_write_voice = self.audio.import_wav(READY_TO_WRITE_WAV)
        self.ready_to_write_voice.loop = True
        self.disconnect_voice = self.audio.import_wav(DISCONNECT_WAV)
        self.writing_voice = self.audio.import_wav(WRITING_WAV)

    def play_correct(self):
        self.incorrect_voice.stop()
        self.ready_to_write_voice.stop()
        self.disconnect_voice.stop()
        self.audio.mixer.play(self.correct_voice)

    def play_incorrect(self):
        self.correct_voice.stop()
        self.ready_to_write_voice.stop()
        self.disconnect_voice.stop()
        self.audio.mixer.play(self.incorrect_voice)

    def play_ready_to_write(self):
        self.correct_voice.stop()
        self.ready_to_write_voice.stop()
        self.disconnect_voice.stop()
        self.incorrect_voice.stop()
        self.audio.mixer.play(self.ready_to_write_voice)

    def play_writing(self):
        self.correct_voice.stop()
        self.ready_to_write_voice.stop()
        self.disconnect_voice.stop()
        self.incorrect_voice.stop()
        self.audio.mixer.play(self.writing_voice)

    def play_disconnect(self):
        self.correct_voice.stop()
        self.writing_voice.stop()
        self.incorrect_voice.stop()
        self.ready_to_write_voice.stop()
        self.audio.mixer.play(self.disconnect_voice)
