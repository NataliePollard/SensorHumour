import asyncio
import json
import canopy
import fern
import time

from fps import FPS
from nfc import NfcWrapper
from rat_mqtt import Mqtt
from rat_wifi import Wifi
from rat_relay import Relay
from ghost_magnet import Magnet
from rat_audio import Audio

from ghost_tag_data import (
    is_valid_tag_data_string,
    TagData,
    PRINTER,
    AUDIO,
    DOLLHOUSE,
    OTHER1,
    OTHER2,
    OTHER3,
    SCALE,
)


PatternInitializing = "CTP-eyJpZCI6ImRkMWVjY2MwLTE3ODYtNDhhYS05ZWE3LWNmMzAwODIwMTFhNCIsInZlcnNpb24iOjMsIm5hbWUiOiJXSWZpIERpc2Nvbm5lY3RlZCIsInBhbGV0dGVzIjp7IlBhbGV0dGUxIjpbWzAsWzEsMCwwXV0sWzAuOTksWzAsMCwwXV1dfSwicGFyYW1zIjp7IkNvbG9yIjoxfSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJjaGFzZXIiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQYWxldHRlMSIsImlucHV0cyI6eyJvZmZzZXQiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC40OCwibWluIjowLCJtYXgiOjF9fSwic2l6ZSI6MC4zMX19XX0"
PatternRainbow = "CTP-eyJpZCI6IjAzNWVlN2NjLWZiM2MtNDI0Ni1hOTM1LTdjNGQ3ZDYyMzEyMyIsInZlcnNpb24iOjEsIm5hbWUiOiJOZXcgUGF0dGVybiIsInBhbGV0dGVzIjp7IlBhbGV0dGUxIjpbWzAsWzEsMCwwXV0sWzAuMTksWzAuOTY0NzA1ODgyMzUyOTQxMiwxLDBdXSxbMC4zNixbMC4wNjI3NDUwOTgwMzkyMTU2OSwxLDAuMDUwOTgwMzkyMTU2ODYyNzQ0XV0sWzAuNTEsWzAsMSwwLjg3MDU4ODIzNTI5NDExNzddXSxbMC42NyxbMCwwLjA5MDE5NjA3ODQzMTM3MjU1LDFdXSxbMC44MixbMC40OCwwLjAxLDAuNDJdXSxbMC45OSxbMSwwLDBdXV19LCJwYXJhbXMiOnsicHJvZ3Jlc3MiOjB9LCJsYXllcnMiOlt7ImVmZmVjdCI6ImdyYWRpZW50Iiwib3BhY2l0eSI6InByb2dyZXNzIiwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUGFsZXR0ZTEiLCJpbnB1dHMiOnsib2Zmc2V0Ijp7InR5cGUiOiJyc2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjQxLCJtaW4iOjAsIm1heCI6MX19LCJzaXplIjowLjUsInJvdGF0aW9uIjowfX1dfQ"
ArtifactWaitingPattern = "CTP-eyJpZCI6IjY1YmNiOTNmLTE5MTktNGFiNi1iZWQ4LWVmOGQyZmRjN2Q1OSIsInZlcnNpb24iOjIsIm5hbWUiOiJBcnRpZmFjdCAtIFJlYWR5IiwicGFsZXR0ZXMiOnsiQ29sb3JzIjpbWzAsWzEsMCwwXV0sWzAuMTUsWzEsMC43MTc2NDcwNTg4MjM1Mjk0LDBdXSxbMC4yOSxbMC45MDE5NjA3ODQzMTM3MjU1LDEsMF1dLFswLjQ0LFswLjI4MjM1Mjk0MTE3NjQ3MDYsMSwwXV0sWzAuNTksWzAsMC44NjY2NjY2NjY2NjY2NjY3LDFdXSxbMC43MyxbMC4wNjY2NjY2NjY2NjY2NjY2NywwLDFdXSxbMC44NixbMC41MTc2NDcwNTg4MjM1Mjk1LDAsMV1dLFswLjk4LFsxLDAsMC43NDkwMTk2MDc4NDMxMzczXV1dLCJPdmVybGF5IjpbWzAsWzAsMCwwXV0sWzEsWzAuNTY4NjI3NDUwOTgwMzkyMSwwLjU2ODYyNzQ1MDk4MDM5MjEsMC41Njg2Mjc0NTA5ODAzOTIxXV1dLCJDaGFzZXIgT3ZlcmxheSI6W1swLFsxLDEsMV1dLFsxLFsxLDEsMV1dXX0sInBhcmFtcyI6eyJDb2xvciI6MC41OSwiVGltZXIiOjF9LCJsYXllcnMiOlt7ImVmZmVjdCI6InNvbGlkIiwib3BhY2l0eSI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjU3LCJtaW4iOjAsIm1heCI6MC44Mn19LCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJDb2xvcnMiLCJpbnB1dHMiOnsib2Zmc2V0IjoiQ29sb3IifX0seyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjAuNDcsImJsZW5kIjoib3ZlcmxheSIsInBhbGV0dGUiOiJPdmVybGF5IiwiaW5wdXRzIjp7ImRlbnNpdHkiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC4zMywibWluIjowLjE1LCJtYXgiOjAuNjl9fSwib2Zmc2V0Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMzIsIm1pbiI6MCwibWF4IjoxfX19fSx7ImVmZmVjdCI6InNwYXJrbGVzIiwib3BhY2l0eSI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjU1LCJtaW4iOjAsIm1heCI6MC42N319LCJibGVuZCI6Im5vcm1hbC1ub25ibGFjayIsInBhbGV0dGUiOiJPdmVybGF5IiwiaW5wdXRzIjp7ImRlbnNpdHkiOjAuMTksIm9mZnNldCI6eyJ0eXBlIjoic2luIiwiaW5wdXRzIjp7InZhbHVlIjowLjI0LCJtaW4iOjAsIm1heCI6MX19fX0seyJlZmZlY3QiOiJjaGFzZXIiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im11bHRpcGx5IiwicGFsZXR0ZSI6IkNoYXNlciBPdmVybGF5IiwiaW5wdXRzIjp7Im9mZnNldCI6IlRpbWVyIiwic2l6ZSI6MX19XX0"
# ArtifactConnectedPatternOld = "CTP-eyJpZCI6ImQyM2NlN2I4LTRhNjktNDYzMS05ODk1LTU2YzQ2ZTIzNWEyZiIsInZlcnNpb24iOjMsIm5hbWUiOiJBcnRpZmFjdCAtIENvbm5lY3RlZCIsInBhbGV0dGVzIjp7IlBhbGV0dGUxIjpbWzAuMixbMCwwLDBdXSxbMC4yOSxbMC40LDEsMF1dLFswLjM4LFswLDAsMF1dLFswLjYxLFswLDAsMF1dLFswLjcyLFswLjkzMzMzMzMzMzMzMzMzMzMsMSwwXV0sWzAuODMsWzAsMCwwXV1dLCJQYWxldHRlMiI6W1swLjEzLFswLDAsMF1dLFswLjI0LFswLDEsMC44NV1dLFswLjMyLFswLDAsMF1dLFswLjY3LFswLDAsMF1dLFswLjc3LFswLDEsMC44M11dLFswLjg3LFswLDAsMF1dXX0sInBhcmFtcyI6e30sImxheWVycyI6W3siZWZmZWN0IjoiZ3JhZGllbnQiLCJvcGFjaXR5IjowLjIsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6IlBhbGV0dGUxIiwiaW5wdXRzIjp7Im9mZnNldCI6eyJ0eXBlIjoic2F3IiwiaW5wdXRzIjp7InZhbHVlIjowLjUsIm1pbiI6MCwibWF4IjoxfX0sInNpemUiOjAuNjMsInJvdGF0aW9uIjowLjI1fX0seyJlZmZlY3QiOiJwbGFzbWEiLCJvcGFjaXR5IjowLjA2LCJibGVuZCI6InNjcmVlbiIsInBhbGV0dGUiOiJQYWxldHRlMiIsImlucHV0cyI6eyJkZW5zaXR5Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMTUsIm1pbiI6MCwibWF4IjoxfX0sIm9mZnNldCI6MX19XX0"
ArtifactConnectedPattern = "CTP-eyJpZCI6IjFhMjQ5MmUwLTY2ZGMtNGJmMi04ODY1LTYxNTIwMzNlZTk2ZSIsInZlcnNpb24iOjIsIm5hbWUiOiJBcnRpZmFjdCAtIENvbm5lY3RlZCBDb2xvcnMiLCJwYWxldHRlcyI6eyJDb2xvcnMiOltbMCxbMSwwLDBdXSxbMC4xNSxbMSwwLjcyLDBdXSxbMC4yNyxbMC45LDEsMF1dLFswLjQ0LFswLjI4LDEsMF1dLFswLjU5LFswLDAuODcsMV1dLFswLjczLFswLjA3LDAsMV1dLFswLjg2LFswLjUyLDAsMV1dLFsxLFsxLDAsMC43NV1dXSwiQnJpZ2h0bmVzcyI6W1swLjE0LFswLDAsMF1dLFswLjI1LFsxLDEsMV1dLFswLjM5LFswLDAsMF1dLFswLjU1LFswLDAsMF1dLFswLjY1LFsxLDEsMV1dLFswLjc1LFswLDAsMF1dXX0sInBhcmFtcyI6eyJDb2xvciI6MH0sImxheWVycyI6W3siZWZmZWN0Ijoic29saWQiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJDb2xvcnMiLCJpbnB1dHMiOnsib2Zmc2V0IjoiQ29sb3IifX0seyJlZmZlY3QiOiJjaGFzZXIiLCJvcGFjaXR5IjowLjYsImJsZW5kIjoibXVsdGlwbHkiLCJwYWxldHRlIjoiQnJpZ2h0bmVzcyIsImlucHV0cyI6eyJvZmZzZXQiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAuMTMsIm1heCI6MX19LCJzaXplIjowLjQ1fX0seyJlZmZlY3QiOiJzcGFya2xlcyIsIm9wYWNpdHkiOjAuNywiYmxlbmQiOiJvdmVybGF5IiwicGFsZXR0ZSI6IkJyaWdodG5lc3MiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC42MSwib2Zmc2V0Ijp7InR5cGUiOiJ0cmlhbmdsZSIsImlucHV0cyI6eyJ2YWx1ZSI6MC4yOCwibWluIjowLCJtYXgiOjF9fX19XX0"
ArtifactIncorrectPattern = "CTP-eyJpZCI6IjdkYjZiOGM3LTJkZjYtNDAzNC1iZjA1LTk3MTAxZDI3N2FhZiIsInZlcnNpb24iOjEzLCJuYW1lIjoiQXJ0aWZhY3QgSW5jb3JyZWN0IiwicGFsZXR0ZXMiOnsiUGFsZXR0ZTEiOltbMC40MSxbMSwwLDBdXV19LCJwYXJhbXMiOnsiQ29sb3IiOjF9LCJsYXllcnMiOlt7ImVmZmVjdCI6ImNoYXNlciIsIm9wYWNpdHkiOnsidHlwZSI6InNxdWFyZSIsImlucHV0cyI6eyJ2YWx1ZSI6MC42OSwibWluIjowLCJtYXgiOjF9fSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUGFsZXR0ZTEiLCJpbnB1dHMiOnsib2Zmc2V0IjoxLCJzaXplIjoxfX1dfQ"
ArtifactOffPattern = "CTP-eyJpZCI6Ijk2NTRmMDA4LWNlMjUtNDAwNS04MWE0LTc0NzY5MjJlOWNmZSIsInZlcnNpb24iOjYsIm5hbWUiOiJBcnRpZmFjdCAtIE9mZiIsInBhbGV0dGVzIjp7IkNvbG9ycyI6W1swLjAyLFswLjYxOTYwNzg0MzEzNzI1NDksMC4zODgyMzUyOTQxMTc2NDcwNywwLjA4NjI3NDUwOTgwMzkyMTU3XV0sWzAuMTQsWzAuNzQxMTc2NDcwNTg4MjM1MywwLjc0OTAxOTYwNzg0MzEzNzMsMC4zMDU4ODIzNTI5NDExNzY1XV0sWzAuMjksWzAuNTA1ODgyMzUyOTQxMTc2NCwwLjgxOTYwNzg0MzEzNzI1NDksMC4yMTE3NjQ3MDU4ODIzNTI5NF1dLFswLjQzLFswLjMyOTQxMTc2NDcwNTg4MjM1LDAuODcwNTg4MjM1Mjk0MTE3NywwLjEyMTU2ODYyNzQ1MDk4MDM5XV0sWzAuNTksWzAuMDYyNzQ1MDk4MDM5MjE1NjksMC44NzA1ODgyMzUyOTQxMTc3LDAuNjU0OTAxOTYwNzg0MzEzN11dLFswLjc0LFswLjIxNTY4NjI3NDUwOTgwMzkzLDAuNTI5NDExNzY0NzA1ODgyNCwwLjcwMTk2MDc4NDMxMzcyNTRdXSxbMC44NyxbMC4wMTk2MDc4NDMxMzcyNTQ5LDAuNTI5NDExNzY0NzA1ODgyNCwwLjI0MzEzNzI1NDkwMTk2MDc4XV0sWzAuOTksWzAuNTEzNzI1NDkwMTk2MDc4NCwwLjY1ODgyMzUyOTQxMTc2NDcsMC4xNDUwOTgwMzkyMTU2ODYzXV1dLCJCcmlnaHRuZXNzIjpbWzAuMTQsWzAsMCwwXV0sWzAuMjUsWzEsMSwxXV0sWzAuMzksWzAsMCwwXV0sWzAuNTUsWzAsMCwwXV0sWzAuNjUsWzEsMSwxXV0sWzAuNzUsWzAsMCwwXV1dfSwicGFyYW1zIjp7IkNvbG9yIjp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuNDEsIm1pbiI6MCwibWF4IjoxfX19LCJsYXllcnMiOlt7ImVmZmVjdCI6InNvbGlkIiwib3BhY2l0eSI6MSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiQ29sb3JzIiwiaW5wdXRzIjp7Im9mZnNldCI6IkNvbG9yIn19LHsiZWZmZWN0Ijoic3BhcmtsZXMiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im11bHRpcGx5IiwicGFsZXR0ZSI6IkJyaWdodG5lc3MiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC4yNCwib2Zmc2V0Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMTQsIm1pbiI6MCwibWF4IjoxfX19fV19"
ArtifactMushroomPattern = "CTP-eyJpZCI6ImYxMjZhNTgwLTc3ZDQtNDM1ZC04YTNjLWNlNWM0Yjc3ZjFiNyIsInZlcnNpb24iOjUsIm5hbWUiOiJBcnRpZmFjdCAtIE11c2hyb29tcyIsInBhbGV0dGVzIjp7IkNvbG9ycyI6W1swLFsxLDAsMF1dLFswLjE1LFsxLDAuNzIxNTY4NjI3NDUwOTgwNCwwXV0sWzAuMyxbMC45MDU4ODIzNTI5NDExNzY1LDEsMF1dLFswLjQ0LFswLjI3ODQzMTM3MjU0OTAxOTYsMSwwXV0sWzAuNixbMCwwLjg3MDU4ODIzNTI5NDExNzcsMV1dLFswLjc0LFswLjA3MDU4ODIzNTI5NDExNzY1LDAsMV1dLFswLjg4LFswLjUyMTU2ODYyNzQ1MDk4MDQsMCwxXV0sWzEsWzEsMCwwLjc0OTAxOTYwNzg0MzEzNzNdXV0sIkJyaWdodG5lc3MiOltbMC4xNCxbMCwwLDBdXSxbMC4yNSxbMSwxLDFdXSxbMC4zOSxbMCwwLDBdXSxbMC41NSxbMCwwLDBdXSxbMC42NSxbMSwxLDFdXSxbMC43NSxbMCwwLDBdXV0sIlBhbGV0dGUzIjpbWzAsWzAuMDExNzY0NzA1ODgyMzUyOTQxLDAuNzUyOTQxMTc2NDcwNTg4MiwxXV0sWzAuMzMsWzAuMDE1Njg2Mjc0NTA5ODAzOTIsMC44MzEzNzI1NDkwMTk2MDc5LDAuMzg0MzEzNzI1NDkwMTk2MV1dLFswLjY2LFswLjc4ODIzNTI5NDExNzY0NywwLjQxOTYwNzg0MzEzNzI1NDksMC44MTE3NjQ3MDU4ODIzNTI5XV0sWzAuOTcsWzAsMSwwLjg5ODAzOTIxNTY4NjI3NDVdXV19LCJwYXJhbXMiOnsiQ29sb3IiOjB9LCJsYXllcnMiOlt7ImVmZmVjdCI6InNvbGlkIiwib3BhY2l0eSI6MSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiQ29sb3JzIiwiaW5wdXRzIjp7Im9mZnNldCI6IkNvbG9yIn19LHsiZWZmZWN0Ijoic3BhcmtsZXMiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im11bHRpcGx5IiwicGFsZXR0ZSI6IkJyaWdodG5lc3MiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC43Niwib2Zmc2V0Ijp7InR5cGUiOiJ0cmlhbmdsZSIsImlucHV0cyI6eyJ2YWx1ZSI6MC4xMiwibWluIjowLCJtYXgiOjF9fX19LHsiZWZmZWN0Ijoic3BhcmtsZXMiLCJvcGFjaXR5IjowLjE3LCJibGVuZCI6Im5vcm1hbC1ub25ibGFjayIsInBhbGV0dGUiOiJQYWxldHRlMyIsImlucHV0cyI6eyJkZW5zaXR5Ijp7InR5cGUiOiJzaW4iLCJpbnB1dHMiOnsidmFsdWUiOjAuMDksIm1pbiI6MC4yNiwibWF4IjowLjY3fX0sIm9mZnNldCI6eyJ0eXBlIjoidHJpYW5nbGUiLCJpbnB1dHMiOnsidmFsdWUiOjAuMTYsIm1pbiI6MCwibWF4IjoxfX19fV19"
ArtifactCity = "CTP-eyJpZCI6IjMwZGE2ZjVmLTBkODYtNDFiMi05YzJmLWFmYjA4ZWRmNjdmMyIsInZlcnNpb24iOjIsIm5hbWUiOiJBcnRpZmFjdCAtIENpdHkiLCJwYWxldHRlcyI6eyJDb2xvcnMiOltbMCxbMSwwLDBdXSxbMC4xNSxbMSwwLjcyLDBdXSxbMC4yNyxbMC45LDEsMF1dLFswLjQ0LFswLjI4LDEsMF1dLFswLjU5LFswLDAuODcsMV1dLFswLjczLFswLjA3LDAsMV1dLFswLjg2LFswLjUyLDAsMV1dLFsxLFsxLDAsMC43NV1dXSwiQnJpZ2h0bmVzcyI6W1swLjE0LFswLDAsMF1dLFswLjI1LFsxLDEsMV1dLFswLjM5LFswLDAsMF1dLFswLjU1LFswLDAsMF1dLFswLjY1LFsxLDEsMV1dLFswLjc1LFswLDAsMF1dXX0sInBhcmFtcyI6eyJDb2xvciI6MC4zNH0sImxheWVycyI6W3siZWZmZWN0Ijoic29saWQiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJDb2xvcnMiLCJpbnB1dHMiOnsib2Zmc2V0IjoiQ29sb3IifX0seyJlZmZlY3QiOiJjaGFzZXIiLCJvcGFjaXR5IjowLjYsImJsZW5kIjoibXVsdGlwbHkiLCJwYWxldHRlIjoiQnJpZ2h0bmVzcyIsImlucHV0cyI6eyJvZmZzZXQiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC4yNiwibWluIjowLjEzLCJtYXgiOjF9fSwic2l6ZSI6MC40NX19LHsiZWZmZWN0Ijoic3BhcmtsZXMiLCJvcGFjaXR5IjowLjcsImJsZW5kIjoib3ZlcmxheSIsInBhbGV0dGUiOiJCcmlnaHRuZXNzIiwiaW5wdXRzIjp7ImRlbnNpdHkiOjAuNjEsIm9mZnNldCI6eyJ0eXBlIjoidHJpYW5nbGUiLCJpbnB1dHMiOnsidmFsdWUiOjAuMzIsIm1pbiI6MCwibWF4IjoxfX19fV19"

