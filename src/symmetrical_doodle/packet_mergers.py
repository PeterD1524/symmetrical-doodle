import dataclasses

import symmetrical_doodle.packets


@dataclasses.dataclass
class Merger:
    config: bytes | None = dataclasses.field(default=None, init=False)

    def merge(self, packet: symmetrical_doodle.packets.Packet):
        is_config = packet.pts is None
        config = self.config
        if is_config:
            config = packet.input
        elif config is not None:
            packet.input = config + packet.input
            config = None
        self.config = config
