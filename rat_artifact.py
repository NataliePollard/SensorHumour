import asyncio
import json
import canopy
import fern

from fps import FPS
from nfc import NfcWrapper
from rat_mqtt import Mqtt
from rat_wifi import Wifi
from rat_magnet import Magnet
from rat_relay import Relay
from rat_audio import Audio


PatternInitializing = "CTP-eyJpZCI6ImRkMWVjY2MwLTE3ODYtNDhhYS05ZWE3LWNmMzAwODIwMTFhNCIsInZlcnNpb24iOjMsIm5hbWUiOiJXSWZpIERpc2Nvbm5lY3RlZCIsInBhbGV0dGVzIjp7IlBhbGV0dGUxIjpbWzAsWzEsMCwwXV0sWzAuOTksWzAsMCwwXV1dfSwicGFyYW1zIjp7IkNvbG9yIjoxfSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJjaGFzZXIiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQYWxldHRlMSIsImlucHV0cyI6eyJvZmZzZXQiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC40OCwibWluIjowLCJtYXgiOjF9fSwic2l6ZSI6MC4zMX19XX0"
# PatternRainbow = "CTP-eyJpZCI6IjAzNWVlN2NjLWZiM2MtNDI0Ni1hOTM1LTdjNGQ3ZDYyMzEyMyIsInZlcnNpb24iOjEsIm5hbWUiOiJOZXcgUGF0dGVybiIsInBhbGV0dGVzIjp7IlBhbGV0dGUxIjpbWzAsWzEsMCwwXV0sWzAuMTksWzAuOTY0NzA1ODgyMzUyOTQxMiwxLDBdXSxbMC4zNixbMC4wNjI3NDUwOTgwMzkyMTU2OSwxLDAuMDUwOTgwMzkyMTU2ODYyNzQ0XV0sWzAuNTEsWzAsMSwwLjg3MDU4ODIzNTI5NDExNzddXSxbMC42NyxbMCwwLjA5MDE5NjA3ODQzMTM3MjU1LDFdXSxbMC44MixbMC40OCwwLjAxLDAuNDJdXSxbMC45OSxbMSwwLDBdXV19LCJwYXJhbXMiOnsicHJvZ3Jlc3MiOjB9LCJsYXllcnMiOlt7ImVmZmVjdCI6ImdyYWRpZW50Iiwib3BhY2l0eSI6InByb2dyZXNzIiwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUGFsZXR0ZTEiLCJpbnB1dHMiOnsib2Zmc2V0Ijp7InR5cGUiOiJyc2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjQxLCJtaW4iOjAsIm1heCI6MX19LCJzaXplIjowLjUsInJvdGF0aW9uIjowfX1dfQ"
ArtifactWaitingPattern = "CTP-eyJpZCI6IjY1YmNiOTNmLTE5MTktNGFiNi1iZWQ4LWVmOGQyZmRjN2Q1OSIsInZlcnNpb24iOjUsIm5hbWUiOiJBcnRpZmFjdCAtIFJlYWR5IiwicGFsZXR0ZXMiOnsiQ29sb3JzIjpbWzAsWzEsMCwwXV0sWzAuMTUsWzEsMC43MTc2NDcwNTg4MjM1Mjk0LDBdXSxbMC4yOSxbMC45MDE5NjA3ODQzMTM3MjU1LDEsMF1dLFswLjQ0LFswLjI4MjM1Mjk0MTE3NjQ3MDYsMSwwXV0sWzAuNTksWzAsMC44NjY2NjY2NjY2NjY2NjY3LDFdXSxbMC43MyxbMC4wNjY2NjY2NjY2NjY2NjY2NywwLDFdXSxbMC44NixbMC41MTc2NDcwNTg4MjM1Mjk1LDAsMV1dLFswLjk4LFsxLDAsMC43NDkwMTk2MDc4NDMxMzczXV1dLCJPdmVybGF5IjpbWzAsWzAsMCwwXV0sWzEsWzEsMSwxXV1dfSwicGFyYW1zIjp7IkNvbG9yIjowLjc0fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzb2xpZCIsIm9wYWNpdHkiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC41NywibWluIjowLjA3LCJtYXgiOjAuODJ9fSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiQ29sb3JzIiwiaW5wdXRzIjp7Im9mZnNldCI6IkNvbG9yIn19LHsiZWZmZWN0Ijoic3BhcmtsZXMiLCJvcGFjaXR5IjowLjQ3LCJibGVuZCI6Im92ZXJsYXkiLCJwYWxldHRlIjoiT3ZlcmxheSIsImlucHV0cyI6eyJkZW5zaXR5Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMzMsIm1pbiI6MC4xNSwibWF4IjowLjY5fX0sIm9mZnNldCI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjMyLCJtaW4iOjAsIm1heCI6MX19fX0seyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC41NSwibWluIjowLCJtYXgiOjAuNjd9fSwiYmxlbmQiOiJub3JtYWwtbm9uYmxhY2siLCJwYWxldHRlIjoiT3ZlcmxheSIsImlucHV0cyI6eyJkZW5zaXR5IjowLjE5LCJvZmZzZXQiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC4yNCwibWluIjowLCJtYXgiOjF9fX19XX0"
# ArtifactConnectedPatternOld = "CTP-eyJpZCI6ImQyM2NlN2I4LTRhNjktNDYzMS05ODk1LTU2YzQ2ZTIzNWEyZiIsInZlcnNpb24iOjMsIm5hbWUiOiJBcnRpZmFjdCAtIENvbm5lY3RlZCIsInBhbGV0dGVzIjp7IlBhbGV0dGUxIjpbWzAuMixbMCwwLDBdXSxbMC4yOSxbMC40LDEsMF1dLFswLjM4LFswLDAsMF1dLFswLjYxLFswLDAsMF1dLFswLjcyLFswLjkzMzMzMzMzMzMzMzMzMzMsMSwwXV0sWzAuODMsWzAsMCwwXV1dLCJQYWxldHRlMiI6W1swLjEzLFswLDAsMF1dLFswLjI0LFswLDEsMC44NV1dLFswLjMyLFswLDAsMF1dLFswLjY3LFswLDAsMF1dLFswLjc3LFswLDEsMC44M11dLFswLjg3LFswLDAsMF1dXX0sInBhcmFtcyI6e30sImxheWVycyI6W3siZWZmZWN0IjoiZ3JhZGllbnQiLCJvcGFjaXR5IjowLjIsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6IlBhbGV0dGUxIiwiaW5wdXRzIjp7Im9mZnNldCI6eyJ0eXBlIjoic2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjUsIm1pbiI6MCwibWF4IjoxfX0sInNpemUiOjAuNjMsInJvdGF0aW9uIjowLjI1fX0seyJlZmZlY3QiOiJwbGFzbWEiLCJvcGFjaXR5IjowLjA2LCJibGVuZCI6InNjcmVlbiIsInBhbGV0dGUiOiJQYWxldHRlMiIsImlucHV0cyI6eyJkZW5zaXR5Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMTUsIm1pbiI6MCwibWF4IjoxfX0sIm9mZnNldCI6MX19XX0"
ArtifactConnectedPattern = "CTP-eyJpZCI6IjFhMjQ5MmUwLTY2ZGMtNGJmMi04ODY1LTYxNTIwMzNlZTk2ZSIsInZlcnNpb24iOjgsIm5hbWUiOiJBcnRpZmFjdCAtIENvbm5lY3RlZCBDb2xvcnMiLCJwYWxldHRlcyI6eyJDb2xvcnMiOltbMCxbMSwwLDBdXSxbMC4xNSxbMSwwLjcyLDBdXSxbMC4yNyxbMC45LDEsMF1dLFswLjQ0LFswLjI4LDEsMF1dLFswLjU5LFswLDAuODcsMV1dLFswLjczLFswLjA3LDAsMV1dLFswLjg2LFswLjUyLDAsMV1dLFsxLFsxLDAsMC43NV1dXSwiQnJpZ2h0bmVzcyI6W1swLjE0LFswLDAsMF1dLFswLjI1LFsxLDEsMV1dLFswLjM5LFswLDAsMF1dLFswLjU1LFswLDAsMF1dLFswLjY1LFsxLDEsMV1dLFswLjc1LFswLDAsMF1dXX0sInBhcmFtcyI6eyJDb2xvciI6MC42NH0sImxheWVycyI6W3siZWZmZWN0Ijoic29saWQiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJDb2xvcnMiLCJpbnB1dHMiOnsib2Zmc2V0IjoiQ29sb3IifX0seyJlZmZlY3QiOiJjaGFzZXIiLCJvcGFjaXR5IjowLjYsImJsZW5kIjoibXVsdGlwbHkiLCJwYWxldHRlIjoiQnJpZ2h0bmVzcyIsImlucHV0cyI6eyJvZmZzZXQiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAuMTMsIm1heCI6MX19LCJzaXplIjowLjQ1fX0seyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjAuNywiYmxlbmQiOiJvdmVybGF5IiwicGFsZXR0ZSI6IkJyaWdodG5lc3MiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC42MSwib2Zmc2V0Ijp7InR5cGUiOiJ0cmlhbmdsZSIsImlucHV0cyI6eyJ2YWx1ZSI6MC4yOCwibWluIjowLCJtYXgiOjF9fX19XX0"
ArtifactIncorrectPattern = "CTP-eyJpZCI6IjdkYjZiOGM3LTJkZjYtNDAzNC1iZjA1LTk3MTAxZDI3N2FhZiIsInZlcnNpb24iOjUsIm5hbWUiOiJBcnRpZmFjdCBJbmNvcnJlY3QiLCJwYWxldHRlcyI6eyJQYWxldHRlMSI6W1swLjY4LFswLDAsMF1dLFswLjk4LFsxLDAsMF1dXSwiUGFsZXR0ZTIiOltbMCxbMCwwLDBdXSxbMC4xOCxbMSwwLjQ0NzA1ODgyMzUyOTQxMTgsMF1dLFswLjMxLFswLDAsMF1dLFswLjYzLFswLDAsMF1dLFswLjc3LFsxLDAuOCwwXV0sWzAuOTcsWzAsMCwwXV1dfSwicGFyYW1zIjp7IkNvbG9yIjoxfSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzb2xpZCIsIm9wYWNpdHkiOjEsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6IlBhbGV0dGUxIiwiaW5wdXRzIjp7Im9mZnNldCI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjYzLCJtaW4iOjAsIm1heCI6MC44MX19fX0seyJlZmZlY3QiOiJwbGFzbWEiLCJvcGFjaXR5IjowLjg3LCJibGVuZCI6Im92ZXJsYXkiLCJwYWxldHRlIjoiUGFsZXR0ZTEiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MSwib2Zmc2V0Ijp7InR5cGUiOiJ0cmlhbmdsZSIsImlucHV0cyI6eyJ2YWx1ZSI6MC4wMiwibWluIjowLCJtYXgiOjF9fX19LHsiZWZmZWN0IjoiY2hhc2VyIiwib3BhY2l0eSI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjc0LCJtaW4iOjAsIm1heCI6MX19LCJibGVuZCI6Im5vcm1hbC1ub25ibGFjayIsInBhbGV0dGUiOiJQYWxldHRlMiIsImlucHV0cyI6eyJvZmZzZXQiOjEsInNpemUiOjAuNTF9fV19"


