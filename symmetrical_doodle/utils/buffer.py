def write16be(buf: bytearray, value: int):
    buf.extend(value.to_bytes(2, 'big'))


def write32be(buf: bytearray, value: int):
    buf.extend(value.to_bytes(4, 'big'))


def write64be(buf: bytearray, value: int):
    buf.extend(value.to_bytes(8, 'big'))


def read32be(buf: bytes, start: int):
    buf = buf[start:start + 4]
    assert len(buf) == 4
    value = int.from_bytes(buf, 'big')
    return value, start + 4


def read64be(buf: bytes, start: int):
    buf = buf[start:start + 8]
    assert len(buf) == 8
    value = int.from_bytes(buf, 'big')
    return value, start + 8
