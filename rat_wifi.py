import asyncio
import network


default_ssid = "Goblins2.4"
default_password = "scamlikely"


class Wifi(object):
    is_connected = False

    def __init__(self, ssid=default_ssid, password=default_password):
        self.ssid = ssid
        self.password = password

    def start(self, on_wifi_connected):
        self.on_wifi_connected = on_wifi_connected
        asyncio.create_task(self.connection_loop())

    async def connection_loop(self):
        station = network.WLAN(network.STA_IF)
        station.active(True)
        # Continually try to connect to WiFi access point
        while True:
            if not station.isconnected():
                if self.is_connected:
                    self.is_connected = False
                    print("Connection lost. Trying again.")
                # Try to connect to WiFi access point
                print("Connecting...")
                try:
                    station.connect(self.ssid, self.password)
                except:
                    print("Failed to connect to WiFi")
                await asyncio.sleep(1)
            elif station.isconnected():
                if not self.is_connected:
                    self.is_connected = True
                    # Display connection details
                    print("Connected!")
                    print("My IP Address:", station.ifconfig()[0])
                    self.on_wifi_connected()
                await asyncio.sleep(1)
