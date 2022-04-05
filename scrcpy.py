import asyncio
import pathlib

import adb_tunnel
import adblib
import config
import control_message
import controllers
import coords
import options
import servers
import util.util


async def scrcpy(
    crop: str = '',
    codec_options: str = '',
    encoder_name: str = '',
    log_level: options.LogLevel = options.LogLevel.INFO,
    max_size: int = 0,
    bit_rate: int = config.DEFAULT_BIT_RATE,
    max_fps: int = 0,
    lock_video_orientation: options.LockVideoOrientation = options.
    LockVideoOrientation.UNLOCKED,
    display_id: int = 0,
    show_touches: bool = False,
    control: bool = True,
    turn_screen_off: bool = False,
    stay_awake: bool = False,
    force_adb_forward: bool = False,
    power_off_on_close: bool = False,
    clipboard_autosync: bool = True,
    downsize_on_error: bool = True,
    cleanup: bool = True,
    server_path: str = '/usr/share/scrcpy/scrcpy-server',
    device_server_path: str = servers.DEVICE_SERVER_PATH,
    version: str = config.SCRCPY_VERSION,
    device_socket_name: str = adb_tunnel.DEVICE_SOCKET_NAME,
):
    params = servers.ServerParams(
        log_level=log_level,
        crop=crop,
        codec_options=codec_options,
        encoder_name=encoder_name,
        max_size=max_size,
        bit_rate=bit_rate,
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

    adb = adblib.ADB(adblib.get_executable())
    tunnel = adb_tunnel.Tunnel(adb, device_socket_name)

    server = servers.Server(params, adb, tunnel)

    server_process = await server.run()

    if control:
        controller = controllers.Controller(server.control_connection)
        controller_task = asyncio.create_task(controller.run())

        if turn_screen_off:
            await util.util.turn_screen_off(controller)

    await server_process.wait()


async def main():
    await scrcpy(
        log_level=options.LogLevel.VERBOSE,
        show_touches=True,
        # turn_screen_off=True,
    )


if __name__ == '__main__':
    asyncio.run(main())
