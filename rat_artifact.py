import asyncio
import json
import canopy
import fern
import time

from fps import FPS
from nfc import NfcWrapper
from rat_mqtt import Mqtt
from rat_wifi import Wifi
from rat_magnet import Magnet
from rat_relay import Relay

from rat_audio import Audio


PatternInitializing = "CTP-eyJpZCI6ImRkMWVjY2MwLTE3ODYtNDhhYS05ZWE3LWNmMzAwODIwMTFhNCIsInZlcnNpb24iOjMsIm5hbWUiOiJXSWZpIERpc2Nvbm5lY3RlZCIsInBhbGV0dGVzIjp7IlBhbGV0dGUxIjpbWzAsWzEsMCwwXV0sWzAuOTksWzAsMCwwXV1dfSwicGFyYW1zIjp7IkNvbG9yIjoxfSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJjaGFzZXIiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQYWxldHRlMSIsImlucHV0cyI6eyJvZmZzZXQiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC40OCwibWluIjowLCJtYXgiOjF9fSwic2l6ZSI6MC4zMX19XX0"
# PatternRainbow = "CTP-eyJpZCI6IjAzNWVlN2NjLWZiM2MtNDI0Ni1hOTM1LTdjNGQ3ZDYyMzEyMyIsInZlcnNpb24iOjEsIm5hbWUiOiJOZXcgUGF0dGVybiIsInBhbGV0dGVzIjp7IlBhbGV0dGUxIjpbWzAsWzEsMCwwXV0sWzAuMTksWzAuOTY0NzA1ODgyMzUyOTQxMiwxLDBdXSxbMC4zNixbMC4wNjI3NDUwOTgwMzkyMTU2OSwxLDAuMDUwOTgwMzkyMTU2ODYyNzQ0XV0sWzAuNTEsWzAsMSwwLjg3MDU4ODIzNTI5NDExNzddXSxbMC42NyxbMCwwLjA5MDE5NjA3ODQzMTM3MjU1LDFdXSxbMC44MixbMC40OCwwLjAxLDAuNDJdXSxbMC45OSxbMSwwLDBdXV19LCJwYXJhbXMiOnsicHJvZ3Jlc3MiOjB9LCJsYXllcnMiOlt7ImVmZmVjdCI6ImdyYWRpZW50Iiwib3BhY2l0eSI6InByb2dyZXNzIiwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUGFsZXR0ZTEiLCJpbnB1dHMiOnsib2Zmc2V0Ijp7InR5cGUiOiJyc2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjQxLCJtaW4iOjAsIm1heCI6MX19LCJzaXplIjowLjUsInJvdGF0aW9uIjowfX1dfQ"
ArtifactWaitingPattern = "CTP-eyJpZCI6IjY1YmNiOTNmLTE5MTktNGFiNi1iZWQ4LWVmOGQyZmRjN2Q1OSIsInZlcnNpb24iOjIsIm5hbWUiOiJBcnRpZmFjdCAtIFJlYWR5IiwicGFsZXR0ZXMiOnsiQ29sb3JzIjpbWzAsWzEsMCwwXV0sWzAuMTUsWzEsMC43MTc2NDcwNTg4MjM1Mjk0LDBdXSxbMC4yOSxbMC45MDE5NjA3ODQzMTM3MjU1LDEsMF1dLFswLjQ0LFswLjI4MjM1Mjk0MTE3NjQ3MDYsMSwwXV0sWzAuNTksWzAsMC44NjY2NjY2NjY2NjY2NjY3LDFdXSxbMC43MyxbMC4wNjY2NjY2NjY2NjY2NjY2NywwLDFdXSxbMC44NixbMC41MTc2NDcwNTg4MjM1Mjk1LDAsMV1dLFswLjk4LFsxLDAsMC43NDkwMTk2MDc4NDMxMzczXV1dLCJPdmVybGF5IjpbWzAsWzAsMCwwXV0sWzEsWzAuNTY4NjI3NDUwOTgwMzkyMSwwLjU2ODYyNzQ1MDk4MDM5MjEsMC41Njg2Mjc0NTA5ODAzOTIxXV1dLCJDaGFzZXIgT3ZlcmxheSI6W1swLFsxLDEsMV1dLFsxLFsxLDEsMV1dXX0sInBhcmFtcyI6eyJDb2xvciI6MC41OSwiVGltZXIiOjF9LCJsYXllcnMiOlt7ImVmZmVjdCI6InNvbGlkIiwib3BhY2l0eSI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjU3LCJtaW4iOjAsIm1heCI6MC44Mn19LCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJDb2xvcnMiLCJpbnB1dHMiOnsib2Zmc2V0IjoiQ29sb3IifX0seyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjAuNDcsImJsZW5kIjoib3ZlcmxheSIsInBhbGV0dGUiOiJPdmVybGF5IiwiaW5wdXRzIjp7ImRlbnNpdHkiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC4zMywibWluIjowLjE1LCJtYXgiOjAuNjl9fSwib2Zmc2V0Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMzIsIm1pbiI6MCwibWF4IjoxfX19fSx7ImVmZmVjdCI6InNwYXJrbGVzIiwib3BhY2l0eSI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjU1LCJtaW4iOjAsIm1heCI6MC42N319LCJibGVuZCI6Im5vcm1hbC1ub25ibGFjayIsInBhbGV0dGUiOiJPdmVybGF5IiwiaW5wdXRzIjp7ImRlbnNpdHkiOjAuMTksIm9mZnNldCI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjI0LCJtaW4iOjAsIm1heCI6MX19fX0seyJlZmZlY3QiOiJjaGFzZXIiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im11bHRpcGx5IiwicGFsZXR0ZSI6IkNoYXNlciBPdmVybGF5IiwiaW5wdXRzIjp7Im9mZnNldCI6IlRpbWVyIiwic2l6ZSI6MX19XX0"
# ArtifactConnectedPatternOld = "CTP-eyJpZCI6ImQyM2NlN2I4LTRhNjktNDYzMS05ODk1LTU2YzQ2ZTIzNWEyZiIsInZlcnNpb24iOjMsIm5hbWUiOiJBcnRpZmFjdCAtIENvbm5lY3RlZCIsInBhbGV0dGVzIjp7IlBhbGV0dGUxIjpbWzAuMixbMCwwLDBdXSxbMC4yOSxbMC40LDEsMF1dLFswLjM4LFswLDAsMF1dLFswLjYxLFswLDAsMF1dLFswLjcyLFswLjkzMzMzMzMzMzMzMzMzMzMsMSwwXV0sWzAuODMsWzAsMCwwXV1dLCJQYWxldHRlMiI6W1swLjEzLFswLDAsMF1dLFswLjI0LFswLDEsMC44NV1dLFswLjMyLFswLDAsMF1dLFswLjY3LFswLDAsMF1dLFswLjc3LFswLDEsMC44M11dLFswLjg3LFswLDAsMF1dXX0sInBhcmFtcyI6e30sImxheWVycyI6W3siZWZmZWN0IjoiZ3JhZGllbnQiLCJvcGFjaXR5IjowLjIsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6IlBhbGV0dGUxIiwiaW5wdXRzIjp7Im9mZnNldCI6eyJ0eXBlIjoic2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjUsIm1pbiI6MCwibWF4IjoxfX0sInNpemUiOjAuNjMsInJvdGF0aW9uIjowLjI1fX0seyJlZmZlY3QiOiJwbGFzbWEiLCJvcGFjaXR5IjowLjA2LCJibGVuZCI6InNjcmVlbiIsInBhbGV0dGUiOiJQYWxldHRlMiIsImlucHV0cyI6eyJkZW5zaXR5Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMTUsIm1pbiI6MCwibWF4IjoxfX0sIm9mZnNldCI6MX19XX0"
ArtifactConnectedPattern = "CTP-eyJpZCI6IjFhMjQ5MmUwLTY2ZGMtNGJmMi04ODY1LTYxNTIwMzNlZTk2ZSIsInZlcnNpb24iOjIsIm5hbWUiOiJBcnRpZmFjdCAtIENvbm5lY3RlZCBDb2xvcnMiLCJwYWxldHRlcyI6eyJDb2xvcnMiOltbMCxbMSwwLDBdXSxbMC4xNSxbMSwwLjcyLDBdXSxbMC4yNyxbMC45LDEsMF1dLFswLjQ0LFswLjI4LDEsMF1dLFswLjU5LFswLDAuODcsMV1dLFswLjczLFswLjA3LDAsMV1dLFswLjg2LFswLjUyLDAsMV1dLFsxLFsxLDAsMC43NV1dXSwiQnJpZ2h0bmVzcyI6W1swLjE0LFswLDAsMF1dLFswLjI1LFsxLDEsMV1dLFswLjM5LFswLDAsMF1dLFswLjU1LFswLDAsMF1dLFswLjY1LFsxLDEsMV1dLFswLjc1LFswLDAsMF1dXX0sInBhcmFtcyI6eyJDb2xvciI6MH0sImxheWVycyI6W3siZWZmZWN0Ijoic29saWQiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJDb2xvcnMiLCJpbnB1dHMiOnsib2Zmc2V0IjoiQ29sb3IifX0seyJlZmZlY3QiOiJjaGFzZXIiLCJvcGFjaXR5IjowLjYsImJsZW5kIjoibXVsdGlwbHkiLCJwYWxldHRlIjoiQnJpZ2h0bmVzcyIsImlucHV0cyI6eyJvZmZzZXQiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAuMTMsIm1heCI6MX19LCJzaXplIjowLjQ1fX0seyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjAuNywiYmxlbmQiOiJvdmVybGF5IiwicGFsZXR0ZSI6IkJyaWdodG5lc3MiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC42MSwib2Zmc2V0Ijp7InR5cGUiOiJ0cmlhbmdsZSIsImlucHV0cyI6eyJ2YWx1ZSI6MC4yOCwibWluIjowLCJtYXgiOjF9fX19XX0"
ArtifactIncorrectPattern = "CTP-eyJpZCI6IjdkYjZiOGM3LTJkZjYtNDAzNC1iZjA1LTk3MTAxZDI3N2FhZiIsInZlcnNpb24iOjEzLCJuYW1lIjoiQXJ0aWZhY3QgSW5jb3JyZWN0IiwicGFsZXR0ZXMiOnsiUGFsZXR0ZTEiOltbMC40MSxbMSwwLDBdXV19LCJwYXJhbXMiOnsiQ29sb3IiOjF9LCJsYXllcnMiOlt7ImVmZmVjdCI6ImNoYXNlciIsIm9wYWNpdHkiOnsidHlwZSI6InNxdWFyZSIsImlucHV0cyI6eyJ2YWx1ZSI6MC42OSwibWluIjowLCJtYXgiOjF9fSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUGFsZXR0ZTEiLCJpbnB1dHMiOnsib2Zmc2V0IjoxLCJzaXplIjoxfX1dfQ"
ArtifactOffPattern = "CTP-eyJpZCI6Ijk2NTRmMDA4LWNlMjUtNDAwNS04MWE0LTc0NzY5MjJlOWNmZSIsInZlcnNpb24iOjYsIm5hbWUiOiJBcnRpZmFjdCAtIE9mZiIsInBhbGV0dGVzIjp7IkNvbG9ycyI6W1swLjAyLFswLjYxOTYwNzg0MzEzNzI1NDksMC4zODgyMzUyOTQxMTc2NDcwNywwLjA4NjI3NDUwOTgwMzkyMTU3XV0sWzAuMTQsWzAuNzQxMTc2NDcwNTg4MjM1MywwLjc0OTAxOTYwNzg0MzEzNzMsMC4zMDU4ODIzNTI5NDExNzY1XV0sWzAuMjksWzAuNTA1ODgyMzUyOTQxMTc2NCwwLjgxOTYwNzg0MzEzNzI1NDksMC4yMTE3NjQ3MDU4ODIzNTI5NF1dLFswLjQzLFswLjMyOTQxMTc2NDcwNTg4MjM1LDAuODcwNTg4MjM1Mjk0MTE3NywwLjEyMTU2ODYyNzQ1MDk4MDM5XV0sWzAuNTksWzAuMDYyNzQ1MDk4MDM5MjE1NjksMC44NzA1ODgyMzUyOTQxMTc3LDAuNjU0OTAxOTYwNzg0MzEzN11dLFswLjc0LFswLjIxNTY4NjI3NDUwOTgwMzkzLDAuNTI5NDExNzY0NzA1ODgyNCwwLjcwMTk2MDc4NDMxMzcyNTRdXSxbMC44NyxbMC4wMTk2MDc4NDMxMzcyNTQ5LDAuNTI5NDExNzY0NzA1ODgyNCwwLjI0MzEzNzI1NDkwMTk2MDc4XV0sWzAuOTksWzAuNTEzNzI1NDkwMTk2MDc4NCwwLjY1ODgyMzUyOTQxMTc2NDcsMC4xNDUwOTgwMzkyMTU2ODYzXV1dLCJCcmlnaHRuZXNzIjpbWzAuMTQsWzAsMCwwXV0sWzAuMjUsWzEsMSwxXV0sWzAuMzksWzAsMCwwXV0sWzAuNTUsWzAsMCwwXV0sWzAuNjUsWzEsMSwxXV0sWzAuNzUsWzAsMCwwXV1dfSwicGFyYW1zIjp7IkNvbG9yIjp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuNDEsIm1pbiI6MCwibWF4IjoxfX19LCJsYXllcnMiOlt7ImVmZmVjdCI6InNvbGlkIiwib3BhY2l0eSI6MSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiQ29sb3JzIiwiaW5wdXRzIjp7Im9mZnNldCI6IkNvbG9yIn19LHsiZWZmZWN0Ijoic3BhcmtsZXMiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im11bHRpcGx5IiwicGFsZXR0ZSI6IkJyaWdodG5lc3MiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC4yNCwib2Zmc2V0Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMTQsIm1pbiI6MCwibWF4IjoxfX19fV19"

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
off_pattern = canopy.Pattern(ArtifactOffPattern)
waiting_pattern = canopy.Pattern(ArtifactWaitingPattern)
incorrect_pattern = canopy.Pattern(ArtifactIncorrectPattern)


