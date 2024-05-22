import asyncio

from rat_artifact import Artifact
from rat_artifact_city import CityArtifact

# from rat_energytank import EnergyTank

ARTIFACT_ONE = "noodle/1"
ARTIFACT_TWO = "noodle/2"
ARTIFACT_THREE = "noodle/3"
ARTIFACT_FOUR = "noodle/4"
ARTIFACT_FIVE = "noodle/5"
ARTIFACT_SIX = "noodle/6"
ARTIFACT_SEVEN = "noodle/7"
ARTIFACT_CITY = "noodle/city"
ARTIFACT_NINE = "noodle/9"


ARTIFACT = ARTIFACT_ONE
# ARTIFACT = ARTIFACT_TWO
# ARTIFACT = ARTIFACT_THREE
# ARTIFACT = ARTIFACT_FOUR
# ARTIFACT = ARTIFACT_FIVE
# ARTIFACT = ARTIFACT_SIX
# ARTIFACT = ARTIFACT_SEVEN
# ARTIFACT = ARTIFACT_CITY
# ARTIFACT = ARTIFACT_NINE


async def main():
    # artifact = EnergyTank(ARTIFACT_NAME)
    if ARTIFACT == ARTIFACT_ONE:
        artifact = Artifact(ARTIFACT_ONE, magnet_pin=2, relay_pin=3)
    elif ARTIFACT == ARTIFACT_TWO:
        artifact = Artifact(ARTIFACT_TWO)
    elif ARTIFACT == ARTIFACT_THREE:
        artifact = Artifact(ARTIFACT_THREE)
    elif ARTIFACT == ARTIFACT_FOUR:
        artifact = Artifact(ARTIFACT_FOUR)
    elif ARTIFACT == ARTIFACT_FIVE:
        artifact = Artifact(ARTIFACT_FIVE)
    elif ARTIFACT == ARTIFACT_SIX:
        artifact = Artifact(ARTIFACT_SIX)
    elif ARTIFACT == ARTIFACT_SEVEN:
        artifact = Artifact(ARTIFACT_SEVEN)
    elif ARTIFACT == ARTIFACT_CITY:
        artifact = CityArtifact(ARTIFACT_CITY)
    elif ARTIFACT == ARTIFACT_NINE:
        artifact = Artifact(ARTIFACT_NINE)
    else:
        print("Invalid artifact")
        return

    await artifact.start()
    asyncio.get_event_loop().run_forever()


asyncio.run(main())
