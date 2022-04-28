import asyncio
import asyncio.subprocess
import logging
import pathlib
import threading
from typing import Optional

import symmetrical_doodle.adb
import symmetrical_doodle.adb.utils
import symmetrical_doodle.adb_tunnel
import symmetrical_doodle.cli
import symmetrical_doodle.config
import symmetrical_doodle.control_message
import symmetrical_doodle.controllers
import symmetrical_doodle.coords
import symmetrical_doodle.decoders
import symmetrical_doodle.demuxers
import symmetrical_doodle.options
import symmetrical_doodle.servers
import symmetrical_doodle.utils

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_pyside_screens():
    import symmetrical_doodle.screens.pyside_screens
    return symmetrical_doodle.screens.pyside_screens


async def wait_and_cancel_all(event: asyncio.Event):
    await event.wait()
    current_task = asyncio.current_task()
    for task in asyncio.all_tasks():
        if task == current_task:
            continue
        task.cancel()


async def scrcpy(
    server_path: str,
    display: bool = True,
    # for prepare_adb
    serial: Optional[str] = None,
    tcpip_dst: Optional[str] = None,
    select_usb: bool = False,
    select_tcpip: bool = False,
    # for screen
    window_title: Optional[str] = None,
    # for ServerParams
    crop: Optional[str] = None,
    codec_options: Optional[str] = None,
    encoder_name: Optional[str] = None,
    log_level: symmetrical_doodle.options.LogLevel = symmetrical_doodle.
    options.LogLevel.INFO,
    port: Optional[int] = None,
    max_size: int = 0,
    bit_rate: int = symmetrical_doodle.config.DEFAULT_BIT_RATE,
    max_fps: int = 0,
    lock_video_orientation: symmetrical_doodle.options.
    LockVideoOrientation = symmetrical_doodle.options.LockVideoOrientation.
    UNLOCKED,
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
    device_server_path: str = symmetrical_doodle.servers.DEVICE_SERVER_PATH,
    version: str = symmetrical_doodle.config.SCRCPY_VERSION,
    device_socket_name: str = symmetrical_doodle.adb_tunnel.DEVICE_SOCKET_NAME
):
    if display:
        pyside_screens = get_pyside_screens()
    else:
        pyside_screens = None

    params = symmetrical_doodle.servers.ServerParams(
        log_level=log_level,
        crop=crop,
        codec_options=codec_options,
        encoder_name=encoder_name,
        port=port,
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
        version=version
    )

    adb = symmetrical_doodle.adb.ADB()
    await symmetrical_doodle.adb.utils.prepare_adb(
        adb,
        serial=serial,
        tcpip_dst=tcpip_dst,
        select_usb=select_usb,
        select_tcpip=select_tcpip
    )

    tunnel = symmetrical_doodle.adb_tunnel.Tunnel(adb, device_socket_name)

    server = symmetrical_doodle.servers.Server(params, adb, tunnel)

    loop = asyncio.new_event_loop()

    if display:
        assert pyside_screens is not None
        thread = pyside_screens.Thread(loop.run_forever)
    else:
        thread = threading.Thread(target=loop.run_forever)
    thread.start()

    server_process = asyncio.run_coroutine_threadsafe(server.run(),
                                                      loop).result()

    coros = []

    if control:
        controller = symmetrical_doodle.controllers.Controller(
            server.control_connection
        )
        if turn_screen_off:
            asyncio.run_coroutine_threadsafe(
                symmetrical_doodle.utils.turn_screen_off(controller), loop
            )

        control_coro = controller.run()
        coros.append(control_coro)

    demuxer = symmetrical_doodle.demuxers.Demuxer(server.video_connection)

    decoder = symmetrical_doodle.decoders.Decoder()

    decoder_coro = decoder.run()
    demuxer.sinks.append(decoder.packet_sink)

    demuxer_coro = demuxer.run()

    coros.extend([decoder_coro, demuxer_coro])

    if display:
        assert pyside_screens is not None
        assert isinstance(thread, pyside_screens.Thread)

        if window_title is None:
            try:
                window_title = server.info.device_name.decode()
            except UnicodeDecodeError:
                pass

        app = pyside_screens.App(
            thread,
            size=(server.info.frame_size.width, server.info.frame_size.height),
            window_title=window_title
        )

        decoder.sinks.append(app.screen.frame_receiver.frame_sink)
        screen_frame_receiver_coro = app.screen.frame_receiver.run()
        coros.append(screen_frame_receiver_coro)

        futures = [
            asyncio.run_coroutine_threadsafe(coro, loop) for coro in coros
        ]

        r = app.run()
    else:

        futures = [
            asyncio.run_coroutine_threadsafe(coro, loop) for coro in coros
        ]

    # cancel all tasks
    event = asyncio.Event()
    event_coro = wait_and_cancel_all(event)
    event_future = asyncio.run_coroutine_threadsafe(event_coro, loop)
    loop.call_soon_threadsafe(event.set)
    event_future.result()

    clean_up(loop, server, server_process)

    loop.call_soon_threadsafe(loop.stop)

    if isinstance(thread, threading.Thread):
        thread.join()
    else:
        thread.wait()


def clean_up(
    loop: asyncio.AbstractEventLoop, server: symmetrical_doodle.servers.Server,
    server_process: asyncio.subprocess.Process
):

    async def close_writer(writer: asyncio.StreamWriter):
        writer.write_eof()
        writer.close()
        await writer.wait_closed()

    asyncio.run_coroutine_threadsafe(
        close_writer(server.video_connection[1]), loop
    ).result()

    if server.control_connection is not None:
        asyncio.run_coroutine_threadsafe(
            close_writer(server.control_connection[1]), loop
        ).result()

    # Give some delay for the server to terminate properly
    WATCHDOG_DELAY = 1

    async def wait_for(
        process: asyncio.subprocess.Process, timeout: Optional[float]
    ):
        try:
            await asyncio.wait_for(process.wait(), timeout)
        except asyncio.TimeoutError:
            # After this delay, kill the server if it's not dead already.
            # On some devices, closing the sockets is not sufficient to wake up
            # the blocking calls while the device is asleep.
            logger.warning('Killing the server...')
            process.kill()

    asyncio.run_coroutine_threadsafe(
        wait_for(server_process, WATCHDOG_DELAY), loop
    ).result()


async def main():

    options = symmetrical_doodle.cli.parse_args()

    await scrcpy(
        options.server_path,
        #
        display=options.display,
        serial=options.serial,
        tcpip_dst=options.tcpip_dst,
        select_usb=options.select_usb,
        select_tcpip=options.select_tcpip,
        #
        window_title=options.window_title,
        #
        crop=options.crop,
        codec_options=options.codec_options,
        encoder_name=options.encoder_name,
        log_level=options.log_level,
        port=options.port,
        max_size=options.max_size,
        bit_rate=options.bit_rate,
        max_fps=options.max_fps,
        lock_video_orientation=options.lock_video_orientation,
        display_id=options.display_id,
        show_touches=options.show_touches,
        control=options.control,
        turn_screen_off=options.turn_screen_off,
        stay_awake=options.stay_awake,
        force_adb_forward=options.force_adb_forward,
        power_off_on_close=options.power_off_on_close,
        clipboard_autosync=options.clipboard_autosync,
        downsize_on_error=options.downsize_on_error,
        cleanup=options.cleanup
    )


if __name__ == '__main__':
    asyncio.run(main())
