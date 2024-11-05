import asyncio
import json
import canopy
import fern

from fps import FPS
from nfc import NfcWrapper
from rat_mqtt import Mqtt
from rat_wifi import Wifi
from audio import Audio
import ring_light

from ghost_tag_data import (
    is_valid_tag_data_string,
    TagData,
)


MODE_INITIALIZING = -1
MODE_WAITING_FOR_TRASH = 0
MODE_HAS_TRASH = 1
MODE_READY_TO_WRITE = 2
MODE_FINISHED = 3

# Local Events
EVENT_FINISHED_BOOT = "finishedBoot"
EVENT_CARD_FOUND = "cardFound"
EVENT_CARD_REMOVED = "cardRemoved"
EVENT_WRITE_NFC = "writeNfc"
EVENT_DONE_WRITING = "doneWriting"

# Remote Events
EVENT_GHOST_UPDATE = "ghostUpdate"
EVENT_RESET_COMMAND = "reset"
EVENT_WRITE_RFID_COMMAND = "writeRfid"


class GhostMachine(object):
    is_wifi_connected = False
    is_connected = False

    tag_from_start = None
    current_tag = None
    current_tag_data = None

    current_mode = MODE_INITIALIZING

    is_writing_rfid = False
    has_invalid_tag = False

    def __init__(
        self,
        name,
    ):
        self.audio = Audio()
        self.name = name
        self.mqtt = Mqtt(name, self._onMqttMessage)
        self.wifi = Wifi(hostname=self.name)
        self.nfc = NfcWrapper(self._tag_found, self._tag_lost)

    async def start(self):
        self.wifi.start(self._on_wifi_connected)
        await self.nfc.start()
        self.audio.start()

        print("Starting canopy")
        canopy.init([fern.LED1_DATA, fern.LED2_DATA], 100)
        self.ring_light = ring_light.RingLight(self.audio)
        asyncio.create_task(self._render_loop())

    def _handle_mqtt_event(self, event, data):
        if event == EVENT_RESET_COMMAND:
            self._update_state(EVENT_RESET_COMMAND, should_broadcast=False)
        elif event == EVENT_WRITE_RFID_COMMAND:
            self._update_state(EVENT_WRITE_NFC, should_broadcast=False)

    def _onMqttMessage(self, topic, msg):
        print((topic, msg))
        try:
            events = json.loads(msg)
            if type(events) not in (tuple, list):
                events = [events]
            for data in events:
                if (data.get("event") == EVENT_GHOST_UPDATE and data.get("id") == self.name):
                    command = data.get("command")
                    self._handle_mqtt_event(command, data)
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

    async def _tag_found(self, uid):
        self.current_tag = uid
        self.is_connected = True
        print("Reading NFC")
        nfcData = await self.nfc.read()
        print("NFC Data: ", nfcData)
        self.current_tag_data = TagData(nfcData)
        self._update_state(EVENT_CARD_FOUND)
        if not is_valid_tag_data_string(nfcData):
            self._update_state(EVENT_WRITE_NFC)

    def _tag_lost(self):
        self.is_connected = False
        self.has_invalid_tag = False
        self.current_tag = None
        self.disable_magnet = False
        self._update_state(EVENT_CARD_REMOVED)

    async def _write_nfc(self):
        if self.current_tag:
            print("Writing NFC")
            self.is_writing_rfid = True
            await self.nfc.write(self.current_tag_data.serialize())
            print("Done writing NFC")
            self.is_writing_rfid = False
            self._update_state(EVENT_DONE_WRITING)

    def _can_connect_tag(self):
        if self.tag_from_start:
            return self.tag_from_start == self.current_tag
        return True
    
    def _on_state_change(self, event):
        # Abstract method to handle state changes
        pass

    def _update_state(self, event, should_broadcast=True):
        print("is wifi connected: ", self.is_wifi_connected)
        print("is connected: ", self.is_connected)
        print("is invalid: ", self.has_invalid_tag)
        print("current tag: ", self.current_tag)

        if event == EVENT_FINISHED_BOOT:
            self.current_mode = MODE_WAITING_FOR_TRASH
            self.ring_light.set_mode(ring_light.MODE_WAITING)
        elif event == EVENT_CARD_FOUND:
            if self._can_connect_tag():
                self.has_invalid_tag = False
                if self.current_mode == MODE_WAITING_FOR_TRASH:
                    self.current_mode = MODE_HAS_TRASH
                    self.tag_from_start = self.current_tag
            else:
                self.has_invalid_tag = True
        elif event == EVENT_CARD_REMOVED:
            self.has_invalid_tag = False
            if self.tag_from_start:
                # self.audio.play_please_reconnect()
                pass
            else:
                self.current_mode = MODE_WAITING_FOR_TRASH
        elif event == EVENT_WRITE_NFC:
            self.current_mode = MODE_READY_TO_WRITE
        elif event == EVENT_DONE_WRITING:
            self.tag_from_start = None
            if self.current_tag:
                self.current_mode = MODE_FINISHED
            else:
                self.current_mode = MODE_WAITING_FOR_TRASH
        elif event == EVENT_RESET_COMMAND:
            self.tag_from_start = None
            self.current_mode = MODE_FINISHED
            self.has_invalid_tag = True

        # Write the RFID if we're ready
        if self.current_mode == MODE_READY_TO_WRITE and self.current_tag and not self.has_invalid_tag and not self.is_writing_rfid:
            self._write_nfc()

        print("updated mode: ", self.current_mode)
        self._update_ring_light_pattern()
        self._on_state_change(event)

        if event and should_broadcast and self.mqtt.is_connected:
            self.mqtt.send_message(
                json.dumps(
                    {
                        "event": event,
                        "reader": self.name,
                        "card": self.current_tag,
                        # "cardData": self.current_tag_data,
                        "connected": self.is_connected,
                        "invalid": self.has_invalid_tag,
                    }
                )
            )

    def _draw_light_patterns(self):
        # Abstract method to draw the light patterns
        pass

    def _update_ring_light_pattern(self):
        if self.current_mode == MODE_INITIALIZING:
            self.ring_light.set_mode(ring_light.MODE_INITIALIZING)
        elif self.has_invalid_tag:
            self.ring_light.set_mode(ring_light.MODE_INVALID)
        elif self.is_writing_rfid:
            self.ring_light.set_mode(ring_light.MODE_WRITING)
        elif self.current_mode == MODE_WAITING_FOR_TRASH:
            self.ring_light.set_mode(ring_light.MODE_WAITING)
        elif self.current_mode == MODE_HAS_TRASH:
            self.ring_light.set_mode(ring_light.MODE_CONNECTED)
        elif self.current_mode == MODE_READY_TO_WRITE:
            self.ring_light.set_mode(ring_light.MODE_WAITING_TO_WRITE)
        elif self.current_mode == MODE_FINISHED:
            self.ring_light.set_mode(ring_light.MODE_FINISHED)
        print("Updated light pattern to: ", self.ring_light.current_mode)

    async def _render_loop(self):
        f = FPS(verbose=True)
        while True:
            try:
                f.tick()
                canopy.clear()
                self.ring_light.draw()
                self._draw_light_patterns()
                canopy.render()
            except Exception as e:
                print("Error in render loop", e)

            await asyncio.sleep(0)
