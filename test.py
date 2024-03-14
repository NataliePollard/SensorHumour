import time
from machine import Pin, SPI, I2C
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
    last = 0
    while True:
        value = ss.encoder_position()
        if value != last:
            print("Encoder: ", value)
            last = value
        await asyncio.sleep(0.1)


async def render_loop(encoder):
    segment = (0, 0, 50)
    pattern = canopy.Pattern(PatternRainbow)
    pattern.params["progress"] = 0.7
    last = 0
    f = FPS()
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


async def main():
    print("Opening NFC reader")
    spi = SPI(
        1, baudrate=7000000, sck=fern.NFC_SCK, mosi=fern.NFC_MOSI, miso=fern.NFC_MISO
    )
    reader = nfc.NfcReader(spi, fern.NFC_NSS, fern.NFC_BUSY, fern.NFC_RST)
    reader.onTagFound(tag_found)
    await reader.start()
    asyncio.create_task(reader.loop())

    print("Opening I2C / Seesaw sensors")
    i2c = I2C(0, scl=fern.I2C_SCL, sda=fern.I2C_SDA)
    try:
        encoder = seesaw.Seesaw(i2c, 0x36)
        await encoder.start()
        asyncio.create_task(encoder_loop(encoder))
    except:
        print("No encoder found")

    print("Initing audio codec")
    codec.init(i2c)

    print("Starting canopy")
    canopy.init([fern.LED1_DATA, fern.LED2_DATA], 50)
    asyncio.create_task(render_loop(encoder))

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
