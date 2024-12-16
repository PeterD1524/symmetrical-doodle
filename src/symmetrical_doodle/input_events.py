import dataclasses
import enum

import symmetrical_doodle.coords
import symmetrical_doodle.sdl2.mouse


class Action(enum.Enum):
    DOWN = 0
    """key or button pressed"""
    UP = enum.auto()
    """key or button released"""


class MouseButton(enum.Enum):
    UNKNOWN = (0,)
    LEFT = (symmetrical_doodle.sdl2.mouse.LMASK,)
    RIGHT = (symmetrical_doodle.sdl2.mouse.RMASK,)
    MIDDLE = (symmetrical_doodle.sdl2.mouse.MMASK,)
    X1 = (symmetrical_doodle.sdl2.mouse.X1MASK,)
    X2 = (symmetrical_doodle.sdl2.mouse.X2MASK,)


@dataclasses.dataclass
class MouseClickEvent:
    position: symmetrical_doodle.coords.Position
    action: Action
    button: MouseButton
    buttons_state: int
