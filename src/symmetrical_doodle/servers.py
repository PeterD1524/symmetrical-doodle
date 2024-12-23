import asyncio
import asyncio.subprocess
import dataclasses
import logging
import pathlib
from typing import Optional

import symmetrical_doodle.adb
import symmetrical_doodle.adb_tunnel
import symmetrical_doodle.config
import symmetrical_doodle.coords
import symmetrical_doodle.options
import symmetrical_doodle.utils.conection

logger = logging.getLogger(__name__)

DEVICE_SERVER_PATH = "/data/local/tmp/scrcpy-server.jar"

DEVICE_NAME_FIELD_LENGTH = 64


def create_server_params(
    server_path: str,
    crop: Optional[str] = None,
    codec_options: Optional[str] = None,
    encoder_name: Optional[str] = None,
    port: Optional[int] = None,
    log_level: symmetrical_doodle.options.LogLevel = symmetrical_doodle.options.LogLevel.INFO,
    max_size: int = 0,
    video_bit_rate: int = symmetrical_doodle.config.DEFAULT_VIDEO_BIT_RATE,
    max_fps: int = 0,
    lock_video_orientation: symmetrical_doodle.options.LockVideoOrientation = symmetrical_doodle.options.LockVideoOrientation.UNLOCKED,
    display_id: int = 0,
    show_touches: bool = False,
    control: bool = True,
    stay_awake: bool = False,
    force_adb_forward: bool = False,
    power_off_on_close: bool = False,
    clipboard_autosync: bool = True,
    downsize_on_error: bool = True,
    cleanup: bool = True,
    device_server_path: str = DEVICE_SERVER_PATH,
    version: str = symmetrical_doodle.config.SCRCPY_VERSION,
):
    return ServerParams(
        log_level=log_level,
        crop=crop,
        codec_options=codec_options,
        encoder_name=encoder_name,
        port=port,
        max_size=max_size,
        video_bit_rate=video_bit_rate,
        max_fps=max_fps,
        lock_video_orientation=lock_video_orientation,
        control=control,
        display_id=display_id,
        show_touches=show_touches,
        stay_awake=stay_awake,
        force_adb_forward=force_adb_forward,
        power_off_on_close=power_off_on_close,
        clipboard_autosync=clipboard_autosync,
        downsize_on_error=downsize_on_error,
        cleanup=cleanup,
        server_path=pathlib.Path(server_path),
        device_server_path=device_server_path,
        version=version,
    )


def create_default_server(server_path: str):
    adb = symmetrical_doodle.adb.ADB()
    tunnel = symmetrical_doodle.adb_tunnel.Tunnel(
        adb, symmetrical_doodle.adb_tunnel.DEVICE_SOCKET_NAME
    )
    params = create_server_params(server_path)
    return Server(params, adb, tunnel)


@dataclasses.dataclass
class ServerInfo:
    device_name: bytes


async def read_device_info(
    device_connection: tuple[asyncio.StreamReader, asyncio.StreamWriter]
):
    reader, _ = device_connection
    data = await reader.readexactly(DEVICE_NAME_FIELD_LENGTH)
    device_name = data[: DEVICE_NAME_FIELD_LENGTH - 1]
    end = device_name.find(b"\x00")
    if end != -1:
        device_name = device_name[:end]
    return ServerInfo(device_name)