class Artifact(object):
    color = 0
    local_start_time = -1
    start_time = -1
    end_time = -1
    current_tag = None
    previous_tag = None
    desired_tag = -1
    current_mode = MODE_INITIALIZING
    is_connected = False
    is_invalid_connection = False
    is_wifi_connected = False
    disable_magnet = False
    light_pattern = initializing_pattern

    def __init__(self, name, magnet_pin=1, relay_pin=2):
        self.audio = Audio()
        self.name = name
        self.magnet_pin = magnet_pin
        self.relay_pin = relay_pin
        self.mqtt = Mqtt(name, self._onMqttMessage)
        self.wifi = Wifi(hostname=self.name)
        self.nfc = NfcWrapper(self._tag_found, self._tag_lost)
        self.magnet = Magnet(pin=self.magnet_pin)
        self.relay = Relay(pin=self.relay_pin)

    async def start(self):
        self.wifi.start(self._on_wifi_connected)
        await self.nfc.start()
        self.magnet.start()
        self.audio.start()
        self.audio.play_ambient()

        print("Starting canopy")
        canopy.init([fern.LED1_DATA, fern.LED2_DATA], 100)
        asyncio.create_task(self._render_loop())

    def _onMqttMessage(self, topic, msg):
        print((topic, msg))
        try:
            events = json.loads(msg)
            if not type(events) in (tuple, list):
                events = [events]
            for data in events:
                if (
                    data.get("event") == EVENT_ARTIFACT_UPDATE
                    and data.get("id") == self.name
                ):
                    new_desired_tag = data.get("pendingRfid")
                    if (
                        new_desired_tag
                        and new_desired_tag != self.desired_tag
                        and new_desired_tag != -1
                    ):
                        print("Updating Desired Tag: ", new_desired_tag)
                        self.audio.play_pending()
                    self.desired_tag = new_desired_tag
                    self.color = data.get("color")
                    self.end_time = data.get("endTime") or -1
                    self.start_time = data.get("startTime") or -1
                    if self.start_time > 0:
                        self.local_start_time = time.time()
                    if data.get("shouldDisconnect") == False:
                        self.disable_magnet = True
                    else:
                        self.disable_magnet = False
                    if (
                        self.current_tag
                        and self.desired_tag != -1
                        and self.current_tag != self.desired_tag
                    ):
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
        self.previous_tag = None
        self.current_tag = uid
        self.is_connected = True
        self.is_invalid_connection = self.desired_tag != -1 and uid != self.desired_tag
        if self.is_invalid_connection:
            self.audio.play_incorrect()
        else:
            self.audio.play_correct()
        self._update_state(EVENT_CARD_FOUND)

    def _tag_lost(self):
        self.is_connected = False
        self.is_invalid_connection = False
        self.previous_tag = self.current_tag
        self.current_tag = None
        self.disable_magnet = False
        self.audio.play_disconnect()
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
        elif (
            self.desired_tag is not None
            and self.desired_tag != -1
            and self.current_tag is None
        ):
            self.current_mode = MODE_WAITING
        elif self.desired_tag is None or self.desired_tag == -1:
            self.current_mode = MODE_OFF
        print("updated mode: ", self.current_mode)

    def _after_update_state(self):
        # abstract method to be overridden
        pass

    def _update_state(self, event):
        self._update_mode()
        self._update_light_pattern()
        if self.current_mode == MODE_INVALID:
            if not self.disable_magnet:
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
                        "previousCard": self.previous_tag,
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
        print("Updated light patternt to: ", self.light_pattern)

    async def _update(self):
        # abstract method to be overridden
        pass

    async def _render_loop(self):
        segment = canopy.Segment(0, 0, 16)
        f = FPS(verbose=True)
        G
        while True:
            try:
                now = time.time()
                f.tick()
                self._update()
                params["Color"] = float(self.color)
                if (
                    self.start_time != -1
                    and self.end_time != -1
                    and self.local_start_time != -1
                    and self.light_pattern == waiting_pattern
                ):
                    remote_now = self.start_time + (now - self.local_start_time)
                    timer_remaining = (self.end_time - remote_now) / (
                        self.end_time - self.start_time
                    )
                    params["Timer"] = timer_remaining
                canopy.clear()
                canopy.draw(
                    segment, self.light_pattern, alpha=float(0.8), params=params
                )
                canopy.render()
            except Exception as e:
                print("Error in render loop", e)

            await asyncio.sleep(0)
