import asyncio
import dataclasses

import symmetrical_doodle.device_message


@dataclasses.dataclass
class Receiver:
    control_connection: tuple[asyncio.StreamReader, asyncio.StreamWriter]

    async def run(self):
        reader, _ = self.control_connection

        buf = b""

        while True:
            assert len(buf) < symmetrical_doodle.device_message.DEVICE_MSG_MAX_SIZE
            data = await reader.read(
                symmetrical_doodle.device_message.DEVICE_MSG_MAX_SIZE - len(buf)
            )
            if not data:
                break

            buf += data
            try:
                consumed = self.process_messages(buf, 0)
            except symmetrical_doodle.device_message.NotRecoverable:
                break

            buf = buf[consumed:]

    def process_messages(self, buf: bytes, start: int):
        while True:
            try:
                message, start = symmetrical_doodle.device_message.deserialize(
                    buf, start
                )
            except symmetrical_doodle.device_message.NotAvailable:
                return start

            self.process_message(message)

            if start == len(buf):
                return start

    def process_message(self, message: symmetrical_doodle.device_message.DeviceMessage):
        pass
