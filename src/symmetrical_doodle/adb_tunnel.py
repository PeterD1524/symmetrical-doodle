import asyncio
import asyncio.subprocess
import contextlib
import dataclasses
import logging
from typing import Optional

import symmetrical_doodle.adb
import symmetrical_doodle.utils.conection

DEVICE_SOCKET_NAME = 'scrcpy'

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Tunnel:
    adb: symmetrical_doodle.adb.ADB

    forward: Optional[bool] = dataclasses.field(default=None, init=False)

    # only used for reverse
    server: Optional[asyncio.Server
                     ] = dataclasses.field(default=None, init=False)
    # only used for reverse
    connections: asyncio.Queue[
        tuple[asyncio.StreamReader, asyncio.StreamWriter]
    ] = dataclasses.field(default_factory=asyncio.Queue, init=False)

    local_port: Optional[int] = dataclasses.field(default=None, init=False)
    device_socket_name: str

    @contextlib.asynccontextmanager
    async def open(
        self, port: Optional[int] = None, force_forward: bool = False
    ):
        if force_forward:
            await self.enable_forward(port)
        else:
            try:
                await self.enable_reverse(port)
            except symmetrical_doodle.adb.CalledProcessError:
                logger.warning(
                    "'adb reverse' failed, fallback to 'adb forward'"
                )
                await self.enable_forward(port)
        try:
            yield
        finally:
            await self.close()

    async def enable_forward(self, port: Optional[int] = None):
        assert self.forward is None

        if port is None:
            port = 0

        remote = f'localabstract:{self.device_socket_name}'
        local_port = await self.adb.forward(f'tcp:{port}', remote)

        self.local_port = local_port
        self.forward = True

    async def enable_reverse(self, port: Optional[int] = None):
        assert self.forward is None

        async def append_connection(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ):
            await self.connections.put((reader, writer))

        server = await asyncio.start_server(
            append_connection, host='127.0.0.1', port=port
        )
        local_port = server.sockets[0].getsockname()[1]

        remote = f'localabstract:{self.device_socket_name}'
        local = f'tcp:{local_port}'
        try:
            port = await self.adb.reverse(remote, local)
            assert port is None
        except symmetrical_doodle.adb.CalledProcessError:
            server.close()
            await server.wait_closed()
            await self.close_connections()
            raise

        self.server = server
        self.local_port = local_port
        self.forward = False

    async def close(self):
        if self.forward is None:
            return
        if self.forward:
            process = await self.adb.forward_remove(f'tcp:{self.local_port}')
        else:
            process = await self.adb.reverse_remove(
                f'localabstract:{self.device_socket_name}'
            )
            self.server.close()
            await self.server.wait_closed()
            await self.close_connections()

    async def close_connections(self):
        connections = self.connections
        self.connections = asyncio.Queue()
        while True:
            try:
                connection = connections.get_nowait()
            except asyncio.QueueEmpty:
                break
            symmetrical_doodle.utils.conection.close_connection(connection)
