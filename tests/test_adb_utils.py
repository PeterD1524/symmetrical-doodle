import pytest

import symmetrical_doodle.adb.utils


@pytest.mark.parametrize(
    'output,expected', [
        (
            b'192.168.1.0/24  proto kernel  scope link  src 192.168.12.34\r\r\n',
            b'192.168.12.34'
        ),
        (
            b'192.168.1.0/24  proto kernel  scope link  src 192.168.12.34',
            b'192.168.12.34'
        ),
        (
            b'192.168.1.0/24  proto kernel  scope link  src 192.168.12.34 \n',
            b'192.168.12.34'
        )
    ]
)
def test_parse_device_ip_from_output(output: bytes, expected: bytes):
    ip = symmetrical_doodle.adb.utils.parse_device_ip_from_output(output)
    assert ip == expected
