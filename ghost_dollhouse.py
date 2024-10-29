import asyncio
import json
import canopy
import fern
import time
from debounced_input import DebouncedInput
from machine import Pin

from fps import FPS
from nfc import NfcWrapper
from rat_mqtt import Mqtt
from rat_wifi import Wifi
from rat_relay import Relay
from ghost_magnet import Magnet
from rat_audio import Audio
import ring_light
import ghost_dollhouse_room as DollhouseRooms
from ghost_tag_data import (
    is_valid_tag_data_string,
    TagData,
    DOLLHOUSE,
)


# Local Events
EVENT_FINISHED_BOOT = "finishedBoot"
EVENT_CARD_FOUND = "cardFound"
EVENT_CARD_REMOVED = "cardRemoved"
EVENT_WRITE_NFC = "writeNfc"
EVENT_DONE_WRITING = "doneWriting"
EVENT_WRITE_RFID_COMMAND = "writeRfid"

EVENT_WIN_GAME = "winGame"
EVENT_RESET_GAME = "resetGame"

BUTTON_STUDY = 0
BUTTON_CONSERVATORY = 1
BUTTON_FIREPLACE = 2
BUTTON_BEDROOM = 3
BUTTON_ATTIC = 4

MODE_INITIALIZING = -1
MODE_GAME_PLAYING = 0
MODE_GAME_WON = 1

WIN_TIME_LENGTH_S = 20

WINNING_ORDER = [
    BUTTON_FIREPLACE,
    BUTTON_BEDROOM,
    BUTTON_ATTIC,
    BUTTON_STUDY,
    BUTTON_CONSERVATORY,
]

MATRIX_CHANGES = [
    [1, 0, 1, 1, 1],
    [1, 1, 1, 1, 1],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 1, 0],
    [0, 0, 1, 1, 1],
]


