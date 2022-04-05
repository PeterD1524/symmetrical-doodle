import asyncio
import dataclasses

import control_message


@dataclasses.dataclass
class Controller:
    control_connection: tuple[asyncio.StreamReader, asyncio.StreamWriter]
    queue: asyncio.Queue[
        control_message.ControlMessage
    ] = dataclasses.field(default_factory=asyncio.Queue, init=False)

    async def push_message(self, message: control_message.ControlMessage):
        await self.queue.put(message)

    def push_message_nowait(self, message: control_message.ControlMessage):
        self.queue.put_nowait(message)

    async def process_message(self, message: control_message.ControlMessage):
        # print('[controller]', message)
        serialized_message = message.serialize()
        _, writer = self.control_connection
        writer.write(serialized_message)
        await writer.drain()

    async def run(self):
        while True:
            message = await self.queue.get()
            await self.process_message(message)
