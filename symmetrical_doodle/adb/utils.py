import asyncio.subprocess

import symmetrical_doodle.adb


def is_tcpip_serial(serial: bytes):
    # Emulators are localhost TCP/IP devices.
    # There is no ':' in emulator serials.
    return b':' in serial


async def get_device_ip(adb: symmetrical_doodle.adb.ADB):
    process = await adb.run_command(
        ['shell', 'ip', 'route'],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await process.communicate()
    assert not process.returncode
    return parse_device_ip_from_output(stdout)


def parse_device_ip_from_output(s: bytes):
    for line in s.splitlines():
        try:
            ip = parse_device_ip_from_line(line)
        except ValueError:
            continue
        return ip
    raise ValueError


def parse_device_ip_from_line(line: bytes):
    split = line.split()
    try:
        device_name = split[2]
    except IndexError:
        raise ValueError
    try:
        ip = split[8]
    except IndexError:
        raise ValueError
    if not device_name.startswith(b'wlan'):
        raise ValueError
    return ip
