import os
from machine import Pin, SPI, I2C, I2S
import asyncio
import fern
import nfc
import seesaw
import canopy
import codec
from fps import FPS

# PatternRainbow = "CTP-eyJpZCI6IjAzNWVlN2NjLWZiM2MtNDI0Ni1hOTM1LTdjNGQ3ZDYyMzEyMyIsInZlcnNpb24iOjEsIm5hbWUiOiJOZXcgUGF0dGVybiIsInBhbGV0dGVzIjp7IlBhbGV0dGUxIjpbWzAsWzEsMCwwXV0sWzAuMTksWzAuOTY0NzA1ODgyMzUyOTQxMiwxLDBdXSxbMC4zNixbMC4wNjI3NDUwOTgwMzkyMTU2OSwxLDAuMDUwOTgwMzkyMTU2ODYyNzQ0XV0sWzAuNTEsWzAsMSwwLjg3MDU4ODIzNTI5NDExNzddXSxbMC42NyxbMCwwLjA5MDE5NjA3ODQzMTM3MjU1LDFdXSxbMC44MixbMC40OCwwLjAxLDAuNDJdXSxbMC45OSxbMSwwLDBdXV19LCJwYXJhbXMiOnt9LCJsYXllcnMiOlt7ImVmZmVjdCI6ImdyYWRpZW50Iiwib3BhY2l0eSI6MSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUGFsZXR0ZTEiLCJpbnB1dHMiOnsib2Zmc2V0Ijp7InR5cGUiOiJyc2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjQxLCJtaW4iOjAsIm1heCI6MX19LCJzaXplIjowLjUsInJvdGF0aW9uIjowfX1dfQ"
PatternRainbow = "CTP-eyJpZCI6IjAzNWVlN2NjLWZiM2MtNDI0Ni1hOTM1LTdjNGQ3ZDYyMzEyMyIsInZlcnNpb24iOjEsIm5hbWUiOiJOZXcgUGF0dGVybiIsInBhbGV0dGVzIjp7IlBhbGV0dGUxIjpbWzAsWzEsMCwwXV0sWzAuMTksWzAuOTY0NzA1ODgyMzUyOTQxMiwxLDBdXSxbMC4zNixbMC4wNjI3NDUwOTgwMzkyMTU2OSwxLDAuMDUwOTgwMzkyMTU2ODYyNzQ0XV0sWzAuNTEsWzAsMSwwLjg3MDU4ODIzNTI5NDExNzddXSxbMC42NyxbMCwwLjA5MDE5NjA3ODQzMTM3MjU1LDFdXSxbMC44MixbMC40OCwwLjAxLDAuNDJdXSxbMC45OSxbMSwwLDBdXV19LCJwYXJhbXMiOnsicHJvZ3Jlc3MiOjB9LCJsYXllcnMiOlt7ImVmZmVjdCI6ImdyYWRpZW50Iiwib3BhY2l0eSI6InByb2dyZXNzIiwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUGFsZXR0ZTEiLCJpbnB1dHMiOnsib2Zmc2V0Ijp7InR5cGUiOiJyc2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjQxLCJtaW4iOjAsIm1heCI6MX19LCJzaXplIjowLjUsInJvdGF0aW9uIjowfX1dfQ"


async def tag_found(reader):
    try:
        print("Tag found ", reader.tag)
        while True:
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        print("Tag lost")


async def encoder_loop(ss):
    last = await ss.encoder_position()
    print("Encoder: ", last)
    while True:
        value = await ss.encoder_position()
        if value != last:
            print("Encoder: ", value)
            last = value
        await asyncio.sleep(0.1)


async def render_loop():
    segment = (0, 0, 50)
    pattern = canopy.Pattern(PatternRainbow)
    pattern.params["progress"] = 0.7
    last = 0
    f = FPS(verbose=True)
    while True:
        # value = encoder.encoder_position()
        # if value != last:
        #     pattern.params["progress"] += (last - value) / 50.0
        #     last = value
        #     if pattern.params["progress"] > 1:
        #         pattern.params["progress"] = 1
        #     if pattern.params["progress"] < 0:
        #         pattern.params["progress"] = 0
        f.tick()
        canopy.draw(segment, pattern)
        canopy.render()
        await asyncio.sleep(0)


async def continuous_play(audio_out, wav):
    swriter = asyncio.StreamWriter(audio_out)

    _ = wav.seek(44)  # advance to first byte of Data section in WAV file

    # allocate sample array
    # memoryview used to reduce heap allocation
    wav_samples = bytearray(10000)
    wav_samples_mv = memoryview(wav_samples)

    # continuously read audio samples from the WAV file
    # and write them to an I2S DAC
    print("==========  START PLAYBACK ==========")

    while True:
        num_read = wav.readinto(wav_samples_mv)
        # end of WAV file?
        if num_read == 0:
            # end-of-file, advance to first byte of Data section
            _ = wav.seek(44)
        else:
            # apply temporary workaround to eliminate heap allocation in uasyncio Stream class.
            # workaround can be removed after acceptance of PR:
            #    https://github.com/micropython/micropython/pull/7868
            # swriter.write(wav_samples_mv[:num_read])
            swriter.out_buf = wav_samples_mv[:num_read]
            await swriter.drain()

async def main():
    print("Opening NFC reader")
    spi = SPI(
        1, baudrate=7000000, sck=fern.NFC_SCK, mosi=fern.NFC_MOSI, miso=fern.NFC_MISO
    )
    reader = nfc.NfcReader(spi, fern.NFC_NSS, fern.NFC_BUSY, fern.NFC_RST)
    reader.onTagFound(tag_found)
    try:
        await reader.start(verbose=True)
        asyncio.create_task(reader.loop())
    except Exception as e:
        print("No NFC reader found: ", e)
        raise

    print("Initing codec")
    i2c = I2C(0, scl=fern.I2C_SCL, sda=fern.I2C_SDA)
    codec.init(i2c)

    print("Initing encoder")
    encoder = seesaw.Seesaw(i2c, 0x36)
    try:
        await encoder.start()
        asyncio.create_task(encoder_loop(encoder))
    except:
        print("No encoder found")

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
        WAV_FILE = "test.wav"
        wav = open("/sd/{}".format(WAV_FILE), "rb")
        asyncio.create_task(continuous_play(audio_out, wav))

    print("Starting canopy")
    canopy.init([fern.LED1_DATA, fern.LED2_DATA], 100)
    asyncio.create_task(render_loop())

    asyncio.get_event_loop().run_forever()


asyncio.run(main())


# already_added = False
# try:
#     ndefmsg = self.readNdef()
#     print("Ndef message:")
#     for r in ndefmsg.records:
#         if r.id == b"CT":
#             already_added = True
#         print(r.payload)
# except:
#     ndefmsg = ndef.new_message(
#         (ndef.TNF_WELL_KNOWN, ndef.RTD_TEXT, "", b"\x02enboooom")
#     )

# if not already_added:
#     print("Adding record")
#     r = ndef.NdefRecord()
#     r.tnf = ndef.TNF_WELL_KNOWN
#     r.set_type(ndef.RTD_TEXT)
#     r.set_id(b"CT")
#     r.set_payload(b"\x02enPlease work")

#     ndefmsg.records.append(r)
#     ndefmsg.fix()
#     self.writeNdef(ndefmsg)
#     print("Added")
