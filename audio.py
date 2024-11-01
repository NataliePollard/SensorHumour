from machine import Pin, I2C, I2S
import asyncio
import fern
import codec
import time
import mixer


class Audio(object):
    mixer = None

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
            self.mixer = mixer.Mixer()

    def import_wav(self, path):
        try:
            f = open("/sd/{}".format(path), "rb")
            return mixer.Voice(f)
        except:
            print("Can't open WAV file: ", path)

    def start(self):
        asyncio.create_task(self.continuous_play())

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
