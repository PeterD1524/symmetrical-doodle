def assert_not_none[T](o: T | None) -> T:
    assert o is not None
    return o
