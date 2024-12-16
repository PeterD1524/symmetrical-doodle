import asyncio
import dataclasses

import av

import symmetrical_doodle.packets


@dataclasses.dataclass
class Decoder:
    packet_sink: asyncio.Queue[
        symmetrical_doodle.packets.Packet
    ] = dataclasses.field(default_factory=asyncio.Queue, init=False)
    sinks: list[asyncio.Queue[av.VideoFrame]
                ] = dataclasses.field(default_factory=list, init=False)

    codec_context: av.CodecContext = dataclasses.field(
        default_factory=lambda: av.CodecContext.create('h264', 'r'),
        init=False
    )

    async def push(self, packet: symmetrical_doodle.packets.Packet):
        is_config = packet.pts is None
        if is_config:
            return

        frames = self.codec_context.decode(packet.create_av_packet())
        assert len(frames) == 1
        frame = frames[0]

        for sink in self.sinks:
            await sink.put(frame)

    async def run(self):
        while True:
            packet = await self.packet_sink.get()
            await self.push(packet)
