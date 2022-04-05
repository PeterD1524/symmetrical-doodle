import dataclasses


@dataclasses.dataclass
class Size:
    width: int
    height: int


@dataclasses.dataclass
class Point:
    x: int
    y: int


@dataclasses.dataclass
class Position:
    screen_size: Size
    point: Point
