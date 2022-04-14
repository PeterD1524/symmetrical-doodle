import pytest

import symmetrical_doodle.adb.utils


@pytest.mark.parametrize(
    'output,expected', [
        (
            b'192.168.1.0/24 dev wlan0  proto kernel  scope link  src 192.168.12.34\r\r\n',
            b'192.168.12.34'
        ),
        (
            b'192.168.1.0/24 dev wlan0  proto kernel  scope link  src 192.168.12.34',
            b'192.168.12.34'
        ),
        (
            b'192.168.1.0/24 dev wlan0  proto kernel  scope link  src 192.168.12.34 \n',
            b'192.168.12.34'
        ),
        (
            b'192.168.1.0/24 dev wlan0  proto kernel  scope link  src 192.168.1.2\r\n10.0.0.0/24 dev rmnet  proto kernel  scope link  src 10.0.0.2\r\n',
            b'192.168.1.2'
        ),
        (
            b'10.0.0.0/24 dev rmnet  proto kernel  scope link  src 10.0.0.3\r\n192.168.1.0/24 dev wlan0  proto kernel  scope link  src 192.168.1.3\r\n',
            b'192.168.1.3'
        )
    ]
)
def test_parse_device_ip_from_output(output: bytes, expected: bytes):
    ip = symmetrical_doodle.adb.utils.parse_device_ip_from_output(output)
    assert ip == expected


@pytest.mark.parametrize(
    'output', [
        b'192.168.1.0/24 dev rmnet  proto kernel  scope link  src 192.168.12.34\r\r\n',
        b'192.168.1.0/24 dev rmnet  proto kernel  scope link  src 192.168.12.34',
        b'192.168.1.0/24 dev rmnet  proto kernel  scope link  src \n'
    ]
)
def test_parse_device_ip_from_output_value_error(output: bytes):
    with pytest.raises(ValueError):
        symmetrical_doodle.adb.utils.parse_device_ip_from_output(output)
