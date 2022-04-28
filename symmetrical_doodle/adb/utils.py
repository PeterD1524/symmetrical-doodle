import asyncio.subprocess
from typing import Optional

import symmetrical_doodle.adb


def is_tcpip_serial(serial: bytes):
    # Emulators are localhost TCP/IP devices.
    # There is no ':' in emulator serials.
    return b':' in serial


async def prepare_adb(
    adb: symmetrical_doodle.adb.ADB, serial: Optional[str],
    tcpip_dst: Optional[str], select_usb: bool, select_tcpip: bool
):
    process = await adb.start_server()
    assert not await process.wait()

    # At most one of the 4 following parameters may be set
    assert sum(
        [serial is not None, select_usb, select_tcpip, tcpip_dst is not None]
    ) <= 1

    # A device must be selected via a serial in all cases except when --tcpip=
    # is called with a parameter (in that case, the device may initially not
    # exist, and scrcpy will execute "adb connect").
    need_initial_serial = tcpip_dst is None

    if need_initial_serial:
        if serial is not None:
            adb.serial = serial
        elif select_usb:
            adb.use_usb_device(True)
        elif select_tcpip:
            adb.use_tcpip_device(True)
        else:
            adb.use_usb_device(False)
            adb.use_tcpip_device(False)
            del adb.serial
            del adb.transport_id
        serial = (await adb.get_serialno()).decode()
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
        serial = result[len(b'connected to '):].decode()

    adb.serial = serial


async def get_device_ip(adb: symmetrical_doodle.adb.ADB):
    process = await adb.run_command(
        ['shell', 'ip', 'route', 'show', 'dev', 'wlan0'],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await process.communicate()
    assert not process.returncode
    return parse_device_ip_from_output(stdout)


def parse_device_ip_from_output(s: bytes):
    lines = s.splitlines()
    assert len(lines) == 1 or (len(lines) == 2 and lines[1] == b'')
    return lines[0].split()[6]