MODE_INITIALIZING = 0
MODE_OFF = 1
MODE_WAITING = 2
MODE_CONNECTED = 3
MODE_INVALID = 4

EVENT_FINISHED_BOOT = "finishedBoot"
EVENT_CARD_FOUND = "cardFound"
EVENT_CARD_REMOVED = "cardRemoved"
EVENT_ARTIFACT_UPDATE = "artifactUpdate"

TEST_TAG = "5bc31366080104e0"

initializing_pattern = canopy.Pattern(PatternInitializing)
connected_pattern = canopy.Pattern(ArtifactConnectedPattern)
off_pattern = canopy.Pattern(ArtifactWaitingPattern)
waiting_pattern = canopy.Pattern(ArtifactWaitingPattern)
incorrect_pattern = canopy.Pattern(ArtifactIncorrectPattern)


class Artifact(object):
    color = 0
    current_tag = None
    desired_tag = TEST_TAG
    current_mode = MODE_INITIALIZING
    is_connected = False
    is_invalid_connection = False
    is_wifi_connected = False
    light_pattern = initializing_pattern

    def __init__(self, name, magnet_pin=1, relay_pin=2):
        self.name = name
        self.magnet_pin = magnet_pin
        self.relay_pin = relay_pin
        self.mqtt = Mqtt(name, self._onMqttMessage)
        self.wifi = Wifi()
        self.nfc = NfcWrapper(self._tag_found, self._tag_lost)
        self.magnet = Magnet(pin=self.magnet_pin)
        self.relay = Relay(pin=self.relay_pin)
        self.audio = Audio()

    async def start(self):
        self.wifi.start(self._on_wifi_connected)
        await self.nfc.start()
        self.magnet.start()
        self.audio.start()

        print("Starting canopy")
        canopy.init([fern.LED1_DATA, fern.LED2_DATA], 100)
        asyncio.create_task(self._render_loop())

    def _onMqttMessage(self, topic, msg):
        print((topic, msg))
        try:
            data = json.loads(msg)
            if (
                data.get("event") == EVENT_ARTIFACT_UPDATE
                and data.get("id") == self.name
            ):
                self.desired_tag = data.get("pendingRfid")
                self.color = data.get("color")
                if self.current_tag and self.current_tag != self.desired_tag:
                    self.is_invalid_connection = True
                print("Updating Color: ", self.color)
                self._update_state(EVENT_ARTIFACT_UPDATE)
        except:
            print("Failed to parse mqtt message")

    def _on_wifi_connected(self):
        self.is_wifi_connected = True

        def on_mqtt_connected():
            self._update_state(EVENT_FINISHED_BOOT)

        try:
            asyncio.create_task(self.mqtt.run(on_mqtt_connected))
        except:
            print("Failed to start Mqtt")

    def _tag_found(self, uid):
        self.current_tag = uid
        self.is_connected = True
        self.is_invalid_connection = uid != self.desired_tag
        self._update_state(EVENT_CARD_FOUND)

    def _tag_lost(self):
        self.is_connected = False
        self.is_invalid_connection = False
        self.current_tag = None
        self._update_state(EVENT_CARD_REMOVED)

    def _update_mode(self):
        print("is wifi connected: ", self.is_wifi_connected)
        print("is connected: ", self.is_connected)
        print("is invalid: ", self.is_invalid_connection)
        print("desired tag: ", self.desired_tag)
        print("current tag: ", self.current_tag)
        if self.is_invalid_connection:
            self.current_mode = MODE_INVALID
        elif self.is_connected:
            self.current_mode = MODE_CONNECTED
            # self.audio.play_correct()
        elif self.desired_tag is not None and self.current_tag is None:
            self.current_mode = MODE_WAITING
        elif self.desired_tag is None:
            self.current_mode = MODE_OFF
        print("updated mode: ", self.current_mode)

    def _after_update_state(self):
        # abstract method to be overridden
        pass

    def _update_state(self, event):
        self._update_mode()
        self._update_light_pattern()
        if self.current_mode == MODE_INVALID:
            self.magnet.connect(is_invalid=True)
            self.relay.off()
        elif self.current_mode == MODE_CONNECTED:
            self.relay.on()
            self.magnet.connect(is_invalid=False)
        else:
            self.relay.off()
            self.magnet.disconnect()
        self._after_update_state()
        if event and event != EVENT_ARTIFACT_UPDATE and self.mqtt.is_connected:
            self.mqtt.send_message(
                json.dumps(
                    {
                        "event": event,
                        "reader": self.name,
                        "card": self.current_tag,
                        "connected": self.is_connected,
                        "invalid": self.is_invalid_connection,
                    }
                )
            )

    def _update_light_pattern(self):
        if self.current_mode == MODE_INITIALIZING:
            self.light_pattern = initializing_pattern
        elif self.current_mode == MODE_INVALID:
            self.light_pattern = incorrect_pattern
        elif self.current_mode == MODE_CONNECTED:
            self.light_pattern = connected_pattern
        elif self.current_mode == MODE_WAITING:
            self.light_pattern = waiting_pattern
        elif self.current_mode == MODE_OFF:
            self.light_pattern = off_pattern

    async def _update(self):
        # abstract method to be overridden
        pass

    async def _render_loop(self):
        segment = canopy.Segment(0, 0, 16)
        f = FPS(verbose=True)
        while True:
            f.tick()
            self._update()
            self.light_pattern.params["Color"] = self.color
            canopy.draw(segment, self.light_pattern, float(0.8))
            canopy.render()
            await asyncio.sleep(0)
