import canopy
PatternRainbow = "CTP-eyJrZXkiOiIiLCJ2ZXJzaW9uIjoxLCJuYW1lIjoiTmV3IFBhdHRlcm4iLCJwYWxldHRlcyI6eyJQYWxldHRlMSI6W1swLFsxLDAsMF1dLFswLjE0LFsxLDAuODI3NDUwOTgwMzkyMTU2OCwwLjE0MTE3NjQ3MDU4ODIzNTNdXSxbMC4zMSxbMC4wNTA5ODAzOTIxNTY4NjI3NDQsMSwwXV0sWzAuNTIsWzAsMC45NDExNzY0NzA1ODgyMzUzLDAuODYyNzQ1MDk4MDM5MjE1N11dLFswLjY4LFswLDAuMjgyMzUyOTQxMTc2NDcwNiwxXV0sWzAuOCxbMC40MTE3NjQ3MDU4ODIzNTI5LDAsMC44Nzg0MzEzNzI1NDkwMTk2XV0sWzAuODksWzEsMCwwLjgxNTY4NjI3NDUwOTgwMzldXSxbMSxbMSwwLDBdXV19LCJwYXJhbXMiOnt9LCJsYXllcnMiOlt7ImVmZmVjdCI6InNwYXJrbGVzIiwib3BhY2l0eSI6MSwiYmxlbmQiOiJub3JtYWwiLCJwYWxldHRlIjoiUGFsZXR0ZTEiLCJpbnB1dHMiOnsiZGVuc2l0eSI6MC41LCJvZmZzZXQiOnsidHlwZSI6InNpbiIsImlucHV0cyI6eyJ2YWx1ZSI6MC4zNiwibWluIjowLCJtYXgiOjF9fX19XX0"
GhostHousePattern = "CTP-eyJrZXkiOiJnaG9zdC1ob3VzZS10ZXN0IiwidmVyc2lvbiI6MCwibmFtZSI6Ikdob3N0SG91c2VUZXN0IiwicGFsZXR0ZXMiOnsiUGFsZXR0ZTEiOltbMCxbMC4xNDExNzY0NzA1ODgyMzUzLDAuMzY4NjI3NDUwOTgwMzkyMiwwLjc0MTE3NjQ3MDU4ODIzNTNdXSxbMSxbMC45NjA3ODQzMTM3MjU0OTAyLDAuMDg2Mjc0NTA5ODAzOTIxNTcsMC4wODYyNzQ1MDk4MDM5MjE1N11dXX0sInBhcmFtcyI6e30sImxheWVycyI6W3siZWZmZWN0Ijoic29saWQiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQYWxldHRlMSIsImlucHV0cyI6eyJvZmZzZXQiOjAuNX19LHsiZWZmZWN0Ijoic3BhcmtsZXMiLCJvcGFjaXR5IjowLjY2LCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQYWxldHRlMSIsImlucHV0cyI6eyJkZW5zaXR5Ijp7InR5cGUiOiJ0cmlhbmdsZSIsImlucHV0cyI6eyJ2YWx1ZSI6MC40MiwibWluIjowLCJtYXgiOjF9fSwib2Zmc2V0IjowLjV9fV19"
RedPattern = "CTP-eyJrZXkiOiIiLCJ2ZXJzaW9uIjoxLCJuYW1lIjoiTmV3IFBhdHRlcm4iLCJwYWxldHRlcyI6eyJQYWxldHRlMSI6W1swLFsxLDAsMF1dLFsxLFsxLDEsMV1dXX0sInBhcmFtcyI6e30sImxheWVycyI6W3siZWZmZWN0Ijoic29saWQiLCJvcGFjaXR5IjoxLCJibGVuZCI6Im5vcm1hbCIsInBhbGV0dGUiOiJQYWxldHRlMSIsImlucHV0cyI6eyJvZmZzZXQiOjB9fV19"

house_ambient_pattern = canopy.Pattern(GhostHousePattern)
win_pattern = canopy.Pattern(PatternRainbow)

hidden_room_pattern = canopy.Pattern(RedPattern)
kitchen_pattern = canopy.Pattern(RedPattern)
study_pattern = canopy.Pattern(RedPattern)
living_room_pattern = canopy.Pattern(RedPattern)
conservatory_pattern = canopy.Pattern(RedPattern)
bathroom_pattern = canopy.Pattern(RedPattern)
bedroom_pattern = canopy.Pattern(RedPattern)
attic_pattern = canopy.Pattern(RedPattern)

HIDDEN_ROOM = "hidden_room"
KITCHEN = "kitchen"
STUDY = "study"
LIVING_ROOM = "living_room"
CONSERVATORY = "conservatory"
BATHROOM = "bathroom"
BEDROOM = "bedroom"
ATTIC = "attic"

