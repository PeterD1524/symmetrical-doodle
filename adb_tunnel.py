import asyncio
import asyncio.subprocess
import dataclasses
from typing import Optional

import adblib

DEVICE_SOCKET_NAME = 'scrcpy'


@dataclasses.dataclass
class Tunnel:
    adb: adblib.ADB

    forward: bool = dataclasses.field(init=False)
    server: Optional[asyncio.Server] = dataclasses.field(
        init=False
    )  # only used if not forward
    connections: asyncio.Queue[tuple[asyncio.StreamReader,
                                     asyncio.StreamWriter]
                               ] = dataclasses.field(
                                   default_factory=asyncio.Queue, init=False
                               )  # only used if not forward
    local_port: int = dataclasses.field(init=False)
    device_socket_name: str

    async def open(self, force_forward: bool = False):
        if not force_forward:
            try:
                await self.enable_reverse_any_port()
            except Exception:
                raise
            else:
                return
        await self.enable_forward_any_port()

    async def enable_forward_any_port(self):
        remote = f'localabstract:{self.device_socket_name}'
        process = await self.adb.forward(
            'tcp:0', remote, stdout=asyncio.subprocess.PIPE
        )
        stdout_data, _ = await process.communicate()
        assert not process.returncode
        self.local_port = int(stdout_data)
        self.forward = True

    async def enable_reverse_any_port(self):

        async def append_connection(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ):
            await self.connections.put((reader, writer))

        self.server = await asyncio.start_server(
            append_connection,
            host='127.0.0.1',
        )
        self.local_port = self.server.sockets[0].getsockname()[1]

        remote = f'localabstract:{self.device_socket_name}'
        local = f'tcp:{self.local_port}'
        process = await self.adb.reverse(remote, local)
        assert not await process.wait()
        self.forward = False

    async def close(self):
        if self.forward:
            process = await self.adb.forward_remove(f'tcp:{self.local_port}')
            returncode = await process.wait()
        else:
            process = await self.adb.reverse_remove(
                f'localabstract:{self.device_socket_name}'
            )
            returncode = await process.wait()
            self.server.close()
            await self.server.wait_closed()
            await self.close_connections()
        return returncode

    async def close_connections(self):
        connections = self.connections
        self.connections = asyncio.Queue()
        while True:
            try:
                _, writer = connections.get_nowait()
            except asyncio.QueueEmpty:
                break
            writer.close()
            await writer.wait_closed()
