import asyncio
import json
import canopy
import fern
import time

# from fps import FPS
from rat_mqtt import Mqtt
from rat_wifi import Wifi
from audio import Audio
from ghost_magnet import Magnet
from button import Button
import ring_light
from bank_vault_audio import VaultDoorAudio


MODE_INITIALIZING = -1
MODE_READY = 0
MODE_PARTIAL = 1
MODE_OPEN = 2
MODE_FOUNDER = 3

# Local Events
EVENT_FINISHED_BOOT = "finishedBoot"
EVENT_SENSOR_TRIGGERED = "sensorTriggered"
EVENT_DOOR_OPEN = "doorOpen"
EVENT_DOOR_CLOSE = "doorClose"
EVENT_DOOR_EXIT = "doorExit"
EVENT_UPDATE_POWER = "updatePower"
EVENT_FOUNDER = "founder"
EVENT_MOTIVATION = "motivation"
EVENT_DIAL_LOCK = "dialLock"

# Remote Events
EVENT_BANK_UPDATE = "bankUpdate"
EVENT_RESET_COMMAND = "reset"

BUTTON_ZERO = 0
BUTTON_ONE = 1
BUTTON_TWO = 2
BUTTON_DIAL_LOCK = 3
BUTTON_EXIT = 4
BUTTON_MOTIVATION = 5

DOOR_TIMEOUT_S = 10
DIAL_LOCK_TIME_S = 1