GhostHousePattern = "CTP-eyJrZXkiOiJnaG9zdC1ob3VzZS10ZXN0IiwidmVyc2lvbiI6MCwibmFtZSI6Ikdob3N0SG91c2VUZXN0IiwicGFsZXR0ZXMiOnsiUGFsZXR0ZTEiOltbMCxbMC4xNDExNzY0NzA1ODgyMzUzLDAuMzY4NjI3NDUwOTgwMzkyMiwwLjc0MTE3NjQ3MDU4ODIzNTNdXSxbMSxbMC45NjA3ODQzMTM3MjU0OTAyLDAuMDg2Mjc0NTA5ODAzOTIxNTcsMC4wODYyNzQ1MDk4MDM5MjE1N11dXX0sInBhcmFtcyI6e30sImxheWVycyI6W3siZWZmZWN0Ijoic29saWQiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQYWxldHRlMSIsImlucHV0cyI6eyJvZmZzZXQiOjAuNX19LHsiZWZmZWN0Ijoic3BhcmtsZXMiLCJvcGFjaXR5IjowLjY2LCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQYWxldHRlMSIsImlucHV0cyI6eyJkZW5zaXR5Ijp7InR5cGUiOiJ0cmlhbmdsZSIsImlucHV0cyI6eyJ2YWx1ZSI6MC40MiwibWluIjowLCJtYXgiOjF9fSwib2Zmc2V0IjowLjV9fV19"
ghost_house_pattern = canopy.Pattern(GhostHousePattern)
rainbow_pattern = canopy.Pattern(PatternRainbow)

