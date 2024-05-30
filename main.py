import asyncio

from rat_artifact import Artifact
from rat_artifact_city import CityArtifact

# from rat_energytank import EnergyTank

# ARTIFACT_ONE = "noodle/1"
# ARTIFACT_TWO = "noodle/2"
# ARTIFACT_THREE = "noodle/3"
# ARTIFACT_FOUR = "noodle/4"
# ARTIFACT_FIVE = "noodle/5"
# ARTIFACT_SIX = "noodle/6"
# ARTIFACT_SEVEN = "noodle/7"
# ARTIFACT_CITY = "noodle/city"
# ARTIFACT_NINE = "noodle/9"

ARTIFACT_CITY = "artifact/city"
ARTIFACT_TANK = "artifact/tank"
ARTIFACT_MICROWAVE = "artifact/microwave"
ARTIFACT_BUGS = "artifact/bugs"
ARTIFACT_FISH = "artifact/fish"
ARTIFACT_MUSHROOMS = "artifact/mushrooms"
ARTIFACT_VOLCANO = "artifact/volcano"
ARTIFACT_MOBILE = "artifact/mobile"


ARTIFACT = ARTIFACT_CITY
# ARTIFACT = ARTIFACT_TANK
# ARTIFACT = ARTIFACT_MUSHROOMS
# ARTIFACT = ARTIFACT_MOBILE
# ARTIFACT = ARTIFACT_MICROWAVE
# ARTIFACT = ARTIFACT_BUGS
# ARTIFACT = ARTIFACT_FISH
# ARTIFACT = ARTIFACT_VOLCANO


async def main():
    # artifact = EnergyTank(ARTIFACT_NAME)
    if ARTIFACT == ARTIFACT_TANK:
        artifact = Artifact(ARTIFACT_TANK)
    elif ARTIFACT == ARTIFACT_MICROWAVE:
        artifact = Artifact(ARTIFACT_MICROWAVE)
    elif ARTIFACT == ARTIFACT_BUGS:
        artifact = Artifact(ARTIFACT_BUGS)
    elif ARTIFACT == ARTIFACT_FISH:
        artifact = Artifact(ARTIFACT_FISH)
    elif ARTIFACT == ARTIFACT_MUSHROOMS:
        artifact = Artifact(ARTIFACT_MUSHROOMS)
    elif ARTIFACT == ARTIFACT_VOLCANO:
        artifact = Artifact(ARTIFACT_VOLCANO)
    elif ARTIFACT == ARTIFACT_MOBILE:
        artifact = Artifact(ARTIFACT_MOBILE)
    elif ARTIFACT == ARTIFACT_CITY:
        artifact = CityArtifact(ARTIFACT_CITY)
    # elif ARTIFACT == ARTIFACT_NINE:
    #     artifact = Artifact(ARTIFACT_NINE)
    else:
        print("Invalid artifact")
        return

    await artifact.start()
    asyncio.get_event_loop().run_forever()


asyncio.run(main())
