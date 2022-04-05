import asyncio
import dataclasses

import device_message


@dataclasses.dataclass
class Receiver:
    control_connection: tuple[asyncio.StreamReader, asyncio.StreamWriter]

    async def run(self):
        reader, _ = self.control_connection

        buf = b''

        while True:
            assert len(buf) < device_message.DEVICE_MSG_MAX_SIZE
            data = await reader.read(
                device_message.DEVICE_MSG_MAX_SIZE - len(buf)
            )
            if not data:
                break

            buf += data
            try:
                consumed = self.process_messages(buf, 0)
            except device_message.NotRecoverable:
                break

            buf = buf[consumed:]

    def process_messages(self, buf: bytes, start: int):
        while True:
            try:
                message, start = device_message.deserialize(buf, start)
            except device_message.NotAvailable:
                return start

            self.process_message(message)

            if start == len(buf):
                return start

    def process_message(self, message: device_message.DeviceMessage):
        print('[receiver]', message)
        pass
