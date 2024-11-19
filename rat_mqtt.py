from umqtt.simple import MQTTClient
import asyncio
import time
import machine


class Mqtt(object):
    is_connected = False
    next_ping = 0
    lost_connection_count = 0

    def __init__(
        self, name, on_message_callback, topic="mqtt/timemachine", server="10.0.1.208"
    ):
        self.on_message_callback = on_message_callback
        self.topic = topic
        self.client = MQTTClient(name, server)
        self.client.set_callback(self._on_message)

    async def _connect(self):
        print("MQTT - Connecting")
        while self.is_connected == False:
            try:
                self.client.connect()
                self.is_connected = True
                self.next_ping = time.time() + 45
            except:
                print("MQTT - Failed to connect, retrying")
                await asyncio.sleep(1)

    async def run(self, on_connected=None):
        await self._connect()
        self.client.subscribe(self.topic)
        print("MQTT - Connected")
        if on_connected:
            on_connected()
        while True:
            try:
                self.client.check_msg()
                self.lost_connection_count = 0
                if time.time() > self.next_ping:
                    # self.client.ping()
                    self.next_ping = time.time() + 60
            except:
                print("Lost connection to MQTT ")
                self.lost_connection_count += 1
                self.is_connected = False
                await asyncio.sleep(1)

                if self.lost_connection_count > 10:
                    machine.reset()
                await self._connect()
            await asyncio.sleep(0.3)

    def _on_message(self, topic, msg):
        print("MQTT - Message: ", (topic, msg))
        if self.on_message_callback:
            self.on_message_callback(topic, msg)

    def send_message(self, message):
        print("MQTT - Sending message: ", self.topic, message)
        self.client.publish("mqtt/timemachine", message)

    def close(self):
        self.client.disconnect()