@dataclasses.dataclass
class ServerParams:
    log_level: symmetrical_doodle.options.LogLevel
    crop: Optional[str]
    codec_options: Optional[str]
    encoder_name: Optional[str]
    port: Optional[int]
    max_size: int
    video_bit_rate: int
    max_fps: int
    lock_video_orientation: symmetrical_doodle.options.LockVideoOrientation
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

    adb: symmetrical_doodle.adb.ADB

    info: Optional[ServerInfo] = dataclasses.field(default=None, init=False)

    tunnel: symmetrical_doodle.adb_tunnel.Tunnel

    process: Optional[asyncio.subprocess.Process] = dataclasses.field(
        default=None, init=False
    )

    video_connection: Optional[tuple[asyncio.StreamReader, asyncio.StreamWriter]] = (
        dataclasses.field(default=None, init=False)
    )
    control_connection: Optional[tuple[asyncio.StreamReader, asyncio.StreamWriter]] = (
        dataclasses.field(default=None, init=False)
    )

    def execute(self):
        command = [
            "shell",
            f"CLASSPATH={self.params.device_server_path}",
            "app_process",
            "/",
            "com.genymobile.scrcpy.Server",
            self.params.version,
        ]

        command.append(f"log_level={self.params.log_level.to_server_string()}")
        command.append(f"video_bit_rate={self.params.video_bit_rate}")

        command.append("audio=false")
        if self.params.max_size:
            command.append(f"max_size={self.params.max_size}")
        if self.params.max_fps:
            command.append(f"max_fps={self.params.max_fps}")
        if (
            self.params.lock_video_orientation
            is not symmetrical_doodle.options.LockVideoOrientation.UNLOCKED
        ):
            command.append(
                f"lock_video_orientation={self.params.lock_video_orientation.value}"
            )
        if self.tunnel.forward:
            command.append("tunnel_forward=true")
        if self.params.crop is not None:
            command.append(f"crop={self.params.crop}")
        if not self.params.control:
            # By default, control is true
            command.append("control=false")
        if self.params.display_id:
            command.append(f"display_id={self.params.display_id}")
        if self.params.show_touches:
            command.append("show_touches=true")
        if self.params.stay_awake:
            command.append("stay_awake=true")
        if self.params.codec_options is not None:
            command.append(f"codec_options={self.params.codec_options}")
        if self.params.encoder_name is not None:
            command.append(f"encoder_name={self.params.encoder_name}")
        if self.params.power_off_on_close:
            command.append("power_off_on_close=true")
        if not self.params.clipboard_autosync:
            # By default, clipboard_autosync is true
            command.append("clipboard_autosync=false")
        if not self.params.downsize_on_error:
            # By default, downsize_on_error is true
            command.append("downsize_on_error=false")
        if not self.params.cleanup:
            # By default, cleanup is true
            command.append("cleanup=false")

        return self.adb.run_command(command)

    async def connect(self):
        if self.tunnel.forward:
            host = "127.0.0.1"
            port = self.tunnel.local_port

            self.video_connection = await retry_connect(100, 0.1, host, port)
            if self.params.control:
                # we know that the device is listening, we don't need several
                # attempts
                self.control_connection = await asyncio.open_connection(
                    host=host, port=port
                )
        else:
            self.video_connection = await self.tunnel.connections.get()
            if self.params.control:
                self.control_connection = await self.tunnel.connections.get()

    async def run(self):
        """Runs the server and connects to the server."""
        await self.push()

        async with self.tunnel.open(
            port=self.params.port, force_forward=self.params.force_adb_forward
        ):
            self.process = await self.execute()
            await self.connect()

        assert self.video_connection is not None
        self.info = await read_device_info(self.video_connection)

    async def push(self):
        assert self.params.server_path.is_file()
        process = await self.adb.push(
            [str(self.params.server_path)], self.params.device_server_path
        )
        assert not await process.wait()

    async def close(self):

        if self.video_connection is not None:
            await symmetrical_doodle.utils.conection.close_connection(
                self.video_connection
            )
            self.video_connection = None
        if self.control_connection is not None:
            await symmetrical_doodle.utils.conection.close_connection(
                self.control_connection
            )
            self.control_connection = None

        if self.process is not None:
            # Give some delay for the server to terminate properly
            WATCHDOG_DELAY = 1
            try:
                await asyncio.wait_for(self.process.wait(), WATCHDOG_DELAY)
            except asyncio.TimeoutError:
                # After this delay, kill the server if it's not dead already.
                # On some devices, closing the sockets is not sufficient to
                # wake up the blocking calls while the device is asleep.
                logger.warning("Killing the server...")
                self.process.kill()


async def retry_connect(attempts: int, delay: float, host, port):
    while attempts > 0:
        logger.debug("Remaining connection attempts: %s", attempts)
        try:
            reader, writer = await asyncio.open_connection(host=host, port=port)
        except ConnectionRefusedError:
            pass
        else:
            try:
                await reader.readexactly(1)
            except asyncio.IncompleteReadError:
                writer.close()
                await writer.wait_closed()
            else:
                return reader, writer

        attempts -= 1
        if attempts:
            await asyncio.sleep(delay)
    raise RuntimeError
