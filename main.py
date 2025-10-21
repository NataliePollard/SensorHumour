import asyncio

# from ghost_writer import GhostMachine
from ghost_dollhouse_new import GhostDollhouse
from ghost_listening import GhostListeningMachine
from ghost_printer import GhostPrinter
from ghost_scale import GhostScale
from ghost_scanner_box import GhostScannerBox
# from ghost_tag_data import PRINTER, AUDIO, DOLLHOUSE, OTHER1, OTHER2, OTHER3, SCALE
from rat_bluecheese import BlueCheese
from bank_slot_machine import BankSlotMachine
from bank_vault import BankVaultDoor
from figurine_sensor import FigurineSensor

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
    # artifact = GhostListeningMachine()
    # artifact = GhostScale("scaleOne")
    # artifact = GhostScale("scaleTwo")
    # artifact = GhostPrinter()
    # artifact = GhostScannerBox("scanner1")
    # artifact = GhostScannerBox("scanner2")
    # artifact = GhostScannerBox("scanner3")

    # artifact = BlueCheese()

    # artifact = BankVaultDoor()
    # artifact = BankSlotMachine()
    artifact = FigurineSensor()
    await artifact.start()
    asyncio.get_event_loop().run_forever()


asyncio.run(main())
