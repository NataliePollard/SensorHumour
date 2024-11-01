import asyncio
import canopy
import fern

from fps import FPS


ArtifactBlueCheesePattern = "CTP-eyJpZCI6ImQ1YWM1MzM4LTkzYTgtNGQ0NS1hZjk0LWVlMmZhY2ZjODE3ZSIsInZlcnNpb24iOjE1LCJuYW1lIjoiQXJ0aWZhY3QgLSBCbHVlIENoZWVzZSIsInBhbGV0dGVzIjp7IkNvbG9ycyI6W1swLFsxLDAsMF1dLFswLjE1LFsxLDAuNzIxNTY4NjI3NDUwOTgwNCwwXV0sWzAuMyxbMC45MDU4ODIzNTI5NDExNzY1LDEsMF1dLFswLjQ0LFswLjI3ODQzMTM3MjU0OTAxOTYsMSwwXV0sWzAuNixbMCwwLjg3MDU4ODIzNTI5NDExNzcsMV1dLFswLjc0LFswLjEyMTU2ODYyNzQ1MDk4MDM5LDAuMTgwMzkyMTU2ODYyNzQ1MSwxXV0sWzAuODgsWzAuNTIxNTY4NjI3NDUwOTgwNCwwLDFdXSxbMSxbMSwwLDAuNzQ5MDE5NjA3ODQzMTM3M11dXSwiUGFsZXR0ZTMiOltbMCxbMC4yODIzNTI5NDExNzY0NzA2LDAsMV1dLFswLjMyLFswLDAuMzE3NjQ3MDU4ODIzNTI5NCwxXV0sWzAuNjcsWzAuOCwwLjgzNTI5NDExNzY0NzA1ODksMV1dLFswLjk4LFswLjUyNTQ5MDE5NjA3ODQzMTQsMC4yNTA5ODAzOTIxNTY4NjI3NCwxXV1dLCJQYWxldHRlNCI6W1swLjExLFswLDAsMF1dLFswLjIxLFswLjE0OTAxOTYwNzg0MzEzNzI1LDAuMTc2NDcwNTg4MjM1Mjk0MTMsMV1dLFswLjMsWzAsMCwwXV1dLCJCcmlnaHRuZXNzIjpbWzAuMTQsWzAsMCwwXV0sWzAuMjUsWzEsMSwxXV0sWzAuMzksWzAsMCwwXV0sWzAuNTUsWzAsMCwwXV0sWzAuNjUsWzEsMSwxXV0sWzAuNzUsWzAsMCwwXV1dfSwicGFyYW1zIjp7IkNvbG9yIjowLjd9LCJsYXllcnMiOlt7ImVmZmVjdCI6InNvbGlkIiwib3BhY2l0eSI6MSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiQ29sb3JzIiwiaW5wdXRzIjp7Im9mZnNldCI6IkNvbG9yIn19LHsiZWZmZWN0Ijoic3BhcmtsZXMiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im11bHRpcGx5IiwicGFsZXR0ZSI6IkJyaWdodG5lc3MiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC40NSwib2Zmc2V0Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMTEsIm1pbiI6MCwibWF4IjowLjU0fX19fSx7ImVmZmVjdCI6InNwYXJrbGVzIiwib3BhY2l0eSI6MC45NiwiYmxlbmQiOiJub3JtYWwtbm9uYmxhY2siLCJwYWxldHRlIjoiUGFsZXR0ZTMiLCJpbnB1dHMiOnsiZGVuc2l0eSI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjE2LCJtaW4iOjAuMDYsIm1heCI6MC4zfX0sIm9mZnNldCI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjA5LCJtaW4iOjAuMTMsIm1heCI6MC42NH19fX0seyJlZmZlY3QiOiJncmFkaWVudCIsIm9wYWNpdHkiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC40OSwibWluIjowLCJtYXgiOjF9fSwiYmxlbmQiOiJub3JtYWwtbm9uYmxhY2siLCJwYWxldHRlIjoiUGFsZXR0ZTQiLCJpbnB1dHMiOnsib2Zmc2V0IjowLjQxLCJzaXplIjowLjQ4LCJyb3RhdGlvbiI6MH19XX0"
GhostHousePattern = "CTP-eyJrZXkiOiIiLCJ2ZXJzaW9uIjoxLCJuYW1lIjoiTmV3IFBhdHRlcm4iLCJwYWxldHRlcyI6eyJQYWxldHRlMSI6W1swLFswLjE0MTE3NjQ3MDU4ODIzNTMsMC4zNjg2Mjc0NTA5ODAzOTIyLDAuNzQxMTc2NDcwNTg4MjM1M11dLFsxLFswLjk2MDc4NDMxMzcyNTQ5MDIsMC4wODYyNzQ1MDk4MDM5MjE1NywwLjA4NjI3NDUwOTgwMzkyMTU3XV1dfSwicGFyYW1zIjp7fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJzb2xpZCIsIm9wYWNpdHkiOjEsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6IlBhbGV0dGUxIiwiaW5wdXRzIjp7Im9mZnNldCI6MC41fX0seyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjAuNjYsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6IlBhbGV0dGUxIiwiaW5wdXRzIjp7ImRlbnNpdHkiOnsidHlwZSI6InRyaWFuZ2xlIiwiaW5wdXRzIjp7InZhbHVlIjowLjQyLCJtaW4iOjAsIm1heCI6MX19LCJvZmZzZXQiOjAuNX19XX0"
PatternRainbow = "CTP-eyJrZXkiOiJyYWluYm93LXRlc3QiLCJ2ZXJzaW9uIjowLCJuYW1lIjoiUmFpbmJvdyBUZXN0IiwicGFsZXR0ZXMiOnsiQ29sb3JzIjpbWzAsWzEsMCwwXV0sWzAuMTUsWzEsMC43MTc2NDcwNTg4MjM1Mjk0LDBdXSxbMC4yOSxbMC45MDE5NjA3ODQzMTM3MjU1LDEsMF1dLFswLjQ0LFswLjI4MjM1Mjk0MTE3NjQ3MDYsMSwwXV0sWzAuNTksWzAsMC44NjY2NjY2NjY2NjY2NjY3LDFdXSxbMC43MyxbMC4wNjY2NjY2NjY2NjY2NjY2NywwLDFdXSxbMC44NixbMC41MTc2NDcwNTg4MjM1Mjk1LDAsMV1dLFswLjk4LFsxLDAsMC43NDkwMTk2MDc4NDMxMzczXV1dLCJPdmVybGF5IjpbWzAsWzAsMCwwXV0sWzEsWzAuNTY4NjI3NDUwOTgwMzkyMSwwLjU2ODYyNzQ1MDk4MDM5MjEsMC41Njg2Mjc0NTA5ODAzOTIxXV1dLCJDaGFzZXIgT3ZlcmxheSI6W1swLFsxLDEsMV1dLFsxLFsxLDEsMV1dXX0sInBhcmFtcyI6eyJDb2xvciI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjE4LCJtaW4iOjAsIm1heCI6MX19LCJUaW1lciI6MX0sImxheWVycyI6W3siZWZmZWN0Ijoic29saWQiLCJvcGFjaXR5Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuNCwibWluIjowLjE5LCJtYXgiOjF9fSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiQ29sb3JzIiwiaW5wdXRzIjp7Im9mZnNldCI6IkNvbG9yIn19LHsiZWZmZWN0Ijoic3BhcmtsZXMiLCJvcGFjaXR5IjowLjQ3LCJibGVuZCI6Im92ZXJsYXkiLCJwYWxldHRlIjoiT3ZlcmxheSIsImlucHV0cyI6eyJkZW5zaXR5Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMzMsIm1pbiI6MC4xNSwibWF4IjoxfX0sIm9mZnNldCI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjMyLCJtaW4iOjAuMjQsIm1heCI6MX19fX0seyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC41NSwibWluIjowLCJtYXgiOjF9fSwiYmxlbmQiOiJub3JtYWwtbm9uYmxhY2siLCJwYWxldHRlIjoiT3ZlcmxheSIsImlucHV0cyI6eyJkZW5zaXR5IjowLjE5LCJvZmZzZXQiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC4yNCwibWluIjowLjM0LCJtYXgiOjF9fX19LHsiZWZmZWN0IjoiY2hhc2VyIiwib3BhY2l0eSI6MSwiYmxlbmQiOiJtdWx0aXBseSIsInBhbGV0dGUiOiJDaGFzZXIgT3ZlcmxheSIsImlucHV0cyI6eyJvZmZzZXQiOiJUaW1lciIsInNpemUiOjF9fV19"
ArtifactConnectedPattern = "CTP-eyJpZCI6IjFhMjQ5MmUwLTY2ZGMtNGJmMi04ODY1LTYxNTIwMzNlZTk2ZSIsInZlcnNpb24iOjIsIm5hbWUiOiJBcnRpZmFjdCAtIENvbm5lY3RlZCBDb2xvcnMiLCJwYWxldHRlcyI6eyJDb2xvcnMiOltbMCxbMSwwLDBdXSxbMC4xNSxbMSwwLjcyLDBdXSxbMC4yNyxbMC45LDEsMF1dLFswLjQ0LFswLjI4LDEsMF1dLFswLjU5LFswLDAuODcsMV1dLFswLjczLFswLjA3LDAsMV1dLFswLjg2LFswLjUyLDAsMV1dLFsxLFsxLDAsMC43NV1dXSwiQnJpZ2h0bmVzcyI6W1swLjE0LFswLDAsMF1dLFswLjI1LFsxLDEsMV1dLFswLjM5LFswLDAsMF1dLFswLjU1LFswLDAsMF1dLFswLjY1LFsxLDEsMV1dLFswLjc1LFswLDAsMF1dXX0sInBhcmFtcyI6eyJDb2xvciI6MH0sImxheWVycyI6W3siZWZmZWN0Ijoic29saWQiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJDb2xvcnMiLCJpbnB1dHMiOnsib2Zmc2V0IjoiQ29sb3IifX0seyJlZmZlY3QiOiJjaGFzZXIiLCJvcGFjaXR5IjowLjYsImJsZW5kIjoibXVsdGlwbHkiLCJwYWxldHRlIjoiQnJpZ2h0bmVzcyIsImlucHV0cyI6eyJvZmZzZXQiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAuMTMsIm1heCI6MX19LCJzaXplIjowLjQ1fX0seyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjAuNywiYmxlbmQiOiJvdmVybGF5IiwicGFsZXR0ZSI6IkJyaWdodG5lc3MiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC42MSwib2Zmc2V0Ijp7InR5cGUiOiJ0cmlhbmdsZSIsImlucHV0cyI6eyJ2YWx1ZSI6MC4yOCwibWluIjowLCJtYXgiOjF9fX19XX0"

