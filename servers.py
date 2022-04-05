import asyncio
import dataclasses
import pathlib
from typing import Optional

import adb_tunnel
import adblib
import coords
import options

DEVICE_SERVER_PATH = '/data/local/tmp/scrcpy-server.jar'

DEVICE_NAME_FIELD_LENGTH = 64


@dataclasses.dataclass
class ServerInfo:
    device_name: bytes
    frame_size: coords.Size


async def read_device_info(
    device_connection: tuple[asyncio.StreamReader, asyncio.StreamWriter]
):
    reader, _ = device_connection
    data = await reader.readexactly(DEVICE_NAME_FIELD_LENGTH + 4)
    device_name = data[:DEVICE_NAME_FIELD_LENGTH - 1]
    end = device_name.find(b'\x00')
    if end != -1:
        device_name = device_name[:end]
    width = (data[DEVICE_NAME_FIELD_LENGTH] <<
             8) | data[DEVICE_NAME_FIELD_LENGTH + 1]
    height = (data[DEVICE_NAME_FIELD_LENGTH + 2] <<
              8) | data[DEVICE_NAME_FIELD_LENGTH + 3]
    return ServerInfo(device_name, coords.Size(width, height))


@dataclasses.dataclass
class ServerParams:
    log_level: options.LogLevel
    crop: str
    codec_options: str
    encoder_name: str
    max_size: int
    bit_rate: int
    max_fps: int
    lock_video_orientation: int
    control: bool
    display_id: int
    show_touches: bool
    stay_awake: bool
    force_adb_forward: bool
    power_off_on_close: bool
    clipboard_autosync: bool
    downsize_on_error: bool
    cleanup: bool

    server_path: pathlib.Path
    device_server_path: str
    version: str


@dataclasses.dataclass
class Server:
    params: ServerParams

    adb: adblib.ADB

    info: ServerInfo = dataclasses.field(init=False)

    tunnel: adb_tunnel.Tunnel

    video_connection: tuple[asyncio.StreamReader,
                            asyncio.StreamWriter] = dataclasses.field(
                                init=False
                            )
    control_connection: Optional[tuple[asyncio.StreamReader,
                                       asyncio.StreamWriter]
                                 ] = dataclasses.field(init=False)

    def execute(self):
        command = [
            'shell',
            f'CLASSPATH={self.params.device_server_path}',
            'app_process',
            '/',
            'com.genymobile.scrcpy.Server',
            self.params.version,
        ]

        command.append(f'log_level={self.params.log_level.to_server_string()}')
        command.append(f'bit_rate={self.params.bit_rate}')

        if self.params.max_size:
            command.append(f'max_size={self.params.max_size}')
        if self.params.max_fps:
            command.append(f'max_fps={self.params.max_fps}')
        if self.params.lock_video_orientation != options.LockVideoOrientation.UNLOCKED:
            command.append(
                f'lock_video_orientation={self.params.lock_video_orientation}'
            )
        if self.tunnel.forward:
            command.append('tunnel_forward=true')
        if self.params.crop:
            command.append(f'crop={self.params.crop}')
        if not self.params.control:
            command.append('control=false')
        if self.params.display_id:
            command.append(f'display_id={self.params.display_id}')
        if self.params.show_touches:
            command.append('show_touches=true')
        if self.params.stay_awake:
            command.append('stay_awake=true')
        if self.params.codec_options:
            command.append(f'codec_options={self.params.codec_options}')
        if self.params.encoder_name:
            command.append(f'encoder_name={self.params.encoder_name}')
        if self.params.power_off_on_close:
            command.append('power_off_on_close=true')
        if not self.params.clipboard_autosync:
            command.append('clipboard_autosync=false')
        if not self.params.downsize_on_error:
            command.append('downsize_on_error=false')
        if not self.params.cleanup:
            command.append('cleanup=false')

        return self.adb.run_command(command)

    async def connect_to(self):
        if self.tunnel.forward:
            host = '127.0.0.1'
            port = self.tunnel.local_port

            self.video_connection = await connect_to_server(
                100, 0.1, host, port
            )
            if self.params.control:
                self.control_connection = await asyncio.open_connection(
                    host=host, port=port
                )
        else:
            self.video_connection = await self.tunnel.connections.get()
            if self.params.control:
                self.control_connection = await self.tunnel.connections.get()

        await self.tunnel.close()

        self.info = await read_device_info(self.video_connection)

    async def run(self):
        process = await self.adb.start_server()
        assert not await process.wait()

        await self.push()

        await self.tunnel.open(force_forward=self.params.force_adb_forward)

        process = await self.execute()

        await self.connect_to()

        return process

    async def push(self):
        assert self.params.server_path.is_file()
        process = await self.adb.push(
            [str(self.params.server_path)], self.params.device_server_path
        )
        assert not await process.wait()


async def connect_to_server(attempts: int, delay: float, host, port):
    while attempts > 0:
        try:
            reader, writer = await asyncio.open_connection(
                host=host, port=port
            )
        except ConnectionRefusedError:
            pass
        else:
            data = await reader.read(n=1)
            if len(data) == 1:
                return reader, writer
            else:
                writer.close()
                await writer.wait_closed()

        attempts -= 1
        if attempts:
            await asyncio.sleep(delay)
    raise RuntimeError