MODE_INITIALIZING = 0
MODE_OFF = 1
MODE_WAITING = 2
MODE_CONNECTED = 3
MODE_INVALID = 4
MODE_WRITING = 5

# Local Events
EVENT_FINISHED_BOOT = "finishedBoot"
EVENT_CARD_FOUND = "cardFound"
EVENT_CARD_REMOVED = "cardRemoved"
EVENT_WRITE_NFC = "writeNfc"
EVENT_DONE_WRITING = "doneWriting"

# Remote Events
EVENT_GHOST_UPDATE = "ghostUpdate"
EVENT_RESET_COMMAND = "reset"
EVENT_OPEN_DOOR_COMMAND = "openDoor"
EVENT_WRITE_RFID_COMMAND = "writeRfid"


TEST_TAG = "5bc31366080104e0"

initializing_pattern = canopy.Pattern(PatternInitializing)
connected_pattern = canopy.Pattern(ArtifactConnectedPattern)
off_pattern = canopy.Pattern(ArtifactOffPattern)
incorrect_pattern = canopy.Pattern(ArtifactIncorrectPattern)
waiting_pattern = canopy.Pattern(ArtifactWaitingPattern)
second_light_pattern = canopy.Pattern(ArtifactMushroomPattern)
writing_pattern = canopy.Pattern(PatternRainbow)


