import asyncio
import dataclasses

import symmetrical_doodle.control_message
import symmetrical_doodle.tasks


@dataclasses.dataclass
class Controller:
    control_connection: tuple[asyncio.StreamReader, asyncio.StreamWriter]
    queue: asyncio.Queue[
        symmetrical_doodle.tasks.Task[symmetrical_doodle.control_message.ControlMessage]
    ] = dataclasses.field(default_factory=asyncio.Queue, init=False)

    async def push_message(
        self, message: symmetrical_doodle.control_message.ControlMessage
    ):
        task = symmetrical_doodle.tasks.Task(message)
        await self.queue.put(task)
        return task.event

    def push_message_nowait(
        self, message: symmetrical_doodle.control_message.ControlMessage
    ):
        task = symmetrical_doodle.tasks.Task(message)
        self.queue.put_nowait(task)
        return task.event

    async def send_message(
        self, message: symmetrical_doodle.control_message.ControlMessage
    ):
        serialized_message = message.serialize()
        _, writer = self.control_connection
        writer.write(serialized_message)
        await writer.drain()
        asyncio.Task

    async def run(self):
        while True:
            task = await self.queue.get()
            await self.send_message(task.todo)
            task.event.set()
