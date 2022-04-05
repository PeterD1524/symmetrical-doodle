def str_utf8_truncation_index(utf8: bytes, max_len: int):
    if len(utf8) <= max_len:
        return len(utf8)
    length = max_len
    while utf8[length] & 0x80 != 0 and utf8[length] & 0xc0 != 0xc0:
        length -= 1
    return length
