import symmetrical_doodle.device_message


def test_deserialize_clipboard():
    input = b"\x00\x00\x00\x00\x03ABC"

    message, r = symmetrical_doodle.device_message.deserialize(input, 0)
    assert r == 8

    assert isinstance(message, symmetrical_doodle.device_message.ClipBoard)
    assert message.type == symmetrical_doodle.device_message.DeviceMessageType.CLIPBOARD
    assert message.text == b"ABC"


def test_deserialize_clipboard_big():
    text_length = 262139
    input = b"\x00\x00\x03\xff\xfb" + b"a" * text_length

    message, r = symmetrical_doodle.device_message.deserialize(input, 0)
    assert r == 5 + text_length

    assert isinstance(message, symmetrical_doodle.device_message.ClipBoard)
    assert message.type == symmetrical_doodle.device_message.DeviceMessageType.CLIPBOARD
    assert message.text == b"a" * text_length


def test_deserialize_ack_set_clipboard():
    input = b"\x01\x01\x02\x03\x04\x05\x06\x07\x08"

    message, r = symmetrical_doodle.device_message.deserialize(input, 0)
    assert r == 9

    assert isinstance(message, symmetrical_doodle.device_message.ACKClipBoard)
    assert (
        message.type
        == symmetrical_doodle.device_message.DeviceMessageType.ACK_CLIPBOARD
    )
    assert message.sequence == 0x102030405060708
