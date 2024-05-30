import os
from machine import Pin, SPI, I2C, I2S
import asyncio
import fern
import codec
import time
import mixer
import random

TEST_WAV = "yoshiisland16khz.wav"
AMBIENT_WAV = "ambient-forest.wav"

AMBIENT_FILES = ["ambient-forest.wav", "ambient-forest.wav", "ambient-forest.wav"]

CORRECT_WAV = "ambient-forest.wav"
INCORRECT_WAV = "ambient-forest.wav"
PENDING_WAV = "ambient-forest.wav"


class Audio(object):
    current_file = None
    ambient_wav = None
    mixer = None
    ambient_voices = []
    ambient_voice = None
    correct_voice = None
    incorrect_voice = None
    pending_voice = None

    def __init__(self):
        print("Initing codec")
        i2c = I2C(0, scl=fern.I2C_SCL, sda=fern.I2C_SDA, freq=100000)
        codec.init(i2c)
        time.sleep_ms(1000)

        print("Mount SD card")
        mounted = False
        try:
            fern.mount_sdcard()
            # sd = fern.sdcard()
            # os.mount(sd, "/sd")
            mounted = True
        except:
            print("No SD card found")

        if mounted:
            f = open("/sd/{}".format(AMBIENT_WAV), "rb")
            self.mixer = mixer.Mixer()

            for f in AMBIENT_FILES:
                voice = self._import_wav(f)
                self.ambient_voices.append(voice)
                voice.loop = True
                voice.volume = 1.0
            self.correct_voice = self._import_wav(CORRECT_WAV)

            self.incorrect_voice = self._import_wav(INCORRECT_WAV)
            self.pending_voice = self._import_wav(PENDING_WAV)

    def _import_wav(self, path):
        try:
            f = open("/sd/{}".format(path), "rb")
            return mixer.Voice(f)

        except:
            print("Can't open WAV file: ", path)

    def start(self):
        asyncio.create_task(self.continuous_play())

    def play_ambient(self):
        if self.ambient_voice:
            self.ambient_voice.stop()
        self.ambient_voice = random.choice(self.ambient_voices)
        self.mixer.play(self.ambient_voice)

    def play_correct(self):
        self.incorrect_voice.stop()
        self.pending_voice.stop()
        self.mixer.play(self.correct_voice)

    def play_incorrect(self):
        self.correct_voice.stop()
        self.pending_voice.stop()
        self.mixer.play(self.incorrect_voice)

    def play_pending(self):
        self.correct_voice.stop()
        self.incorrect_voice.stop()
        self.mixer.play(self.pending_voice)

    def play_disconnect(self):
        self.correct_voice.stop()

    # def play_sound(self, path):
    #     print("Playing sound", path)
    #     try:
    #         self.current_wav = open("/sd/{}".format(path), "rb")
    #     except:
    #         print("Can't open WAV file: ", path)

    # def play_correct(self):

    #     self.play_sound(CORRECT_WAV)

    async def continuous_play(self):
        asyncio.sleep(5)
        print("==========  START PLAYBACK ==========")
        audio_out = I2S(
            0,
            sck=Pin(fern.I2S_BCK),
            ws=Pin(fern.I2S_WS),
            sd=Pin(fern.I2S_SDOUT),
            mck=Pin(fern.I2S_MCK),
            mode=I2S.TX,
            bits=16,
            format=I2S.STEREO,
            rate=16000,
            ibuf=4000,
        )

        swriter = asyncio.StreamWriter(audio_out)
        wav_samples = bytearray(5000)
        wav_samples_mv = memoryview(wav_samples)

        while True:
            self.mixer.mixinto(wav_samples_mv)
            swriter.out_buf = wav_samples_mv[:]
            await swriter.drain()
