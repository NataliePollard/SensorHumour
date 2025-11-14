"""
NFC Tag Detection Diagnostic Tool

Use this to scan any RFID tag and see its UID.
Helps identify which tags are compatible with the system.
"""
import asyncio
import binascii
from nfc import NfcWrapper


# Store detected tag UIDs
detected_tags = set()


async def on_tag_found(uid):
    """Called when a tag is detected"""
    print(f"\n{'='*60}")
    print(f"✓ TAG DETECTED!")
    print(f"{'='*60}")
    print(f"UID (hex string): {uid}")
    print(f"UID length: {len(uid)} characters")
    detected_tags.add(uid)
    print(f"\nTotal unique tags detected: {len(detected_tags)}")
    print(f"All UIDs found: {detected_tags}")
    print(f"{'='*60}\n")

    # Keep the callback alive
    while True:
        await asyncio.sleep(0.5)


def on_tag_lost():
    """Called when a tag is removed"""
    print("Tag removed")


async def main():
    print("\nNFC Tag Detection Diagnostic")
    print("="*60)
    print("Scan any RFID tag to see its UID")
    print("Press Ctrl+C to exit")
    print("="*60 + "\n")

    nfc = NfcWrapper(on_tag_found, on_tag_lost)
    await nfc.start()

    # Keep the program running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n\nExiting NFC test")
        print(f"Total unique tags detected: {len(detected_tags)}")
        if detected_tags:
            print("Tag UIDs found:")
            for tag in sorted(detected_tags):
                print(f"  - '{tag}'")


if __name__ == "__main__":
    asyncio.run(main())
