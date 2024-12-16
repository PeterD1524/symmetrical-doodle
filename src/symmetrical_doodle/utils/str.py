def str_utf8_truncation_index(utf8: bytes, max_len: int):
    if len(utf8) <= max_len:
        return len(utf8)
    length = max_len
    while utf8[length] & 0x80 != 0 and utf8[length] & 0xc0 != 0xc0:
        length -= 1
    return length


def parse_integer_with_suffix(s: str):
    mul = 1
    try:
        value = int(s, base=0)
    except ValueError:
        s = s.rstrip()
        try:
            suffix = s[-1]
        except IndexError:
            raise ValueError
        if suffix in 'Mm':
            mul = 1000000
        elif suffix in 'Kk':
            mul = 1000
        else:
            raise ValueError
        value = int(s[:-1], base=0)
    return value * mul
