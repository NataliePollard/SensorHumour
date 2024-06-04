import asyncio

from rat_artifact import Artifact, connected_pattern, mushroom_pattern, city_pattern
from rat_artifact_city import CityArtifact
from rat_bluecheese import BlueCheese

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
ARTIFACT_BLUE_CHEESE = "artifact/blue_cheese"


# ARTIFACT = ARTIFACT_CITY
# ARTIFACT = ARTIFACT_TANK
# ARTIFACT = ARTIFACT_MUSHROOMS
# ARTIFACT = ARTIFACT_MOBILE
# ARTIFACT = ARTIFACT_MICROWAVE
# ARTIFACT = ARTIFACT_BUGS
# ARTIFACT = ARTIFACT_FISH
# ARTIFACT = ARTIFACT_VOLCANO
ARTIFACT = ARTIFACT_BLUE_CHEESE


async def main():
    # artifact = EnergyTank(ARTIFACT_NAME)
    if ARTIFACT == ARTIFACT_TANK:
        artifact = Artifact(ARTIFACT_TANK)
    elif ARTIFACT == ARTIFACT_MICROWAVE:
        artifact = Artifact(ARTIFACT_MICROWAVE)
    elif ARTIFACT == ARTIFACT_BUGS:
        artifact = Artifact(
            ARTIFACT_BUGS,
            second_light_pattern=connected_pattern,
            second_pattern_num_pixels=7,
        )
    elif ARTIFACT == ARTIFACT_FISH:
        artifact = Artifact(ARTIFACT_FISH)
    elif ARTIFACT == ARTIFACT_MUSHROOMS:
        artifact = Artifact(
            ARTIFACT_MUSHROOMS,
            second_light_pattern=mushroom_pattern,
            second_pattern_num_pixels=50,
        )
    elif ARTIFACT == ARTIFACT_VOLCANO:
        artifact = Artifact(ARTIFACT_VOLCANO)
    elif ARTIFACT == ARTIFACT_MOBILE:
        artifact = Artifact(ARTIFACT_MOBILE)
    elif ARTIFACT == ARTIFACT_CITY:
        artifact = CityArtifact(ARTIFACT_CITY, second_light_pattern=mushroom_pattern)
    elif ARTIFACT == ARTIFACT_BLUE_CHEESE:
        artifact = BlueCheese(ARTIFACT_BLUE_CHEESE)
    else:
        print("Invalid artifact")
        return

    await artifact.start()
    asyncio.get_event_loop().run_forever()


asyncio.run(main())
