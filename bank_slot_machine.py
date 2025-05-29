import asyncio
import json
import canopy
import fern
import time
import random

# from fps import FPS
from rat_mqtt import Mqtt
from rat_wifi import Wifi
from audio import Audio
from ghost_magnet import Magnet
from button import Button
import ring_light
from bank_slot_audio import BankSlotMachineAudio
from bank_bean_dispenser import BeanDispenser


MODE_INITIALIZING = -1
MODE_READY = 0
MODE_HAS_PAYMENT = 1
MODE_PLAYING = 2
MODE_WON = 3
MODE_LOST = 4

# Local Events
EVENT_FINISHED_BOOT = "finishedBoot"
EVENT_SENSOR_TRIGGERED = "sensorTriggered"
EVENT_TRIGGER_PLAY = "triggerPlay"
EVENT_PLAY_ENDED = "playEnded"
EVENT_GAME_RESET = "gameReset"

# Remote Events
EVENT_BANK_UPDATE = "bankUpdate"
EVENT_RESET_COMMAND = "reset"

PAYMENT_TIMEOUT_S = 60
WIN_TIMEOUT_S = 10
PLAY_TIMEOUT_S = 3

BUTTON_PLAY = 0
BUTTON_BEAN_SENSOR = 1


class BankSlotMachine(object):
    is_wifi_connected = False
    is_connected = False

    current_mode = MODE_INITIALIZING

    def __init__(
        self,
        name="bank_slot_machine",
        has_wifi=True,
    ):
        self.audio = Audio()
        self.slot_audio = BankSlotMachineAudio(self.audio)
        self.dispenser = BeanDispenser(pin=fern.D6)
        self.name = name
        self.has_wifi = has_wifi
        if has_wifi:
            self.mqtt = Mqtt(name, self._onMqttMessage)
            self.wifi = Wifi(hostname=self.name)
        self.num_leds = 100
        self.payment_timeout = 0
        self.win_timeout = 0   
        self.play_timeout = 0 
        self.wager = 0
        

    async def start(self):
        if self.has_wifi:
            self.wifi.start(self._on_wifi_connected)
        self.audio.start()
        self.dispenser.start()

        def get_button_callback(button_num):
            print("Button callback for ", button_num)

            def button(btn):
                print("Button inner callback for ", button_num)
                self.button_callback(button_num)
            return button

        self.buttons = [
            Button(fern.D5, get_button_callback(BUTTON_PLAY)),
            Button(fern.D8, get_button_callback(BUTTON_BEAN_SENSOR)),
        ]
        
        asyncio.create_task(self.buttons[BUTTON_PLAY].run())
        asyncio.create_task(self.buttons[BUTTON_BEAN_SENSOR].run())

        print("Starting canopy")
        canopy.init([fern.LED1_DATA, fern.LED2_DATA], self.num_leds)
        self.ring_light = ring_light.RingLight(audio=None)
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

        if button == BUTTON_BEAN_SENSOR:
            self._update_state(EVENT_SENSOR_TRIGGERED)
        elif button == BUTTON_PLAY:
            self._update_state(EVENT_TRIGGER_PLAY)

    def _update_state(self, event, should_broadcast=True):
        print("is wifi connected: ", self.is_wifi_connected)
        print("is connected: ", self.is_connected)

        if event == EVENT_FINISHED_BOOT:
            self.current_mode = MODE_READY
            self.slot_audio.play_ambient()
        elif event == EVENT_SENSOR_TRIGGERED:
            if self.current_mode in (MODE_READY, MODE_LOST, MODE_WON):
                self.current_mode = MODE_HAS_PAYMENT
                self.wager += 1
                self.payment_timeout = time.time() + PAYMENT_TIMEOUT_S
                self.play_timeout = 0
                self.win_timeout = 0
                self.slot_audio.play_payment()
        elif event == EVENT_TRIGGER_PLAY:
            self.current_mode = MODE_PLAYING
            self.payment_timeout = 0
            self.win_timeout = 0
            self.play_timeout = time.time() + PLAY_TIMEOUT_S
            self.slot_audio.play_playing()
        elif event == EVENT_PLAY_ENDED:
            if (random.random() < 0.33):
                self.current_mode = MODE_WON
                self.dispenser.dispense(random.randint(1, min((self.wager // 4) + 1, 4)))
                self.slot_audio.play_win()
            else:
                self.current_mode = MODE_LOST
                self.slot_audio.play_lose()
            self.wager = 0
            self.play_timeout = 0
            self.payment_timeout = 0
            self.win_timeout = time.time() + WIN_TIMEOUT_S
        elif event == EVENT_GAME_RESET:
            self.current_mode = MODE_READY
            self.payment_timeout = 0
            self.play_timeout = 0
            self.win_timeout = 0
        
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
        elif self.current_mode == MODE_HAS_PAYMENT:
            self.ring_light.set_mode(ring_light.MODE_CONNECTED)
        elif self.current_mode == MODE_PLAYING:
            self.ring_light.set_mode(ring_light.MODE_RUNNING)
        elif self.current_mode == MODE_WON:
            self.ring_light.set_mode(ring_light.MODE_FINISHED)
        elif self.current_mode == MODE_LOST:
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
                if self.payment_timeout > 0 and time.time() > self.payment_timeout:
                    self.payment_timeout = 0
                    self._update_state(EVENT_GAME_RESET)
                if self.play_timeout > 0 and time.time() > self.play_timeout:
                    self.play_timeout = 0
                    self._update_state(EVENT_PLAY_ENDED)
                if self.win_timeout > 0 and time.time() > self.win_timeout:
                    self.win_timeout = 0
                    self._update_state(EVENT_GAME_RESET)
            except Exception as e:
                print("Error in render loop", e)

            await asyncio.sleep(0.1)