blue_cheese_pattern = canopy.Pattern(ArtifactBlueCheesePattern)
ghost_house_pattern = canopy.Pattern(GhostHousePattern)
rainbow_pattern = canopy.Pattern(PatternRainbow)
artifact_connected_pattern = canopy.Pattern(ArtifactConnectedPattern)

HIDDEN_ROOM_PIXELS = range(0, 27)
KITCHEN_PIXELS = range(27, 56)
STUDY_PIXELS = range(56, 83)
LIVING_ROOM_PIXELS = range(83, 133)
CONSERVATORY_PIXELS = range(133, 150)
BATHROOM_PIXELS = range(150, 165)
BEDROOM_PIXELS = range(165, 171)
ATTIC_PIXELS = range(171, 229)


COLOR_RED = 0.01
COLOR_ORANGE = 0.07
COLOR_YELLOW = 0.22
COLOR_GREEN = 0.47
COLOR_LIGHT_BLUE = 0.59
COLOR_BLUE = 0.72
COLOR_PURPLE = 0.88
COLOR_PINK = 1


class BlueCheese(object):
    light_pattern = blue_cheese_pattern

    # def __init__(
    #     self
    # ):

    async def start(self):
        print("Starting canopy")
        canopy.init([fern.LED1_DATA, fern.LED2_DATA], 450)
        asyncio.create_task(self._render_loop())
        self.light_pattern = ghost_house_pattern

    async def _render_loop(self):
        segment1 = canopy.Segment(0, 0, 50)
        segment2 = canopy.Segment(0, 50, 100)
        segment3 = canopy.Segment(0, 100, 150)
        segment4 = canopy.Segment(0, 150, 200)
        segment5 = canopy.Segment(0, 200, 250)
        f = FPS(verbose=True)
        params1 = canopy.Params()
        # params1["Color"] = float(COLOR_RED)
        params2 = canopy.Params()
        # params2["Color"] = float(COLOR_BLUE)
        params3 = canopy.Params()
        # params3["Color"] = float(COLOR_RED)
        params4 = canopy.Params()
        # params4["Color"] = float(COLOR_YELLOW)
        params5 = canopy.Params()
        # params5["Color"] = float(COLOR_PINK)
        while True:
            try:
                f.tick()
                # params["Color"] = float(0.70)
                canopy.clear()
                canopy.draw(
                    segment1, ghost_house_pattern, alpha=float(0.3), params=params1
                )
                canopy.draw(
                    segment2, ghost_house_pattern, alpha=float(0.3), params=params2
                )
                canopy.draw(
                    segment3, ghost_house_pattern, alpha=float(0.3), params=params3
                )
                canopy.draw(
                    segment4, ghost_house_pattern, alpha=float(0.3), params=params4
                )
                canopy.draw(
                    segment5, ghost_house_pattern, alpha=float(0.3), params=params5
                )

                canopy.render()
            except Exception as e:
                print("Error in render loop", e)

            await asyncio.sleep(0)
