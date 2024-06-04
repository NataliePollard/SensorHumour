import asyncio
import canopy
import fern
import time

from fps import FPS


ArtifactBlueCheesePattern = "CTP-eyJpZCI6ImQ1YWM1MzM4LTkzYTgtNGQ0NS1hZjk0LWVlMmZhY2ZjODE3ZSIsInZlcnNpb24iOjE1LCJuYW1lIjoiQXJ0aWZhY3QgLSBCbHVlIENoZWVzZSIsInBhbGV0dGVzIjp7IkNvbG9ycyI6W1swLFsxLDAsMF1dLFswLjE1LFsxLDAuNzIxNTY4NjI3NDUwOTgwNCwwXV0sWzAuMyxbMC45MDU4ODIzNTI5NDExNzY1LDEsMF1dLFswLjQ0LFswLjI3ODQzMTM3MjU0OTAxOTYsMSwwXV0sWzAuNixbMCwwLjg3MDU4ODIzNTI5NDExNzcsMV1dLFswLjc0LFswLjEyMTU2ODYyNzQ1MDk4MDM5LDAuMTgwMzkyMTU2ODYyNzQ1MSwxXV0sWzAuODgsWzAuNTIxNTY4NjI3NDUwOTgwNCwwLDFdXSxbMSxbMSwwLDAuNzQ5MDE5NjA3ODQzMTM3M11dXSwiUGFsZXR0ZTMiOltbMCxbMC4yODIzNTI5NDExNzY0NzA2LDAsMV1dLFswLjMyLFswLDAuMzE3NjQ3MDU4ODIzNTI5NCwxXV0sWzAuNjcsWzAuOCwwLjgzNTI5NDExNzY0NzA1ODksMV1dLFswLjk4LFswLjUyNTQ5MDE5NjA3ODQzMTQsMC4yNTA5ODAzOTIxNTY4NjI3NCwxXV1dLCJQYWxldHRlNCI6W1swLjExLFswLDAsMF1dLFswLjIxLFswLjE0OTAxOTYwNzg0MzEzNzI1LDAuMTc2NDcwNTg4MjM1Mjk0MTMsMV1dLFswLjMsWzAsMCwwXV1dLCJCcmlnaHRuZXNzIjpbWzAuMTQsWzAsMCwwXV0sWzAuMjUsWzEsMSwxXV0sWzAuMzksWzAsMCwwXV0sWzAuNTUsWzAsMCwwXV0sWzAuNjUsWzEsMSwxXV0sWzAuNzUsWzAsMCwwXV1dfSwicGFyYW1zIjp7IkNvbG9yIjowLjd9LCJsYXllcnMiOlt7ImVmZmVjdCI6InNvbGlkIiwib3BhY2l0eSI6MSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiQ29sb3JzIiwiaW5wdXRzIjp7Im9mZnNldCI6IkNvbG9yIn19LHsiZWZmZWN0Ijoic3BhcmtsZXMiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im11bHRpcGx5IiwicGFsZXR0ZSI6IkJyaWdodG5lc3MiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC40NSwib2Zmc2V0Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMTEsIm1pbiI6MCwibWF4IjowLjU0fX19fSx7ImVmZmVjdCI6InNwYXJrbGVzIiwib3BhY2l0eSI6MC45NiwiYmxlbmQiOiJub3JtYWwtbm9uYmxhY2siLCJwYWxldHRlIjoiUGFsZXR0ZTMiLCJpbnB1dHMiOnsiZGVuc2l0eSI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjE2LCJtaW4iOjAuMDYsIm1heCI6MC4zfX0sIm9mZnNldCI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjA5LCJtaW4iOjAuMTMsIm1heCI6MC42NH19fX0seyJlZmZlY3QiOiJncmFkaWVudCIsIm9wYWNpdHkiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC40OSwibWluIjowLCJtYXgiOjF9fSwiYmxlbmQiOiJub3JtYWwtbm9uYmxhY2siLCJwYWxldHRlIjoiUGFsZXR0ZTQiLCJpbnB1dHMiOnsib2Zmc2V0IjowLjQxLCJzaXplIjowLjQ4LCJyb3RhdGlvbiI6MH19XX0"

blue_cheese_pattern = canopy.Pattern(ArtifactBlueCheesePattern)


class BlueCheese(object):
    light_pattern = blue_cheese_pattern

    def __init__(
        self,
        name,
    ):
        self.name = name

    async def start(self):
        print("Starting canopy")
        canopy.init([fern.LED1_DATA, fern.LED2_DATA], 100)
        asyncio.create_task(self._render_loop())
        self.light_pattern = blue_cheese_pattern

    async def _render_loop(self):
        segment = canopy.Segment(0, 0, 50)
        f = FPS(verbose=True)
        params = canopy.Params()
        while True:
            try:
                now = time.time()
                f.tick()
                params["Color"] = float(0.70)
                canopy.clear()
                canopy.draw(
                    segment, self.light_pattern, alpha=float(0.8), params=params
                )
                canopy.render()
            except Exception as e:
                print("Error in render loop", e)

            await asyncio.sleep(0)
