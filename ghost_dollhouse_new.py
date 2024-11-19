import time
import asyncio
import fern

from button import Button

import ghost_machine_base
from ghost_magnet import Magnet
from ghost_dollhouse_audio import DollhouseAudio
import ghost_dollhouse_room as DollhouseRooms
import ring_light


EVENT_WIN_GAME = "winGame"
EVENT_RESET_GAME = "resetGame"
EVENT_BUTTON_PRESSED = "buttonPressed"

BUTTON_RESET = -1
BUTTON_BEDROOM = 0
BUTTON_CONSERVATORY = 1
BUTTON_STUDY = 2
BUTTON_FIREPLACE = 3
BUTTON_ATTIC = 4

# MODE_INITIALIZING = -1
# MODE_GAME_PLAYING = 0
# MODE_GAME_WON = 1

WIN_TIME_LENGTH_S = 60
MAGNET_RESET_TIME_S = 5
GAME_TIMEOUT_S = 20

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


class GhostDollhouse(ghost_machine_base.GhostMachine):

    def __init__(self):
        super().__init__("listening", has_wifi=False)
        self.dollhouse_audio = DollhouseAudio(self.audio)
        self.magnet = Magnet(pin=1)
        self.state = [False, False, False, False, False]
        self.win_time = 0
        self.magnet_open_time = 0
        self.room_states = {}
        self.num_leds = 300
        self.is_finished = False
        self.reset_time = 0

    async def start(self):
        await super().start()
        self.dollhouse_audio.play_ambient()
        self.room_states[DollhouseRooms.HIDDEN_ROOM] = DollhouseRooms.HiddenRoomState()
        self.room_states[DollhouseRooms.KITCHEN] = DollhouseRooms.KitchenState()
        self.room_states[DollhouseRooms.STUDY] = DollhouseRooms.StudyState()
        self.room_states[DollhouseRooms.CONSERVATORY] = DollhouseRooms.ConservatoryState()
        self.room_states[DollhouseRooms.LIVING_ROOM] = DollhouseRooms.LivingRoomState()
        self.room_states[DollhouseRooms.BATHROOM] = DollhouseRooms.BathroomState()
        self.room_states[DollhouseRooms.BEDROOM] = DollhouseRooms.BedroomState()
        self.room_states[DollhouseRooms.ATTIC] = DollhouseRooms.AtticState()

        def get_button_callback(button_num):
            print("Button callback for ", button_num)

            def button(btn):
                print("Button inner callback for ", button_num)
                self.button_callback(button_num)
            return button

        self.buttons = [
            Button(fern.D8, get_button_callback(BUTTON_RESET)),
            Button(fern.D4, get_button_callback(BUTTON_STUDY)),
            Button(fern.D5, get_button_callback(BUTTON_CONSERVATORY)),
            Button(fern.D6, get_button_callback(BUTTON_FIREPLACE)),
            Button(fern.D7, get_button_callback(BUTTON_BEDROOM)),
            Button(fern.D3, get_button_callback(BUTTON_ATTIC)),
        ]
        asyncio.create_task(self.buttons[0].run())
        asyncio.create_task(self.buttons[1].run())
        asyncio.create_task(self.buttons[2].run())
        asyncio.create_task(self.buttons[3].run())
        asyncio.create_task(self.buttons[4].run())
        asyncio.create_task(self.buttons[5].run())
        self._update_state(ghost_machine_base.EVENT_FINISHED_BOOT)

    def _update_rfid_data(self):
        super()._update_rfid_data()
        self.current_tag_data.dollhouse = True

    def _can_connect_tag(self):
        return self.is_finished  # self.current_mode == ghost_machine_base.MODE_FINISHED  # and self.current_tag and not self.current_tag_data.dollhouse

    def _on_state_change(self, event):
        super()._on_state_change(event)
        self.previous_tag = None

        # if self.has_invalid_tag:
        #     self.ring_light.set_mode(ring_light.MODE_INVALID)

        if event in [ghost_machine_base.EVENT_FINISHED_BOOT, ghost_machine_base.EVENT_RESET_COMMAND, EVENT_RESET_GAME]:
            self.magnet.close()
            self.is_finished = False
        if event in [EVENT_WIN_GAME]:
            print("Finished Game")
            # self.current_mode = ghost_machine_base.MODE_FINISHED
            self.is_finished = True
            self.reset_time = 0
            self.state = [False, False, False, False, False]
            self.win_time = time.time()
            self.magnet.open()
            self.dollhouse_audio.play_win_game()
            # self._update_state(ghost_machine_base.MODE_WAITING_FOR_TRASH)
        if event in [EVENT_RESET_GAME]:
            print("Resetting Game")
            # self.current_mode = ghost_machine_base
            self.state = [False, False, False, False, False]
            self.is_finished = False
            self.reset_time = 0
            self.magnet.close()

        if event in [ghost_machine_base.EVENT_DONE_WRITING]:
            self.has_invalid_tag = True
            self.dollhouse_audio.play_correct()

        if self.has_invalid_tag:
            print("Temp Opening Door", self.magnet_open_time)
            self.magnet.open()
            self.magnet_open_time = time.time() + MAGNET_RESET_TIME_S
            self.ring_light.set_mode(ring_light.MODE_INVALID)
        elif not self.is_finished:
            self.ring_light.set_mode(ring_light.MODE_OFF)
        elif event in [ghost_machine_base.EVENT_CARD_FOUND]:
            self.ring_light.set_mode(ring_light.MODE_CONNECTED)
        elif event in [ghost_machine_base.EVENT_DONE_WRITING]:
            self.ring_light.set_mode(ring_light.MODE_INVALID)
        else:
            self.ring_light.set_mode(ring_light.MODE_WAITING)
        self._update_house_lights()

    def _draw_light_patterns(self):
        super()._draw_light_patterns()

        if self.is_finished and self.win_time > 0 and (
            time.time() - self.win_time > WIN_TIME_LENGTH_S
        ):
            print("Resetting Game")
            self._update_state(EVENT_RESET_GAME)
            self.win_time = -1

        if self.reset_time > 0 and time.time() > self.reset_time:
            print("Resetting Game timeout")
            self._update_state(EVENT_RESET_GAME)
            self.reset_time = 0
        if self.magnet_open_time > 0 and time.time() > self.magnet_open_time:
            print("Resetting Magnet")
            self.magnet.close()
            self.magnet_open_time = -1

        for room in self.room_states:
            room_state = self.room_states[room]
            room_state.draw()
            asyncio.sleep(0.25)

    def _update_ring_light_pattern(self):
        pass
        # if self.has_invalid_tag:
        #     self.ring_light.set_mode(ring_light.MODE_INVALID)
        # elif not self.is_finished:
        #     self.ring_light.set_mode(ring_light.MODE_OFF)
        # elif self.is_writing_rfid:
        #     # self.ring_light.set_mode(ring_light.MODE_CONNECTED)
        #     pass
        # elif self.current_mode == ghost_machine_base.MODE_WAITING_FOR_TRASH:
        #     self.ring_light.set_mode(ring_light.MODE_WAITING)
        # elif self.current_mode == ghost_machine_base.MODE_HAS_TRASH:
        #     self.ring_light.set_mode(ring_light.MODE_CONNECTED)
        print("Updated light pattern to: ", self.ring_light.current_mode)

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
            self.reset_time = 0
            self._update_state(EVENT_WIN_GAME)
        else:
            self.reset_time = time.time() + GAME_TIMEOUT_S
            self._update_state(EVENT_BUTTON_PRESSED)

    def _update_house_lights(self):
        if self.current_mode == ghost_machine_base.MODE_FINISHED:
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