import asyncio
import asyncio.subprocess
import dataclasses
from typing import Optional

import symmetrical_doodle.adb

DEVICE_SOCKET_NAME = 'scrcpy'


@dataclasses.dataclass
class Tunnel:
    adb: symmetrical_doodle.adb.ADB

    forward: Optional[bool] = dataclasses.field(default=None, init=False)
    server: Optional[asyncio.Server] = dataclasses.field(
        default=None, init=False
    )  # only used if not forward
    connections: asyncio.Queue[tuple[asyncio.StreamReader,
                                     asyncio.StreamWriter]
                               ] = dataclasses.field(
                                   default_factory=asyncio.Queue, init=False
                               )  # only used if not forward
    local_port: Optional[int] = dataclasses.field(default=None, init=False)
    device_socket_name: str

    async def open(
        self, port: Optional[int] = None, force_forward: bool = False
    ):
        if not force_forward:
            try:
                await self.enable_reverse(port)
            except Exception:
                raise
            else:
                return
        await self.enable_forward(port)

    async def enable_forward(self, port: Optional[int] = None):
        if port is None:
            port = 0

        remote = f'localabstract:{self.device_socket_name}'
        process = await self.adb.forward(
            f'tcp:{port}', remote, stdout=asyncio.subprocess.PIPE
        )
        stdout_data, _ = await process.communicate()
        assert not process.returncode
        self.local_port = int(stdout_data)
        self.forward = True

    async def enable_reverse(self, port: Optional[int] = None):

        async def append_connection(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ):
            await self.connections.put((reader, writer))

        self.server = await asyncio.start_server(
            append_connection, host='127.0.0.1', port=port
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
            writer.write_eof()
            writer.close()
            await writer.wait_closed()
