import dataclasses
import enum

import coords
import sdl2.mouse


class Action(enum.Enum):
    DOWN = 0
    """key or button pressed"""
    UP = enum.auto()
    """key or button released"""


class MouseButton(enum.Enum):
    UNKNOWN = 0,
    LEFT = sdl2.mouse.LMASK,
    RIGHT = sdl2.mouse.RMASK,
    MIDDLE = sdl2.mouse.MMASK,
    X1 = sdl2.mouse.X1MASK,
    X2 = sdl2.mouse.X2MASK,


@dataclasses.dataclass
class MouseClickEvent:
    position: coords.Position
    action: Action
    button: MouseButton
    buttons_state: int
