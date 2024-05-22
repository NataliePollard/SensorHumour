import os
from machine import Pin, SPI, I2C, I2S
import asyncio
import fern
import codec
import time


AMBIENT_WAV = "ambient-forest.wav"
CORRECT_WAV = "powerup.wav"
INCORRECT_WAV = "incorrect.wav"


class Audio(object):
    current_file = None
    ambient_wav = None

    def __init__(self):
        print("Initing codec")
        i2c = I2C(0, scl=fern.I2C_SCL, sda=fern.I2C_SDA)
        codec.init(i2c)
        time.sleep_ms(1000)

        print("Mount SD card")
        mounted = False
        try:
            sd = fern.sdcard()
            os.mount(sd, "/sd")
            mounted = True
        except:
            print("No SD card found")

        if mounted:
            print("Initing I2S audio out")
            self.audio_out = I2S(
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

    def start(self):
        WAV_FILE = "ambient-forest.wav"
        # WAV_FILE = "powerup.wav"
        # WAV_FILE = "yoshiisland16khz.wav"
        try:
            wav = open("/sd/{}".format(WAV_FILE), "rb")
            # self.ambient_wav = wav
            asyncio.create_task(self.continuous_play(wav))
        except:
            print("Can't open WAV file: ", WAV_FILE)

    # def play_sound(self, path):
    #     print("Playing sound", path)
    #     try:
    #         self.current_wav = open("/sd/{}".format(path), "rb")
    #     except:
    #         print("Can't open WAV file: ", path)

    # def play_correct(self):

    #     self.play_sound(CORRECT_WAV)

    async def continuous_play(self, wav):
        asyncio.sleep(5)

        swriter = asyncio.StreamWriter(self.audio_out)

        _ = wav.seek(44)  # advance to first byte of Data section in WAV file

        # allocate sample array
        # memoryview used to reduce heap allocation
        wav_samples = bytearray(10000)
        wav_samples_mv = memoryview(wav_samples)

        # continuously read audio samples from the WAV file
        # and write them to an I2S DAC
        print("==========  START PLAYBACK ==========")

        # self.current_wav = self.ambient_wav

        while True:
            num_read = wav.readinto(wav_samples_mv)
            # end of WAV file?
            if num_read == 0:
                # if self.current_wav != self.ambient_wav:
                #     self.current_wav = self.ambient_wav
                #     print("Resetting to ambient")
                # end-of-file, advance to first byte of Data section
                _ = wav.seek(44)
            else:
                # apply temporary workaround to eliminate heap allocation in uasyncio Stream class.
                # workaround can be removed after acceptance of PR:
                #    https://github.com/micropython/micropython/pull/7868
                # swriter.write(wav_samples_mv[:num_read])
                swriter.out_buf = wav_samples_mv[:num_read]
                await swriter.drain()
