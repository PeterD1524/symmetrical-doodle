import enum


class LogLevel(enum.Enum):
    VERBOSE = 0
    DEBUG = enum.auto()
    INFO = enum.auto()
    WARN = enum.auto()
    ERROR = enum.auto()

    def to_server_string(self):
        return self.name.lower()


class LockVideoOrientation(enum.Enum):
    UNLOCKED = -1
    # lock the current orientation when scrcpy starts
    INITIAL = -2
    zero = 0
    one = enum.auto()
    two = enum.auto()
    three = enum.auto()
