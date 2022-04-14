import asyncio
import pathlib
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
import symmetrical_doodle.screens.cv2_screens
import symmetrical_doodle.servers
import symmetrical_doodle.utils


async def configure_tcpip_unknown_address(adb: symmetrical_doodle.adb.ADB):
    raise NotImplementedError


async def prepare_adb(
    adb: symmetrical_doodle.adb.ADB, serial: Optional[str], tcpip: bool,
    tcpip_dst: Optional[str], select_usb: bool, select_tcpip: bool
):
    # tcpip_dst implies tcpip
    assert not (tcpip_dst is not None and not tcpip)

    # If tcpip_dst parameter is given, then it must connect to this address.
    # Therefore, the device is unknown, so serial is meaningless at this point.
    assert not (serial is not None and tcpip_dst is not None)

    # A device must be selected via a serial in all cases except when --tcpip=
    # is called with a parameter (in that case, the device may initially not
    # exist, and scrcpy will execute "adb connect").
    need_initial_serial = tcpip_dst is None

    if need_initial_serial:
        # At most one of the 3 following parameters may be set
        assert sum([serial is not None, select_usb, select_tcpip]) <= 1

        transports = await adb.list_connected_devices()
        if serial is not None:
            s = serial.encode()
            transports = [t for t in transports if t.serial == s]
            assert len(transports) == 1
        elif select_usb:
            adb.use_usb_device(True)
            serial = (await adb.get_serialno()).decode()
        elif select_tcpip:
            adb.use_tcpip_device(True)
            serial = (await adb.get_serialno()).decode()
        else:
            adb.use_usb_device(False)
            adb.use_tcpip_device(False)
            del adb.serial
            del adb.transport_id
            serial = (await adb.get_serialno()).decode()

        if tcpip:
            assert tcpip_dst is None
            adb.serial = serial
            await configure_tcpip_unknown_address(adb)
    else:
        host, sep, port = tcpip_dst.partition(':')
        if sep:
            port = int(port)
        else:
            port = None
        try:
            await adb.disconnect(host, port)
        except symmetrical_doodle.adb.Error:
            pass
        result = await adb.connect(host, port)
        assert result.startswith(b'connected to ')

    adb.serial = serial


async def scrcpy(
    server_path: str,
    # for prepare_adb
    serial: Optional[str] = None,
    tcpip: bool = False,
    tcpip_dst: Optional[str] = None,
    select_usb: bool = False,
    select_tcpip: bool = False,
    # for ServerParams
    crop: Optional[str] = None,
    codec_options: Optional[str] = None,
    encoder_name: Optional[str] = None,
    log_level: symmetrical_doodle.options.LogLevel = symmetrical_doodle.
    options.LogLevel.INFO,
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
    device_socket_name: str = symmetrical_doodle.adb_tunnel.DEVICE_SOCKET_NAME,
):
    params = symmetrical_doodle.servers.ServerParams(
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

    adb = symmetrical_doodle.adb.ADB()
    await prepare_adb(
        adb,
        serial=serial,
        tcpip=tcpip,
        tcpip_dst=tcpip_dst,
        select_usb=select_usb,
        select_tcpip=select_tcpip
    )

    tunnel = symmetrical_doodle.adb_tunnel.Tunnel(adb, device_socket_name)

    server = symmetrical_doodle.servers.Server(params, adb, tunnel)

    server_process = await server.run()

    if control:
        controller = symmetrical_doodle.controllers.Controller(
            server.control_connection
        )
        controller_task = asyncio.create_task(controller.run())

        if turn_screen_off:
            await symmetrical_doodle.utils.turn_screen_off(controller)

    demuxer = symmetrical_doodle.demuxers.Demuxer(server.video_connection)

    decoder = symmetrical_doodle.decoders.Decoder()

    screen = symmetrical_doodle.screens.cv2_screens.CV2Screen(
        server.info.device_name.decode()
    )

    decoder.sinks.append(screen.frame_sink)
    screen_task = asyncio.create_task(screen.run())

    decoder_task = asyncio.create_task(decoder.run())
    demuxer.sinks.append(decoder.packet_sink)

    demuxer_task = asyncio.create_task(demuxer.run())

    aws = [
        controller_task, screen_task, decoder_task, demuxer_task,
        server_process.wait()
    ]

    await asyncio.gather(*aws)


async def main():
    # print(
    #     f'scrcpy {symmetrical_doodle.config.SCRCPY_VERSION} <https://github.com/Genymobile/scrcpy>'
    # )

    options = symmetrical_doodle.cli.parse_args()

    await scrcpy(
        options.server_path,
        serial=options.serial,
        tcpip=options.tcpip,
        tcpip_dst=options.tcpip_dst,
        select_usb=options.select_usb,
        select_tcpip=options.select_tcpip,
        crop=options.crop,
        codec_options=options.codec_options,
        encoder_name=options.encoder_name,
        log_level=options.log_level,
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
