import pytest

import symmetrical_doodle.utils.buffer


@pytest.mark.parametrize(
    'buf,value,expected', [
        (bytearray(), 0xabcd, (0xab, 0xcd)),
        (bytearray(16), 0xabcd, (0xab, 0xcd)),
    ]
)
def test_write16be(buf: bytearray, value: int, expected: tuple[int, int]):
    old_bytes = bytes(buf)
    symmetrical_doodle.utils.buffer.write16be(buf, value)
    assert len(buf) == len(old_bytes) + 2
    assert buf[:-2] == old_bytes
    assert buf[-2] == expected[0]
    assert buf[-1] == expected[1]


@pytest.mark.parametrize(
    'buf,value,expected', [
        (bytearray(), 0xabcd1234, (0xab, 0xcd, 0x12, 0x34)),
    ]
)
def test_write32be(
    buf: bytearray, value: int, expected: tuple[int, int, int, int]
):
    old_bytes = bytes(buf)
    symmetrical_doodle.utils.buffer.write32be(buf, value)
    assert len(buf) == len(old_bytes) + 4
    assert buf[:-4] == old_bytes
    assert buf[-4] == expected[0]
    assert buf[-3] == expected[1]
    assert buf[-2] == expected[2]
    assert buf[-1] == expected[3]


@pytest.mark.parametrize(
    'buf,value,expected', [
        (
            bytearray(), 0xabcd1234567890ef,
            (0xab, 0xcd, 0x12, 0x34, 0x56, 0x78, 0x90, 0xef)
        ),
    ]
)
def test_write64be(
    buf: bytearray, value: int, expected: tuple[int, int, int, int, int, int,
                                                int, int]
):
    old_bytes = bytes(buf)
    symmetrical_doodle.utils.buffer.write64be(buf, value)
    assert len(buf) == len(old_bytes) + 8
    assert buf[:-8] == old_bytes
    assert buf[-8] == expected[0]
    assert buf[-7] == expected[1]
    assert buf[-6] == expected[2]
    assert buf[-5] == expected[3]
    assert buf[-4] == expected[4]
    assert buf[-3] == expected[5]
    assert buf[-2] == expected[6]
    assert buf[-1] == expected[7]


@pytest.mark.parametrize(
    'buf,start,expected', [
        (b'\xab\xcd\x124', 0, (0xabcd1234, 4)),
    ]
)
def test_read32be(buf: bytes, start: int, expected: tuple[int, int]):
    assert symmetrical_doodle.utils.buffer.read32be(buf, start) == expected


@pytest.mark.parametrize(
    'buf,start,expected', [
        (b'\xab\xcd\x124Vx\x90\xef', 0, (0xabcd1234567890ef, 8)),
    ]
)
def test_read64be(buf: bytes, start: int, expected: tuple[int, int]):
    assert symmetrical_doodle.utils.buffer.read64be(buf, start) == expected
