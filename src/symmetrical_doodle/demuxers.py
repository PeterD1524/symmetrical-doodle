import asyncio
import dataclasses
import enum

import av.codec
import av.codec.context

import symmetrical_doodle.packet_mergers
import symmetrical_doodle.packets
import symmetrical_doodle.utils.buffer

PACKET_HEADER_SIZE = 12

PACKET_FLAG_CONFIG = 1 << 63
PACKET_FLAG_KEY_FRAME = 1 << 62

PACKET_PTS_MASK = PACKET_FLAG_KEY_FRAME - 1


class CodecID(enum.Enum):
    H264 = 0x68323634  # "h264" in ASCII
    H265 = 0x68323635  # "h265" in ASCII
    AV1 = 0x00617631  # "av1" in ASCII
    OPUS = 0x6F707573  # "opus" in ASCII
    AAC = 0x00616163  # "aac" in ASCII
    FLAC = 0x666C6163  # "flac" in ASCII
    RAW = 0x00726177  # "raw" in ASCII


def to_av_codec_id(codec_id: int):

    av_codec_names = {
        CodecID.H264.value: "h264",
        CodecID.H265.value: "hevc",
        CodecID.AV1.value: "av1",
        CodecID.OPUS.value: "opus",
        CodecID.AAC.value: "aac",
        CodecID.FLAC.value: "flac",
        CodecID.RAW.value: "pcm_s16le",
    }
    try:
        return av_codec_names[codec_id]
    except KeyError:
        return None


@dataclasses.dataclass
class Demuxer:
    connection: tuple[asyncio.StreamReader, asyncio.StreamWriter]

    sinks: list[
        asyncio.Queue[
            symmetrical_doodle.packets.VideoCodecContext
            | symmetrical_doodle.packets.Packet
        ]
    ] = dataclasses.field(default_factory=list, init=False)

    pending: symmetrical_doodle.packets.Packet | None = dataclasses.field(
        default=None, init=False
    )

    async def receive_codec_id(self):
        reader, _ = self.connection
        return symmetrical_doodle.utils.buffer.read32be(await reader.readexactly(4), 0)[
            0
        ]

    async def receive_video_size(self):
        reader, _ = self.connection
        data = await reader.readexactly(8)
        start = 0
        width, start = symmetrical_doodle.utils.buffer.read32be(data, start)
        height, start = symmetrical_doodle.utils.buffer.read32be(data, start)
        return width, height

    async def run(self):
        raw_codec_id = await self.receive_codec_id()
        assert raw_codec_id not in (0, 1)
        codec_id = to_av_codec_id(raw_codec_id)
        assert codec_id is not None

        codec = av.codec.Codec(codec_id)

        flags = av.codec.context.Flags.low_delay

        if codec.type == "video":
            width, height = await self.receive_video_size()
            context = symmetrical_doodle.packets.VideoCodecContext(
                codec, flags, width, height, "yuv420p"
            )
        else:
            assert False

        await self.push_item_to_sinks(context)

        must_merge_config_packet = (
            raw_codec_id == CodecID.H264.value or raw_codec_id == CodecID.H265
        )

        merger = (
            symmetrical_doodle.packet_mergers.Merger()
            if must_merge_config_packet
            else None
        )

        while True:
            packet = await self.receive_packet()
            if must_merge_config_packet:
                assert merger is not None
                merger.merge(packet)
            await self.push_item_to_sinks(packet)

    async def receive_packet(self):
        reader, _ = self.connection
        header = await reader.readexactly(PACKET_HEADER_SIZE)

        start = 0
        pts_flags, start = symmetrical_doodle.utils.buffer.read64be(header, start)
        length, start = symmetrical_doodle.utils.buffer.read32be(header, start)
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

    async def push_item_to_sinks(
        self,
        item: (
            symmetrical_doodle.packets.VideoCodecContext
            | symmetrical_doodle.packets.Packet
        ),
    ):
        for sink in self.sinks:
            await sink.put(item)
