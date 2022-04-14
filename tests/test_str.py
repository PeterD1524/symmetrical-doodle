import pytest

import symmetrical_doodle.utils.str


@pytest.mark.parametrize(
    's,expected', [
        ('1234', 1234),
        ('-1234', -1234),
        ('1234k', 1234000),
        ('1234m', 1234000000),
        ('-1234k', -1234000),
        ('-1234m', -1234000000),
        (
            '123456789876543212345678987654321',
            123456789876543212345678987654321
        ),
        ('4611686018427387k', 4611686018427387000),
        ('4611686018427387m', 4611686018427387000000),
        ('-4611686018427387k', -4611686018427387000),
        ('-4611686018427387m', -4611686018427387000000),
    ]
)
def test_parse_integer_with_suffix(s: str, expected: int):
    value = symmetrical_doodle.utils.str.parse_integer_with_suffix(s)
    assert value == expected


@pytest.mark.parametrize(
    'max_len,expected', [
        (1, 1),
        (2, 1),
        (3, 3),
        (4, 4),
        (5, 4),
        (6, 6),
        (7, 7),
        (8, 7),
    ]
)
def test_utf8_truncate(max_len: int, expected: int):
    s = 'aÉbÔc'.encode()
    assert len(s) == 7

    count = symmetrical_doodle.utils.str.str_utf8_truncation_index(s, max_len)
    assert count == expected
