import dataclasses
from typing import Any

import av

AV_PKT_FLAG_KEY = 0x0001


@dataclasses.dataclass
class Packet:
    pts: Any = dataclasses.field(default=None, init=False)
    dts: Any = dataclasses.field(default=None, init=False)
    flags: Any = dataclasses.field(default=0, init=False)

    input: bytes = dataclasses.field(default=b"")

    def create_av_packet(self):
        packet = av.Packet(self.input)
        packet.pts = self.pts
        packet.dts = self.dts
        return packet

    @property
    def size(self):
        return len(self.input)
