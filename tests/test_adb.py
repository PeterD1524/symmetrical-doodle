import pytest

import symmetrical_doodle.adb


@pytest.mark.parametrize(
    'line,transport_id,state,serial,product,model,device,devpath', [
        (
            b'0123456789abcdef       device usb:2-1 product:MyProduct model:MyModel device:MyDevice transport_id:1',
            1, b'device', b'0123456789abcdef', b'MyProduct', b'MyModel',
            b'MyDevice', b'usb:2-1'
        ),
        (
            b'192.168.1.1:5555       device product:MyWifiProduct model:MyWifiModel device:MyWifiDevice transport_id:2',
            2, b'device', b'192.168.1.1:5555', b'MyWifiProduct',
            b'MyWifiModel', b'MyWifiDevice', b''
        )
    ]
)
def test_parse_device(
    line: bytes, transport_id: int, state: bytes, serial: bytes,
    product: bytes, model: bytes, device: bytes, devpath: bytes
):
    transport = symmetrical_doodle.adb.parse_device(line)
    assert isinstance(transport, symmetrical_doodle.adb.Transport)
    assert transport.id == transport_id
    assert transport.state == state
    assert transport.serial == serial
    assert transport.product == product
    assert transport.model == model
    assert transport.device == device
    assert transport.devpath == devpath
