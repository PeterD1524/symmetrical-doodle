import dataclasses
import enum

import util.buffer_util

DEVICE_MSG_MAX_SIZE = 1 << 18
DEVICE_MSG_TEXT_MAX_LENGTH = DEVICE_MSG_MAX_SIZE - 5


class DeviceMessageType(enum.Enum):
    CLIPBOARD = enum.auto()
    ACK_CLIPBOARD = enum.auto()


class DeserializeError(Exception):
    pass


class NotRecoverable(DeserializeError):
    pass


class NotAvailable(DeserializeError):
    pass


def deserialize(buf: bytes, start: int):
    length = len(buf[start:])
    if length < 5:
        raise NotAvailable

    try:
        type = DeviceMessageType(buf[start])
    except ValueError:
        raise NotRecoverable
    start += 1
    if type is DeviceMessageType.CLIPBOARD:
        clipboard_len, start = util.buffer_util.read32be(buf, start)
        if clipboard_len > length - 5:
            raise NotAvailable
        text = buf[start:start + clipboard_len]
        return ClipBoard(text), start + clipboard_len
    elif type is DeviceMessageType.ACK_CLIPBOARD:
        sequence, start = util.buffer_util.read64be(buf, start)
        return ACKClipBoard(sequence), start
    else:
        raise NotRecoverable


@dataclasses.dataclass
class DeviceMessage:
    type: DeviceMessageType = dataclasses.field(init=False)


@dataclasses.dataclass
class ClipBoard(DeviceMessage):
    type = DeviceMessageType.CLIPBOARD
    text: bytes


@dataclasses.dataclass
class ACKClipBoard(DeviceMessage):
    type = DeviceMessageType.ACK_CLIPBOARD
    sequence: int