class GhostDollhouse(object):
    current_tag = None
    current_mode = MODE_INITIALIZING
    magnet = None
    state = [False, False, False, False, False]
    win_time = 0

    room_states_map = {}

    def __init__(
        self,
        name=DOLLHOUSE,
        magnet_pin=1,
        relay_pin=2,
    ):
        self.audio = Audio(name)
        self.name = name
        self.magnet_pin = magnet_pin
        self.relay_pin = relay_pin
        self.nfc = NfcWrapper(self._tag_found, self._tag_lost)
        self.relay = Relay(pin=self.relay_pin)
        self.magnet = Magnet(pin=self.magnet_pin)

        def get_button_callback(button):
            return lambda: self.button_callback(button)

        self.buttons = [
            DebouncedInput(
                fern.D8, get_button_callback(BUTTON_STUDY), Pin.PULL_UP, False, 50
            ),
            DebouncedInput(
                fern.D7,
                get_button_callback(BUTTON_CONSERVATORY),
                Pin.PULL_UP,
                False,
                50,
            ),
            DebouncedInput(
                fern.D6,
                get_button_callback(BUTTON_FIREPLACE),
                Pin.PULL_UP,
                False,
                50,
            ),
            DebouncedInput(
                fern.D5,
                get_button_callback(BUTTON_BEDROOM),
                Pin.PULL_UP,
                False,
                50,
            ),
            DebouncedInput(
                fern.D4,
                get_button_callback(BUTTON_ATTIC),
                Pin.PULL_UP,
                False,
                50,
            ),
        ]

    async def start(self):
        await self.nfc.start()
        self.audio.start()
        self.audio.play_ambient()

        print("Starting canopy")
        canopy.init([fern.LED1_DATA, fern.LED2_DATA], 300)
        asyncio.create_task(self._render_loop())

        self.ring_light = ring_light.RingLight()
        self.room_states = {}
        self.room_states[DollhouseRooms.HIDDEN_ROOM] = DollhouseRooms.HiddenRoomState()
        self.room_states[DollhouseRooms.KITCHEN] = DollhouseRooms.KitchenState()
        self.room_states[DollhouseRooms.STUDY] = DollhouseRooms.StudyState()
        self.room_states[DollhouseRooms.CONSERVATORY] = DollhouseRooms.ConservatoryState()
        self.room_states[DollhouseRooms.LIVING_ROOM] = DollhouseRooms.LivingRoomState()
        self.room_states[DollhouseRooms.BATHROOM] = DollhouseRooms.BathroomState()
        self.room_states[DollhouseRooms.BEDROOM] = DollhouseRooms.BedroomState()
        self.room_states[DollhouseRooms.ATTIC] = DollhouseRooms.AtticState()

        self._update_state(EVENT_FINISHED_BOOT)

    def button_callback(self, button):
        print("Button Pressed: ", button)

        old_state = self.state
        matrix = MATRIX_CHANGES[button]
        self.state = [old_state[i] and matrix[i] for i in range(0, 5)]
        self.state[button] = 1
        print("New State: ", self.state)
        has_turned_off = False
        all_lights_on = True
        for i in range(0, 5):
            if not self.state[i]:
                all_lights_on = False
            if old_state[i] and not self.state[i]:
                has_turned_off = True
                print(f"Turned off index {i}")
            elif not old_state[i] and self.state[i]:
                print(f"Turned on index {i}")
        if has_turned_off:
            print("Turned off some lights!")
            # Play sounds?
        if all_lights_on:
            self._update_state(EVENT_WIN_GAME)

    async def _tag_found(self, uid):
        self.current_tag = uid
        print("Reading NFC")
        try:
            nfcData = await self.nfc.read()
        except Exception as e:
            print(e)
            nfcData = ''
        print("NFC Data: ", nfcData)
        self.current_tag_data = TagData(nfcData)
        self._update_state(EVENT_CARD_FOUND)
        if not is_valid_tag_data_string(nfcData):
            print("Invalid tag data")
            self._update_state(EVENT_WRITE_NFC)

    def _tag_lost(self):
        self.current_tag = None
        self._update_state(EVENT_CARD_REMOVED)

    async def _write_nfc(self):
        if self.current_tag:
            print("Writing NFC")
            await self.nfc.write(self.current_tag_data.serialize())
            print("Done writing NFC")
            self._update_state(EVENT_DONE_WRITING)
        else:
            print("Cannot write NFC without a tag")

    def _can_connect_tag(self):
        return self.current_mode == MODE_GAME_WON

    def _update_house_lights(self):
        if self.current_mode == MODE_GAME_WON:
            self.room_states[DollhouseRooms.HIDDEN_ROOM].set_state(
                DollhouseRooms.WIN_STATE
            )
            self.room_states[DollhouseRooms.KITCHEN].set_state(DollhouseRooms.WIN_STATE)
            self.room_states[DollhouseRooms.STUDY].set_state(DollhouseRooms.WIN_STATE)
            self.room_states[DollhouseRooms.LIVING_ROOM].set_state(
                DollhouseRooms.WIN_STATE
            )
            self.room_states[DollhouseRooms.CONSERVATORY].set_state(
                DollhouseRooms.WIN_STATE
            )
            self.room_states[DollhouseRooms.BATHROOM].set_state(
                DollhouseRooms.WIN_STATE
            )
            self.room_states[DollhouseRooms.BEDROOM].set_state(DollhouseRooms.WIN_STATE)
            self.room_states[DollhouseRooms.ATTIC].set_state(DollhouseRooms.WIN_STATE)
        else:
            self.room_states[DollhouseRooms.HIDDEN_ROOM].set_state(False)
            self.room_states[DollhouseRooms.KITCHEN].set_state(self.state[BUTTON_STUDY])
            self.room_states[DollhouseRooms.STUDY].set_state(self.state[BUTTON_STUDY])
            self.room_states[DollhouseRooms.LIVING_ROOM].set_state(
                self.state[BUTTON_FIREPLACE]
            )
            self.room_states[DollhouseRooms.CONSERVATORY].set_state(
                self.state[BUTTON_CONSERVATORY]
            )
            self.room_states[DollhouseRooms.BATHROOM].set_state(
                self.state[BUTTON_BEDROOM]
            )
            self.room_states[DollhouseRooms.BEDROOM].set_state(
                self.state[BUTTON_BEDROOM]
            )
            self.room_states[DollhouseRooms.ATTIC].set_state(self.state[BUTTON_ATTIC])

    def _update_state(self, event):
        print("updating state with event: ", event)
        print("current tag: ", self.current_tag)

        if event == EVENT_FINISHED_BOOT:
            self.current_mode = MODE_GAME_PLAYING
            self.ring_light.set_mode(ring_light.MODE_OFF)
            self.magnet.close()
        elif event == EVENT_CARD_FOUND:
            if self._can_connect_tag():
                self.audio.play_correct()
                self.ring_light.set_mode(ring_light.MODE_CONNECTED)
            else:
                self.audio.play_incorrect()
                self.magnet.open()
                self.ring_light.set_mode(ring_light.MODE_INVALID)
        elif event == EVENT_CARD_REMOVED:
            self.audio.play_disconnect()
            if self.current_mode is MODE_GAME_WON:
                self.ring_light.set_mode(ring_light.MODE_WAITING)
            else:
                self.ring_light.set_mode(ring_light.MODE_OFF)
                self.magnet.close()
        elif event == EVENT_WRITE_NFC:
            if (
                self.current_tag
                and self.ring_light.current_mode is not ring_light.MODE_WRITING
            ):
                self.previous_mode = self.current_mode
                self.ring_light.set_mode(ring_light.MODE_WRITING)
                asyncio.create_task(self._write_nfc())
            else:
                print("Cannot write NFC mode")
        elif event == EVENT_DONE_WRITING:
            if self.current_mode == MODE_GAME_WON:
                self.ring_light.set_mode(ring_light.MODE_WAITING)
            else:
                self.ring_light.set_mode(ring_light.MODE_OFF)
        elif event == EVENT_WIN_GAME:
            self.current_mode = MODE_GAME_WON
            self.ring_light.set_mode(ring_light.MODE_WAITING)
            self.win_time = time.time()
            self.magnet.open()
        elif event == EVENT_RESET_GAME:
            self.current_mode = MODE_GAME_PLAYING
            self.ring_light.set_mode(ring_light.MODE_OFF)
            self.magnet.close()

        print("updated mode: ", self.current_mode)
        print("updated ring mode: ", self.ring_light.current_mode)

        self._update_house_lights()

        if self.current_mode == MODE_GAME_WON:
            self.relay.on()
        else:
            self.relay.off()

    async def _render_loop(self):
        if self.current_mode == MODE_GAME_WON and (
            time.time() - self.win_time > WIN_TIME_LENGTH_S
        ):
            self._update_state(EVENT_RESET_GAME)
        f = FPS(verbose=True)
        while True:
            try:
                f.tick()
                canopy.clear()
                self.ring_light.draw()
                for room in self.room_states:
                    room_state = self.room_states[room]
                    room_state.draw()
                canopy.render()
            except Exception as e:
                print("Error in render loop", e)

            await asyncio.sleep(0)
