import asyncio
import dataclasses

import symmetrical_doodle.packets
import symmetrical_doodle.utils.buffer

PACKET_HEADER_SIZE = 12

PACKET_FLAG_CONFIG = 1 << 63
PACKET_FLAG_KEY_FRAME = 1 << 62

PACKET_PTS_MASK = PACKET_FLAG_KEY_FRAME - 1


@dataclasses.dataclass
class Demuxer:
    connection: tuple[asyncio.StreamReader, asyncio.StreamWriter]

    sinks: list[asyncio.Queue[symmetrical_doodle.packets.Packet]
                ] = dataclasses.field(default_factory=list, init=False)

    pending: symmetrical_doodle.packets.Packet = dataclasses.field(
        default=None, init=False
    )

    async def run(self):
        while True:
            packet = await self.receive_packet()

            # print(
            #     f'{packet.pts=} {packet.dts=} {packet.flags=} {len(packet.input)=}'
            # )

            await self.push_packet(packet)

    async def receive_packet(self):
        reader, _ = self.connection
        header = await reader.readexactly(PACKET_HEADER_SIZE)

        start = 0
        pts_flags, start = symmetrical_doodle.utils.buffer.read64be(
            header, start
        )
        length, start = symmetrical_doodle.utils.buffer.read32be(
            header, start
        )
        assert length

        data = await reader.readexactly(length)
        packet = symmetrical_doodle.packets.Packet(data)

        if pts_flags & PACKET_FLAG_CONFIG:
            packet.pts = None
        else:
            packet.pts = pts_flags & PACKET_PTS_MASK

        if pts_flags & PACKET_FLAG_KEY_FRAME:
            packet.flags |= symmetrical_doodle.packets.AV_PKT_FLAG_KEY

        packet.dts = packet.pts

        return packet

    async def push_packet(self, packet: symmetrical_doodle.packets.Packet):
        is_config = packet.pts is None

        if self.pending is not None:
            self.pending.input += packet.input

            if not is_config:
                self.pending.pts = packet.pts
                self.pending.dts = packet.dts
                self.pending.flags = packet.flags
                packet = self.pending
        elif is_config:
            self.pending = symmetrical_doodle.packets.Packet(packet.input)

        await self.push_packet_to_sinks(packet)

        if not is_config:
            self.pending = None

    async def push_packet_to_sinks(
        self, packet: symmetrical_doodle.packets.Packet
    ):
        for sink in self.sinks:
            await sink.put(packet)
