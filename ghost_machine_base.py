import asyncio
import json
import canopy
import fern
import time

# from fps import FPS
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
MODE_RUNNING = 2
MODE_READY_TO_PRINT = 4
MODE_FINISHED = 3

# Local Events
EVENT_FINISHED_BOOT = "finishedBoot"
EVENT_CARD_FOUND = "cardFound"
EVENT_CARD_REMOVED = "cardRemoved"
EVENT_WRITE_NFC = "writeNfc"
EVENT_DONE_WRITING = "doneWriting"

EVENT_UPDATE_POWER = "updatePower"

# Remote Events
EVENT_GHOST_UPDATE = "ghostUpdate"
EVENT_RESET_COMMAND = "reset"

EVENT_SET_RUNNING = "setRunning"
EVENT_SET_FINISHED = "setFinished"
EVENT_READY_TO_PRINT = "ready_to_print"

PREVIOUS_TAG_TIMEOUT = 1


class GhostMachine(object):
    is_wifi_connected = False
    is_connected = False

    previous_tag = None
    tag_from_start = None
    previous_tag_timeout = 0

    current_tag = None
    current_tag_data = None

    current_mode = MODE_INITIALIZING

    is_writing_rfid = False
    has_invalid_tag = False

    ignore_events_while_running = True

    def __init__(
        self,
        name,
        has_wifi=True,
    ):
        self.audio = Audio()
        self.name = name
        self.has_wifi = has_wifi
        if has_wifi:
            self.mqtt = Mqtt(name, self._onMqttMessage)
            self.wifi = Wifi(hostname=self.name)
        self.nfc = NfcWrapper(self._tag_found, self._tag_lost)
        self.num_leds = 100

    async def start(self):
        if self.has_wifi:
            self.wifi.start(self._on_wifi_connected)
        await self.nfc.start()
        self.audio.start()

        print("Starting canopy")
        canopy.init([fern.LED1_DATA, fern.LED2_DATA], self.num_leds)
        self.ring_light = ring_light.RingLight(self.audio)
        asyncio.create_task(self._render_loop())

    def _handle_mqtt_event(self, event, data):
        print("Handling mqtt event: ", event)
        if event == EVENT_RESET_COMMAND:
            self._update_state(EVENT_RESET_COMMAND, should_broadcast=False)
        elif event == EVENT_SET_RUNNING:
            self._update_state(EVENT_SET_RUNNING, should_broadcast=False)
        elif event == EVENT_SET_FINISHED:
            self._update_state(EVENT_SET_FINISHED, should_broadcast=False)
        elif event == EVENT_READY_TO_PRINT:
            self._update_state(EVENT_READY_TO_PRINT, should_broadcast=False)

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
        self._update_state(EVENT_CARD_FOUND)
        print("Reading NFC")
        try:
            nfcData = await self.nfc.read()
        except:
            nfcData = None
        print("NFC Data: ", nfcData)
        self.current_tag_data = TagData(nfcData)
        if (not is_valid_tag_data_string(nfcData) or self.current_mode in [MODE_HAS_TRASH, MODE_READY_TO_PRINT, MODE_RUNNING]) and self._can_connect_tag():
            self._update_state(EVENT_WRITE_NFC)

    def _tag_lost(self):
        self.is_connected = False
        self.has_invalid_tag = False
        self.current_tag = None
        self.disable_magnet = False
        self._update_state(EVENT_CARD_REMOVED)

    async def _write_nfc(self):
        print("Trying to write NFC", self.current_tag)
        if self.current_tag:
            print("Writing NFC")
            await self.nfc.write(self.current_tag_data.serialize())
            print("Done writing NFC")
            self._update_state(EVENT_DONE_WRITING)

    def _get_power_level(self):
        if self.current_tag and self.current_tag_data:
            power = 0
            if self.current_tag_data.printer:
                power += 1
            if self.current_tag_data.audio:
                power += 1
            if self.current_tag_data.dollhouse:
                power += 1
            if self.current_tag_data.other1:
                power += 1
            if self.current_tag_data.other2:
                power += 1
            if self.current_tag_data.other3:
                power += 1
            if self.current_tag_data.scale:
                power -= 0
            return power
        else:
            return 0

    def _can_connect_tag(self):
        if self.tag_from_start:
            return self.tag_from_start == self.current_tag
        return True

    def _on_state_change(self, event):
        # Abstract method to handle state changes
        pass

    def _update_rfid_data(self):
        # Abstract method to handle updating the rfid data
        pass

    def _update_state(self, event, should_broadcast=True):
        print("is wifi connected: ", self.is_wifi_connected)
        print("is connected: ", self.is_connected)
        print("is invalid: ", self.has_invalid_tag)
        print("current tag: ", self.current_tag)

        if self.previous_tag_timeout and time.time() > self.previous_tag_timeout:
            self.previous_tag = None
            self.previous_tag_timeout = 0
            print("Resetting previous tag")

        if event == EVENT_FINISHED_BOOT:
            self.current_mode = MODE_WAITING_FOR_TRASH
            self.ring_light.set_mode(ring_light.MODE_WAITING)
        elif event == EVENT_CARD_FOUND:
            if self._can_connect_tag():
                self.has_invalid_tag = False
                if self.current_mode == MODE_WAITING_FOR_TRASH and self.current_tag != self.previous_tag:
                    self.current_mode = MODE_HAS_TRASH
                    self.previous_tag = self.current_tag
                    # self.tag_from_start = self.current_tag
                else:
                    print("Refusing tag scan because previous tag")
                    should_broadcast = not self.ignore_events_while_running
                    self.previous_tag_timeout = 0
            else:
                print("refusing tag scan because it is invalid")
                self.has_invalid_tag = True
                should_broadcast = False
        elif event == EVENT_CARD_REMOVED:
            self.has_invalid_tag = False
            self.is_writing_rfid = False
            if not self.tag_from_start and self.current_mode not in [MODE_RUNNING, MODE_READY_TO_PRINT]:
                self.current_mode = MODE_WAITING_FOR_TRASH
                self.previous_tag_timeout = time.time() + PREVIOUS_TAG_TIMEOUT
            else:
                print("Ignoring tag removing because game is running")
                should_broadcast = not self.ignore_events_while_running
        elif event == EVENT_WRITE_NFC:
            if not self.has_invalid_tag:
                if self.has_wifi and self.mqtt.is_connected:
                    self.mqtt.send_message(
                        json.dumps(
                            {
                                "event": EVENT_UPDATE_POWER,
                                "reader": self.name,
                                "card": self.current_tag,
                                "power": self._get_power_level(),
                                "connected": self.is_connected,
                                "invalid": self.has_invalid_tag,
                            }
                        )
                    )
                # if self.current_mode in [MODE_HAS_TRASH, MODE_WAITING_FOR_TRASH]:
                #     self.current_mode = MODE_HAS_TRASH
                self._update_rfid_data()
                self.is_writing_rfid = True
                asyncio.create_task(self._write_nfc())
        elif event == EVENT_DONE_WRITING:
            print("Done writing NFC")
            self.is_writing_rfid = False
            # if 
            # # self.tag_from_start = None
            # if self.current_tag:
            #     self.current_mode = MODE_FINISHED
            # else:
            #     self.current_mode = MODE_WAITING_FOR_TRASH
        elif event == EVENT_RESET_COMMAND:
            if self.current_tag is None:
                self.previous_tag = None
            # else:
            #     self.previous_tag_timeout = time.time() + PREVIOUS_TAG_TIMEOUT
            self.tag_from_start = None
            self.current_mode = MODE_WAITING_FOR_TRASH
            self.current_tag = None
            self.current_tag_data = None
        elif event == EVENT_SET_RUNNING:
            self.current_mode = MODE_RUNNING
            if self.current_tag:
                self.tag_from_start = self.current_tag
            else:
                self.tag_from_start = self.previous_tag
        elif event == EVENT_READY_TO_PRINT:
            self.current_mode = MODE_READY_TO_PRINT
            if self.current_tag:
                self.tag_from_start = self.current_tag
            else:
                self.tag_from_start = self.previous_tag
        elif event == EVENT_SET_FINISHED:
            if self.current_tag is None:
                self.previous_tag = None
            # else:
            #     self.previous_tag_timeout = time.time() + PREVIOUS_TAG_TIMEOUT
            # self.previous_tag = None
            self.tag_from_start = None
            self.current_mode = MODE_FINISHED

        print("updated mode: ", self.current_mode, event)
        self._update_ring_light_pattern()
        self._on_state_change(event)

        if event and should_broadcast and self.has_wifi and self.mqtt.is_connected:
            self.mqtt.send_message(
                json.dumps(
                    {
                        "event": event,
                        "reader": self.name,
                        "card": self.current_tag,
                        "power": self._get_power_level(),
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
        elif self.current_mode == MODE_RUNNING or self.current_mode == MODE_READY_TO_PRINT:
            self.ring_light.set_mode(ring_light.MODE_RUNNING)
        elif self.current_mode == MODE_FINISHED:
            self.ring_light.set_mode(ring_light.MODE_FINISHED)
        print("Updated light pattern to: ", self.ring_light.current_mode)

    async def _render_loop(self):
        # f = FPS(verbose=True)
        while True:
            try:
                # f.tick()
                canopy.clear()
                self.ring_light.draw()
                self._draw_light_patterns()
                canopy.render()
            except Exception as e:
                print("Error in render loop", e)

            await asyncio.sleep(0.1)