HIDDEN_ROOM_PIXEL_START = 0
HIDDEN_ROOM_PIXEL_LENGTH = 28
KITCHEN_PIXEL_START = HIDDEN_ROOM_PIXEL_START + HIDDEN_ROOM_PIXEL_LENGTH
KITCHEN_PIXEL_LENGTH = 29
STUDY_PIXEL_START = KITCHEN_PIXEL_START + KITCHEN_PIXEL_LENGTH
STUDY_PIXEL_LENGTH = 27
LIVING_ROOM_PIXEL_START = STUDY_PIXEL_START + STUDY_PIXEL_LENGTH
LIVING_ROOM_PIXEL_LENGTH = 50
CONSERVATORY_PIXEL_START = LIVING_ROOM_PIXEL_START + LIVING_ROOM_PIXEL_LENGTH
CONSERVATORY_PIXEL_LENGTH = 17
BATHROOM_PIXEL_START = CONSERVATORY_PIXEL_START + CONSERVATORY_PIXEL_LENGTH
BATHROOM_PIXEL_LENGTH = 15
BEDROOM_PIXEL_START = BATHROOM_PIXEL_START + BATHROOM_PIXEL_LENGTH
BEDROOM_PIXEL_LENGTH = 35
ATTIC_PIXELS_START = BEDROOM_PIXEL_START + BEDROOM_PIXEL_LENGTH
ATTIC_PIXELS_LENGTH = 58

WIN_STATE = "win"


class BaseRoomState(object):
    def __init__(self, name, start, length):
        self.name = name
        self.start = start
        self.length = length
        self.light_pattern = None
        self.params = canopy.Params()
        self.segment = canopy.Segment(1, start, length)
        self.state = False

    def set_state(self, state):
        self.state = state
        self._update_lighting()

    def _update_lighting(self):
        if self.state is WIN_STATE:
            self.light_pattern = win_pattern

    def draw(self):
        if self.light_pattern:
            canopy.draw(self.segment, self.light_pattern, alpha=0.3, params=self.params)


class HiddenRoomState(BaseRoomState):
    def __init__(self):
        super().__init__(HIDDEN_ROOM, HIDDEN_ROOM_PIXEL_START, HIDDEN_ROOM_PIXEL_LENGTH)

    def _update_lighting(self):
        super()._update_lighting()
        if self.state is not WIN_STATE:
            if self.state:
                self.light_pattern = hidden_room_pattern
            else:
                self.light_pattern = None


class KitchenState(BaseRoomState):
    def __init__(self):
        super().__init__(KITCHEN, KITCHEN_PIXEL_START, KITCHEN_PIXEL_LENGTH)

    def _update_lighting(self):
        super()._update_lighting()
        if self.state is not WIN_STATE:
            if self.state:
                self.light_pattern = kitchen_pattern
            else:
                self.light_pattern = house_ambient_pattern


class StudyState(BaseRoomState):
    def __init__(self):
        super().__init__(STUDY, STUDY_PIXEL_START, STUDY_PIXEL_LENGTH)

    def _update_lighting(self):
        super()._update_lighting()
        if self.state is not WIN_STATE:
            if self.state:
                self.light_pattern = study_pattern
            else:
                self.light_pattern = house_ambient_pattern


class LivingRoomState(BaseRoomState):
    def __init__(self):
        super().__init__(LIVING_ROOM, LIVING_ROOM_PIXEL_START, LIVING_ROOM_PIXEL_LENGTH)

    def _update_lighting(self):
        super()._update_lighting()
        if self.state is not WIN_STATE:
            if self.state:
                self.light_pattern = living_room_pattern
            else:
                self.light_pattern = house_ambient_pattern


class ConservatoryState(BaseRoomState):
    def __init__(self):
        super().__init__(
            CONSERVATORY, CONSERVATORY_PIXEL_START, CONSERVATORY_PIXEL_LENGTH
        )

    def _update_lighting(self):
        super()._update_lighting()
        if self.state is not WIN_STATE:
            if self.state:
                self.light_pattern = conservatory_pattern
            else:
                self.light_pattern = house_ambient_pattern


class BathroomState(BaseRoomState):
    def __init__(self):
        super().__init__(BATHROOM, BATHROOM_PIXEL_START, BATHROOM_PIXEL_LENGTH)

    def _update_lighting(self):
        super()._update_lighting()
        if self.state is not WIN_STATE:
            if self.state:
                self.light_pattern = bathroom_pattern
            else:
                self.light_pattern = house_ambient_pattern


class BedroomState(BaseRoomState):
    def __init__(self):
        super().__init__(BEDROOM, BEDROOM_PIXEL_START, BEDROOM_PIXEL_LENGTH)

    def _update_lighting(self):
        super()._update_lighting()
        if self.state is not WIN_STATE:
            if self.state:
                self.light_pattern = bedroom_pattern
            else:
                self.light_pattern = house_ambient_pattern


class AtticState(BaseRoomState):
    def __init__(self):
        super().__init__(ATTIC, ATTIC_PIXELS_START, ATTIC_PIXELS_LENGTH)

    def _update_lighting(self):
        super()._update_lighting()
        if self.state is not WIN_STATE:
            if self.state:
                self.light_pattern = attic_pattern
            else:
                self.light_pattern = house_ambient_pattern
