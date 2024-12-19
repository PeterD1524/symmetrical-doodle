import asyncio
import dataclasses

import av

import symmetrical_doodle.packets


@dataclasses.dataclass
class Decoder:
    packet_sink: asyncio.Queue[
        symmetrical_doodle.packets.VideoCodecContext | symmetrical_doodle.packets.Packet
    ] = dataclasses.field(default_factory=asyncio.Queue, init=False)
    sinks: list[asyncio.Queue[av.VideoFrame]] = dataclasses.field(
        default_factory=list, init=False
    )

    codec_context: av.VideoCodecContext | None = dataclasses.field(
        default=None, init=False
    )

    async def push(self, packet: symmetrical_doodle.packets.Packet):
        is_config = packet.pts is None
        if is_config:
            return

        codec_context = self.codec_context
        assert codec_context is not None
        frames = codec_context.decode(packet.create_av_packet())
        assert len(frames) == 1
        frame = frames[0]

        for sink in self.sinks:
            await sink.put(frame)

    async def run(self):
        while True:
            item = await self.packet_sink.get()
            if isinstance(item, symmetrical_doodle.packets.VideoCodecContext):
                self.codec_context = item.create_av_codec_context()
            else:
                await self.push(item)
