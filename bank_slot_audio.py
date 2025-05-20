from audio import Audio

AMBIENT_WAV = "Dollhouse-ambiance.wav"
PAYMENT_WAV = "Dollhouse-wrong.wav"
PLAYING_WAV = "Dollhouse-playing.wav"
WIN_WAV = "Dollhouse-win.wav"
LOSE_WAVE = "Dollhouse-lose.wav"



class BankSlotMachineAudio(object):

    def __init__(self, audio: Audio):
        self.audio = audio

        self.ambient_voice = self.audio.import_wav(AMBIENT_WAV)
        self.ambient_voice.loop = True
        self.ambient_voice.volume = 0.5

        self.payment_voice = self.audio.import_wav(PAYMENT_WAV)
        self.playing_voice = self.audio.import_wav(PLAYING_WAV)
        self.win_voice = self.audio.import_wav(WIN_WAV)
        self.lose_voice = self.audio.import_wav(LOSE_WAVE)

    def play_ambient(self):
        self.ambient_voice.stop()
        self.audio.mixer.play(self.ambient_voice)

    def play_payment(self):
        self.win_voice.stop()
        self.lose_voice.stop()
        self.playing_voice.stop()
        self.audio.mixer.play(self.payment_voice)

    def play_playing(self):
        self.payment_voice.stop()
        self.win_voice.stop()
        self.lose_voice.stop()
        self.audio.mixer.play(self.playing_voice)

    def play_win(self):
        self.payment_voice.stop()
        self.playing_voice.stop()
        self.lose_voice.stop()
        self.audio.mixer.play(self.win_voice)
    
    def play_lose(self):
        self.payment_voice.stop()
        self.playing_voice.stop()
        self.win_voice.stop()
        self.audio.mixer.play(self.lose_voice)
