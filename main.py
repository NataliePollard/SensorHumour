import asyncio

from figurine_sensor import FigurineSensor
from game_sensor import GameSensor

async def main():
    # artifact = FigurineSensor()
    artifact = GameSensor()
    await artifact.start()
    asyncio.get_event_loop().run_forever()


asyncio.run(main())
