import dataclasses
from typing import Any

import av
import av.codec
import av.codec.context

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


@dataclasses.dataclass
class VideoCodecContext:
    codec: av.codec.Codec
    flags: int
    width: int
    height: int
    pix_fmt: str

    def create_av_codec_context(self):
        context = av.codec.context.CodecContext.create(self.codec)
        context.flags |= self.flags
        context.width = self.width
        context.height = self.height
        context.pix_fmt = self.pix_fmt
        return context
