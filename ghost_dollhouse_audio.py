from audio import Audio

FIREPLACE_WAV = "Dollhouse-button5.wav"
BEDROOM_WAV = "Dollhouse-button4.wav"
ATTIC_WAV = "Dollhouse-button3.wav"
STUDY_WAV = "Dollhouse-button2.wav"
CONSERVATORY_WAV = "Dollhouse-button1.wav"

AMBIENT_WAV = "Dollhouse-ambiance.wav"
# AMBIENT_WAV = "ESP-ambience2.wav"
TURN_OFF_WAV = "Dollhouse-wrong.wav"

WIN_GAME_WAV = "Dollhouse-win.wav"

CORRECT_WAV = "Artifact-Connected.wav"


class DollhouseAudio(object):

    def __init__(self, audio: Audio):
        self.audio = audio

        self.ambient_voice = self.audio.import_wav(AMBIENT_WAV)
        self.ambient_voice.loop = True
        self.ambient_voice.volume = 0.5

        self.fireplace_voice = self.audio.import_wav(FIREPLACE_WAV)
        self.bedroom_voice = self.audio.import_wav(BEDROOM_WAV)
        self.attic_voice = self.audio.import_wav(ATTIC_WAV)
        self.study_voice = self.audio.import_wav(STUDY_WAV)
        self.conservatory_voice = self.audio.import_wav(CONSERVATORY_WAV)

        self.turn_off_voice = self.audio.import_wav(TURN_OFF_WAV)
        self.turn_off_voice.volume = 0.3
        self.win_game_voice = self.audio.import_wav(WIN_GAME_WAV)
        self.win_game_voice.volume = 0.7

        self.correct_voice = self.audio.import_wav(CORRECT_WAV)

    def play_ambient(self):
        self.ambient_voice.stop()
        self.win_game_voice.stop()
        self.audio.mixer.play(self.ambient_voice)

    def _turn_off_rooms(self):
        self.fireplace_voice.stop()
        self.bedroom_voice.stop()
        self.attic_voice.stop()
        self.study_voice.stop()
        self.conservatory_voice.stop()

    def play_win_game(self):
        self._turn_off_rooms()
        self.turn_off_voice.stop()
        # self.ambient_voice.stop()
        self.audio.mixer.play(self.win_game_voice)

    def play_fireplace(self):
        self._turn_off_rooms()
        self.audio.mixer.play(self.fireplace_voice)

    def play_bedroom(self):
        self._turn_off_rooms()
        self.audio.mixer.play(self.bedroom_voice)

    def play_attic(self):
        self._turn_off_rooms()
        self.audio.mixer.play(self.attic_voice)

    def play_study(self):
        self._turn_off_rooms()
        self.audio.mixer.play(self.study_voice)

    def play_conservatory(self):
        self._turn_off_rooms()
        self.audio.mixer.play(self.conservatory_voice)

    def play_turn_off(self):
        self.turn_off_voice.stop()
        self.audio.mixer.play(self.turn_off_voice)

    def play_correct(self):
        self.audio.mixer.play(self.correct_voice)
