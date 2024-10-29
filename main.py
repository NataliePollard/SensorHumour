import asyncio

# from ghost_writer import GhostMachine
from ghost_dollhouse import GhostDollhouse
from ghost_tag_data import PRINTER, AUDIO, DOLLHOUSE, OTHER1, OTHER2, OTHER3, SCALE
from rat_bluecheese import BlueCheese

# MACHINE = DOLLHOUSE
# MACHINE = AUDIO
# MACHINE = DOLLHOUSE
# MACHINE = OTHER1
# MACHINE = OTHER2
# MACHINE = OTHER3
# MACHINE = SCALE


async def main():
    # if MACHINE == DOLLHOUSE:
        # artifact = GhostDollhouse()
    # artifact = GhostMachine(name=MACHINE)
    artifact = BlueCheese(name=DOLLHOUSE)
    await artifact.start()
    asyncio.get_event_loop().run_forever()


asyncio.run(main())
  