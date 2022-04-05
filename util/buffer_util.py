def write16be(buf: bytearray, value: int):
    buf.append((value >> 8) & 0xff)
    buf.append(value & 0xff)


def write32be(buf: bytearray, value: int):
    for i in range(4):
        buf.append((value >> (24 - i * 8)) & 0xff)


def write64be(buf: bytearray, value: int):
    write32be(buf, value >> 32)
    write32be(buf, value)


def read32be(buf: bytes, start: int):
    buf = buf[start:]
    value = (buf[0] << 24) | (buf[1] << 16) | (buf[2] << 8) | buf[3]
    return value, start + 4


def read64be(buf: bytes, start: int):
    msb, start = read32be(buf, start)
    lsb, start = read32be(buf, start)
    return (msb << 32) | lsb, start
