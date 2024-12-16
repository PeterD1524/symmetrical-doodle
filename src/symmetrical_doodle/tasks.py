import asyncio
import dataclasses
from typing import Generic, TypeVar

T = TypeVar('T')


@dataclasses.dataclass
class Task(Generic[T]):
    todo: T
    event: asyncio.Event = dataclasses.field(default_factory=asyncio.Event)
