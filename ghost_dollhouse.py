import asyncio
import canopy
import fern
import time
from button import Button

from fps import FPS
from nfc import NfcWrapper
from rat_relay import Relay
from ghost_magnet import Magnet
from audio import Audio
from ghost_dollhouse_audio import DollhouseAudio
import ring_light
import ghost_dollhouse_room as DollhouseRooms
from ghost_tag_data import (
    is_valid_tag_data_string,
    TagData,
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
EVENT_BUTTON_PRESSED = "buttonPressed"

BUTTON_RESET = -1
BUTTON_BEDROOM = 0
BUTTON_CONSERVATORY = 1
BUTTON_STUDY = 2
BUTTON_FIREPLACE = 3
BUTTON_ATTIC = 4

MODE_INITIALIZING = -1
MODE_GAME_PLAYING = 0
MODE_GAME_WON = 1

WIN_TIME_LENGTH_S = 60
MAGNET_RESET_TIME_S = 5

WINNING_ORDER = [
    BUTTON_BEDROOM,
    BUTTON_CONSERVATORY,
    BUTTON_STUDY,
    BUTTON_FIREPLACE,
    BUTTON_ATTIC,
]

MATRIX_CHANGES = [
    [1, 0, 0, 0, 0],
    [1, 1, 0, 0, 0],
    [1, 1, 1, 0, 0],
    [1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1],
]


class GhostDollhouse(object):
    magnet_pin = 1
    relay_pin = 2

    current_tag = None
    current_mode = MODE_INITIALIZING
    magnet = None
    state = [False, False, False, False, False]
    win_time = 0
    magnet_open_time = 0

    room_states_map = {}

    def __init__(self):
        self.audio = Audio()
        self.dollhouse_audio = DollhouseAudio(self.audio)
        self.nfc = NfcWrapper(self._tag_found, self._tag_lost)
        self.relay = Relay(pin=self.relay_pin)
        self.magnet = Magnet(pin=self.magnet_pin)

        def get_button_callback(button_num):
            print("Button callback for ", button_num)
            
            def button(btn):
                print("Button inner callback for ", button_num)
                if btn.pressed():
                    self.button_callback(button_num)
            return button

        self.buttons = [
            Button(fern.D3, get_button_callback(BUTTON_RESET)),
            Button(fern.D4, get_button_callback(BUTTON_STUDY)),
            Button(fern.D5, get_button_callback(BUTTON_CONSERVATORY)),
            Button(fern.D6, get_button_callback(BUTTON_FIREPLACE)),
            Button(fern.D7, get_button_callback(BUTTON_BEDROOM)),
            Button(fern.D8, get_button_callback(BUTTON_ATTIC)),
        ]

    async def start(self):
        await self.nfc.start()
        self.audio.start()

        print("Starting canopy")
        canopy.init([fern.LED1_DATA, fern.LED2_DATA], 300)
        asyncio.create_task(self._render_loop())

        self.ring_light = ring_light.RingLight(self.audio)
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

        if button == BUTTON_RESET:
            self.magnet.open()
            self.magnet_open_time = time.time() + MAGNET_RESET_TIME_S
            self._update_state(EVENT_BUTTON_PRESSED)
            print("Temp Opening Door", self.magnet_open_time)
            return

        old_state = self.state
        matrix = MATRIX_CHANGES[button]
        self.state = [old_state[i] and matrix[i] for i in range(0, 5)]
        self.state[button] = 1
        if button == BUTTON_STUDY:
            self.dollhouse_audio.play_study()
        elif button == BUTTON_CONSERVATORY:
            self.dollhouse_audio.play_conservatory()
        elif button == BUTTON_FIREPLACE:
            self.dollhouse_audio.play_fireplace()
        elif button == BUTTON_BEDROOM:
            self.dollhouse_audio.play_bedroom()
        elif button == BUTTON_ATTIC:
            self.dollhouse_audio.play_attic()

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
            self.dollhouse_audio.play_turn_off()
        if all_lights_on:
            self._update_state(EVENT_WIN_GAME)
        else:
            self._update_state(EVENT_BUTTON_PRESSED)

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
        return self.current_mode == MODE_GAME_WON  # and self.current_tag and not self.current_tag_data.dollhouse

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
            self.dollhouse_audio.play_ambient()
        if event == EVENT_CARD_FOUND:
            if self._can_connect_tag():
                print("Tag connected and game won")
                self.ring_light.set_mode(ring_light.MODE_CONNECTED)
                event = EVENT_WRITE_NFC
            else:
                print("Tag connected but game not won")
                self.magnet.open()
                self.ring_light.set_mode(ring_light.MODE_INVALID)
        if event == EVENT_CARD_REMOVED:
            if self.current_mode is MODE_GAME_WON:
                self.ring_light.set_mode(ring_light.MODE_WAITING)
            else:
                self.ring_light.set_mode(ring_light.MODE_OFF)
                self.magnet.close()
        if event == EVENT_WRITE_NFC:
            if (
                self.current_tag and self.ring_light.current_mode is not ring_light.MODE_WRITING
            ):
                self.ring_light.set_mode(ring_light.MODE_WRITING)
                asyncio.create_task(self._write_nfc())
            else:
                print("Cannot write NFC mode")
        if event == EVENT_DONE_WRITING:
            if self.current_mode == MODE_GAME_WON:
                if self.current_tag:
                    self.ring_light.set_mode(ring_light.MODE_FINISHED)
                else:
                    self.ring_light.set_mode(ring_light.MODE_WAITING_TO_WRITE)
            else:
                self.ring_light.set_mode(ring_light.MODE_OFF)
        if event == EVENT_WIN_GAME:
            self.current_mode = MODE_GAME_WON
            self.ring_light.set_mode(ring_light.MODE_WAITING_TO_WRITE)
            self.win_time = time.time()
            self.magnet.open()
            self.dollhouse_audio.play_win_game()
        if event == EVENT_RESET_GAME:
            self.current_mode = MODE_GAME_PLAYING
            self.ring_light.set_mode(ring_light.MODE_OFF)
            self.state = [False, False, False, False, False]
            self.magnet.close()

        print("updated mode: ", self.current_mode)
        print("updated ring mode: ", self.ring_light.current_mode)

        self._update_house_lights()

        # if self.current_mode == MODE_GAME_WON :
        #     self.relay.on()
        # else:
        #     self.relay.off()

    async def _render_loop(self):
        f = FPS(verbose=True)
        while True:
            try:
                if self.current_mode == MODE_GAME_WON and (
                    time.time() - self.win_time > WIN_TIME_LENGTH_S
                ):
                    self._update_state(EVENT_RESET_GAME)
                    self.win_time = -1
                if self.magnet_open_time > 0 and time.time() > self.magnet_open_time:
                    print("Resetting Magnet")
                    self.magnet.close()
                    self.magnet_open_time = -1
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