class GhostMachine(object):
    color = 0
    local_start_time = -1
    start_time = -1
    end_time = -1
    current_tag = None
    current_mode = MODE_INITIALIZING
    is_connected = False
    is_invalid_connection = False
    is_wifi_connected = False
    light_pattern = initializing_pattern
    magnet = None

    room_states_map = {
        [HIDDEN_ROOM]: RoomState(
            name=HIDDEN_ROOM,
            start=HIDDEN_ROOM_PIXEL_START,
            length=HIDDEN_ROOM_PIXEL_LENGTH,
        ),
        [KITCHEN]: RoomState(
            name=KITCHEN, start=KITCHEN_PIXEL_START, length=KITCHEN_PIXEL_LENGTH
        ),
        [STUDY]: RoomState(
            name=STUDY, start=STUDY_PIXEL_START, length=STUDY_PIXEL_LENGTH
        ),
        [LIVING_ROOM]: RoomState(
            name=LIVING_ROOM,
            start=LIVING_ROOM_PIXEL_START,
            length=LIVING_ROOM_PIXEL_LENGTH,
        ),
        [CONSERVATORY]: RoomState(
            name=CONSERVATORY,
            start=CONSERVATORY_PIXEL_START,
            length=CONSERVATORY_PIXEL_LENGTH,
        ),
        [DINING_ROOM]: RoomState(
            name=DINING_ROOM,
            start=DINING_ROOM_PIXEL_START,
            length=DINING_ROOM_PIXEL_LENGTH,
        ),
        [LIBRARY]: RoomState(
            name=LIBRARY, start=LIBRARY_PIXEL_START, length=LIBRARY_PIXEL_LENGTH
        ),
        [ATTIC]: RoomState(
            name=ATTIC, start=ATTIC_PIXELS_START, length=ATTIC_PIXELS_LENGTH
        ),
    }

    def __init__(
        self,
        name="artifact/tank",
        magnet_pin=1,
        relay_pin=2,
    ):
        self.audio = Audio(name)
        self.name = name
        self.magnet_pin = magnet_pin
        self.relay_pin = relay_pin
        self.mqtt = Mqtt(name, self._onMqttMessage)
        self.wifi = Wifi(hostname=self.name)
        self.nfc = NfcWrapper(self._tag_found, self._tag_lost)
        self.relay = Relay(pin=self.relay_pin)
        self.magnet = Magnet(pin=self.magnet_pin)

    async def start(self):
        # self.wifi.start(self._on_wifi_connected)
        await self.nfc.start()
        self.audio.start()
        self.audio.play_ambient()

        print("Starting canopy")
        canopy.init([fern.LED1_DATA, fern.LED2_DATA], 250)
        asyncio.create_task(self._render_loop())

    def _onMqttMessage(self, topic, msg):
        print((topic, msg))
        try:
            events = json.loads(msg)
            if not type(events) in (tuple, list):
                events = [events]
            for data in events:
                if (
                    data.get("event") == EVENT_GHOST_UPDATE
                    and data.get("id") == self.name
                ):
                    command = data.get("command")
                    if command == EVENT_RESET_COMMAND:
                        self._update_state(EVENT_RESET_COMMAND, should_broadcast=False)
                    elif command == EVENT_OPEN_DOOR_COMMAND:
                        self._update_state(
                            EVENT_OPEN_DOOR_COMMAND, should_broadcast=False
                        )
                    elif command == EVENT_WRITE_RFID_COMMAND:
                        self._update_state(EVENT_WRITE_NFC, should_broadcast=False)
        except:
            print("Failed to parse mqtt message")

    def _on_wifi_connected(self):
        self.is_wifi_connected = True

        def on_mqtt_connected():
            self._update_state(EVENT_FINISHED_BOOT)

        try:
            asyncio.create_task(self.mqtt.run(on_mqtt_connected))
        except:
            print("Failed to start Mqtt")

    async def _tag_found(self, uid):
        self.current_tag = uid
        self.is_connected = True
        print("Reading NFC")
        nfcData = await self.nfc.read()
        print("NFC Data: ", nfcData)
        self.current_tag_data = TagData(nfcData)
        self._update_state(EVENT_CARD_FOUND)
        if not is_valid_tag_data_string(nfcData):
            self._update_state(EVENT_WRITE_NFC)

    def _tag_lost(self):
        self.is_connected = False
        self.is_invalid_connection = False
        self.current_tag = None
        self.disable_magnet = False
        self._update_state(EVENT_CARD_REMOVED)

    async def _write_nfc(self):
        if self.current_tag:
            print("Writing NFC")
            await self.nfc.write(self.current_tag_data.serialize())
            print("Done writing NFC")
            self._update_state(EVENT_DONE_WRITING)

    def _can_connect_tag(self):
        if self.name == DOLLHOUSE:
            return (
                self.current_mode == MODE_WAITING
                or self.current_mode == MODE_CONNECTED
                or self.current_mode == MODE_WRITING
            )
        else:
            True

    def _update_state(self, event, should_broadcast=True):
        print("is wifi connected: ", self.is_wifi_connected)
        print("is connected: ", self.is_connected)
        print("is invalid: ", self.is_invalid_connection)
        print("current tag: ", self.current_tag)

        def set_mode(mode):
            if self.current_mode == MODE_WRITING:
                self.previous_mode = mode
            else:
                self.current_mode = mode

        if event == EVENT_FINISHED_BOOT:
            set_mode(MODE_WAITING)
        elif event == EVENT_CARD_FOUND:
            if self._can_connect_tag():
                self.audio.play_correct()
                set_mode(MODE_CONNECTED)
            else:
                self.audio.play_incorrect()
                set_mode(MODE_INVALID)
        elif event == EVENT_CARD_REMOVED:
            self.audio.play_disconnect()
            set_mode(MODE_WAITING)
        elif event == EVENT_WRITE_NFC:
            if self.current_tag and self.current_mode is not MODE_WRITING:
                self.previous_mode = self.current_mode
                set_mode(MODE_WRITING)
                self._write_nfc()
        elif event == EVENT_DONE_WRITING:
            self.current_mode = self.previous_mode
        elif event == EVENT_RESET_COMMAND:
            set_mode(MODE_OFF)
        elif event == EVENT_OPEN_DOOR_COMMAND:
            set_mode(MODE_WAITING)

        print("updated mode: ", self.current_mode)
        self._update_light_pattern()

        if self.name == DOLLHOUSE:
            if (
                # self.current_mode == MODE_WAITING
                self.current_tag
                # and self._can_connect_tag()
            ):
                self.relay.on()
                self.magnet.open()
                print("Opening Door")
            else:
                self.relay.off()
                self.magnet.close()
                print("Closing Door")
        else:
            self.relay.off()
            self.magnet.close()

        if event and should_broadcast and self.mqtt.is_connected:
            self.mqtt.send_message(
                json.dumps(
                    {
                        "event": event,
                        "reader": self.name,
                        "card": self.current_tag,
                        "cardData": self.current_tag_data,
                        "connected": self.is_connected,
                        "invalid": self.is_invalid_connection,
                    }
                )
            )

    def _update_light_pattern(self):
        if self.current_mode == MODE_INITIALIZING:
            self.light_pattern = initializing_pattern
            self.second_light_pattern = self.second_light_pattern_to_use
        elif self.current_mode == MODE_INVALID:
            self.light_pattern = incorrect_pattern
            self.second_light_pattern = self.second_light_pattern_to_use
        elif self.current_mode == MODE_CONNECTED:
            self.light_pattern = connected_pattern
            self.second_light_pattern = self.second_light_pattern_to_use
        elif self.current_mode == MODE_WAITING:
            self.light_pattern = waiting_pattern
            self.second_light_pattern = self.second_light_pattern_to_use
        elif self.current_mode == MODE_WRITING:
            self.light_pattern = writing_pattern
            self.second_light_pattern = self.second_light_pattern_to_use
        elif self.current_mode == MODE_OFF:
            self.light_pattern = off_pattern
            self.second_light_pattern = self.second_light_pattern_to_use
        print("Updated light pattern to: ", self.light_pattern)

    async def _render_loop(self):
        ring_segment = canopy.Segment(0, 0, 16)
        ring_params = canopy.Params()
        f = FPS(verbose=True)
        while True:
            try:
                f.tick()
                canopy.clear()
                canopy.draw(
                    ring_segment,
                    self.light_pattern,
                    alpha=float(0.8),
                    params=ring_params,
                )
                for room in self.room_states_map:
                    room_state = self.room_states_map[room]
                    if room_state.light_pattern:
                        canopy.draw(
                            room_state.segment,
                            room_state.light_pattern,
                            alpha=float(0.8),
                            params=room_state.params,
                        )
                canopy.render()
            except Exception as e:
                print("Error in render loop", e)

            await asyncio.sleep(0)