class BankVaultDoor(object):
    is_wifi_connected = False
    is_connected = False

    current_mode = MODE_INITIALIZING

    def __init__(
        self,
        name="bank_vault_door",
        has_wifi=True,
    ):
        self.audio = Audio()
        self.vault_audio = VaultDoorAudio(self.audio)
        self.name = name
        self.has_wifi = has_wifi
        if has_wifi:
            self.mqtt = Mqtt(name, self._onMqttMessage)
            self.wifi = Wifi(hostname=self.name)
        self.num_leds = 100
        self.magnet = Magnet(pin=fern.D5)
        self.state = [False, False, False]
        self.magnet_open_time = 0
        self.dial_lock_time = 0
        

    async def start(self):
        if self.has_wifi:
            self.wifi.start(self._on_wifi_connected)
        self.audio.start()

        def get_button_callback(button_num):
            print("Button callback for ", button_num)

            def button(btn):
                print("Button inner callback for ", button_num)
                self.button_callback(button_num)
            return button

        self.buttons = [
            Button(fern.D3, get_button_callback(BUTTON_ZERO), wait_time_ms=1),
            Button(fern.D2, get_button_callback(BUTTON_ONE), wait_time_ms=1),
            Button(fern.D4, get_button_callback(BUTTON_TWO), wait_time_ms=1),
            Button(fern.D1, get_button_callback(BUTTON_DIAL_LOCK), pull_up=False),
            Button(fern.D6, get_button_callback(BUTTON_EXIT)),
            Button(fern.D7, get_button_callback(BUTTON_MOTIVATION)),
        ]
        
        asyncio.create_task(self.buttons[BUTTON_ZERO].run())
        asyncio.create_task(self.buttons[BUTTON_ONE].run())
        asyncio.create_task(self.buttons[BUTTON_TWO].run())
        asyncio.create_task(self.buttons[BUTTON_EXIT].run())
        asyncio.create_task(self.buttons[BUTTON_DIAL_LOCK].run())
        asyncio.create_task(self.buttons[BUTTON_MOTIVATION].run())

        print("Starting canopy")
        canopy.init([fern.LED1_DATA, fern.LED2_DATA], self.num_leds)
        self.ring_light = ring_light.RingLight()
        asyncio.create_task(self._render_loop())

    def _handle_mqtt_event(self, event, data):
        print("Handling mqtt event: ", event)
        if event == EVENT_RESET_COMMAND:
            self._update_state(EVENT_RESET_COMMAND, should_broadcast=False)
        elif event == EVENT_BANK_UPDATE:
            self._update_state(EVENT_BANK_UPDATE, should_broadcast=False)

    def _onMqttMessage(self, topic, msg):
        print((topic, msg))
        try:
            events = json.loads(msg)
            if type(events) not in (tuple, list):
                events = [events]
            for data in events:
                if (data.get("event") == EVENT_BANK_UPDATE and data.get("id") == self.name):
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

    def button_callback(self, button):
        print("Button Pressed: ", button)

        if button == BUTTON_EXIT:
            self._update_state(EVENT_DOOR_EXIT)
        elif button == BUTTON_DIAL_LOCK:
            self._update_state(EVENT_DIAL_LOCK)
        elif button == BUTTON_MOTIVATION:
            self._update_state(EVENT_MOTIVATION)
        else:
            if button == BUTTON_ZERO:
                self.state = [True, False, False]
            elif button == BUTTON_ONE:
                self.state[1] = True
                self.state[2] = False
            elif button == BUTTON_TWO:
                self.state[2] = True

            if button == BUTTON_TWO and self.state[0] and self.state[1] and self.state[2]:
                self._update_state(EVENT_DOOR_OPEN)

            print("New State: ", self.state)

    def _update_state(self, event, should_broadcast=True):
        print("is wifi connected: ", self.is_wifi_connected)
        print("is connected: ", self.is_connected)

        if event == EVENT_FINISHED_BOOT:
            self.current_mode = MODE_READY
            self.vault_audio.play_ambient()
            self.magnet.close()
            print("Vault Door is ready")
        elif event == EVENT_SENSOR_TRIGGERED:
            if self.current_mode in (MODE_READY, MODE_PARTIAL):
                self.current_mode = MODE_PARTIAL
                print("Vault Door is partially open", self.state)
            
        elif event == EVENT_DOOR_OPEN or event == EVENT_FOUNDER or event == EVENT_DOOR_EXIT:
            self.current_mode = MODE_OPEN
            self.magnet_open_time = time.time() + DOOR_TIMEOUT_S
            self.magnet.open()
            if event != EVENT_DOOR_EXIT:
                self.state = [False, False, False]
                print("Vault door open, resetting state")
            if event == EVENT_DOOR_OPEN:
                self.vault_audio.play_open()
                print("Vault Door is open")
            elif event == EVENT_FOUNDER and self.current_mode:
                self.vault_audio.play_founder()
                self.current_mode = MODE_FOUNDER
                print("Vault combo entered, founder mode activated")
            else:
                print("Exiting Vault")
        elif event == EVENT_DOOR_CLOSE:
            self.current_mode = MODE_READY
            self.magnet_open_time = 0
            self.magnet.close()
            self.reset_time = -1
            print("Vault Door closing")
        elif event == EVENT_MOTIVATION and self.current_mode in (MODE_READY, MODE_PARTIAL):
            self.vault_audio.play_motivation()
            self.state = [False, False, False]
        elif event == EVENT_DIAL_LOCK and self.dial_lock_time <= 0:
            print("Dial lock solved, waiting...")
            self.dial_lock_time = time.time() + DIAL_LOCK_TIME_S
        
        print("updated mode: ", self.current_mode, event)
        self._update_ring_light_pattern()

        if event and should_broadcast and self.has_wifi and self.mqtt.is_connected:
            self.mqtt.send_message(
                json.dumps(
                    {
                        "event": event,
                        "reader": self.name,
                    }
                )
            )

    def _update_ring_light_pattern(self):
        if self.current_mode == MODE_INITIALIZING:
            self.ring_light.set_mode(ring_light.MODE_INITIALIZING)
        elif self.current_mode == MODE_READY:
            self.ring_light.set_mode(ring_light.MODE_WAITING)
        elif self.current_mode == MODE_PARTIAL:
            self.ring_light.set_mode(ring_light.MODE_CONNECTED)
        elif self.current_mode == MODE_OPEN:
            self.ring_light.set_mode(ring_light.MODE_INVALID)
        elif self.current_mode == MODE_FOUNDER:
            self.ring_light.set_mode(ring_light.MODE_INVALID)
        print("Updated light pattern to: ", self.ring_light.current_mode)


    async def _render_loop(self):
        # f = FPS(verbose=True)
        while True:
            try:
                # f.tick()
                canopy.clear()
                self.ring_light.draw()
                canopy.render()
                if self.magnet_open_time > 0 and time.time() > self.magnet_open_time:
                    self.magnet_open_time = 0
                    self._update_state(EVENT_DOOR_CLOSE)
                if self.dial_lock_time > 0 and time.time() > self.dial_lock_time:
                    self.dial_lock_time = 0
                    if (self.buttons[BUTTON_DIAL_LOCK].is_pressed()):
                        self._update_state(EVENT_FOUNDER)
            except Exception as e:
                print("Error in render loop", e)

            await asyncio.sleep(0.1)
