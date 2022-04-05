import dataclasses
import enum
from typing import Optional

import android.input
import android.keycodes
import util.buffer_util
import util.str
import coords

CONTROL_MSG_MAX_SIZE = 1 << 18

CONTROL_MSG_INJECT_TEXT_MAX_LENGTH = 300
CONTROL_MSG_CLIPBOARD_TEXT_MAX_LENGTH = CONTROL_MSG_MAX_SIZE - 14

POINTER_ID_MOUSE = 0xffffffffffffffff
POINTER_ID_VIRTUAL_FINGER = 0xfffffffffffffffe


class ControlMessageType(enum.Enum):
    INJECT_KEYCODE = 0
    INJECT_TEXT = enum.auto()
    INJECT_TOUCH_EVENT = enum.auto()
    INJECT_SCROLL_EVENT = enum.auto()
    BACK_OR_SCREEN_ON = enum.auto()
    EXPAND_NOTIFICATION_PANEL = enum.auto()
    EXPAND_SETTINGS_PANEL = enum.auto()
    COLLAPSE_PANELS = enum.auto()
    GET_CLIPBOARD = enum.auto()
    SET_CLIPBOARD = enum.auto()
    SET_SCREEN_POWER_MODE = enum.auto()
    ROTATE_DEVICE = enum.auto()


class ScreenPowerMode(enum.Enum):
    # see <https://android.googlesource.com/platform/frameworks/base.git/+/pie-release-2/core/java/android/view/SurfaceControl.java#305>
    SC_SCREEN_POWER_MODE_OFF = 0
    SC_SCREEN_POWER_MODE_NORMAL = 2


class CopyKey(enum.Enum):
    NONE = 0
    COPY = enum.auto()
    CUT = enum.auto()


def write_position(buf: bytearray, position: coords.Position):
    util.buffer_util.write32be(buf, position.point.x)
    util.buffer_util.write32be(buf, position.point.y)
    util.buffer_util.write16be(buf, position.screen_size.width)
    util.buffer_util.write16be(buf, position.screen_size.height)


def write_string(buf: bytearray, utf8: bytes, max_len: int):
    length = util.str.str_utf8_truncation_index(utf8, max_len)
    util.buffer_util.write32be(buf, length)
    buf.extend(utf8[:length])


def to_fixed_point_16(f: float):
    assert f >= 0.0 and f <= 1.0
    u = int(f * 65536.0)
    if u >= 0xffff:
        u = 0xffff
    return u & 0xffff


@dataclasses.dataclass
class ControlMessage:
    type: ControlMessageType = dataclasses.field(init=False)

    def get_buf(self):
        return bytearray([self.type.value])

    def serialize(self):
        return self.get_buf()


@dataclasses.dataclass
class InjectKeycode(ControlMessage):
    type = ControlMessageType.INJECT_KEYCODE
    action: android.input.KeyEventAction
    keycode: android.keycodes.Keycode
    repeat: int
    meta_state: android.input.MetaState

    def serialize(self):
        buf = self.get_buf()
        buf.append(self.action.value)
        util.buffer_util.write32be(buf, self.keycode.value)
        util.buffer_util.write32be(buf, self.repeat)
        util.buffer_util.write32be(buf, self.meta_state.value)
        return buf


@dataclasses.dataclass
class InjectText(ControlMessage):
    type = ControlMessageType.INJECT_TEXT
    text: bytes

    def serialize(self):
        buf = self.get_buf()
        write_string(buf, self.text, CONTROL_MSG_INJECT_TEXT_MAX_LENGTH)
        return buf


@dataclasses.dataclass
class InjectTouchEvent(ControlMessage):
    type = ControlMessageType.INJECT_TOUCH_EVENT
    action: android.input.MotionEventAction
    buttons: int
    pointer_id: int
    position: coords.Position
    pressure: float

    def serialize(self):
        buf = self.get_buf()
        buf.append(self.action.value)
        util.buffer_util.write64be(buf, self.pointer_id)
        write_position(buf, self.position)
        pressure = to_fixed_point_16(self.pressure)
        util.buffer_util.write16be(buf, pressure)
        util.buffer_util.write32be(buf, self.buttons)
        return buf


@dataclasses.dataclass
class InjectScrollEvent(ControlMessage):
    type = ControlMessageType.INJECT_SCROLL_EVENT
    position: coords.Position
    hscroll: int
    vscroll: int
    button: android.input.MotionEventButton

    def serialize(self):
        buf = self.get_buf()
        write_position(buf, self.position)
        util.buffer_util.write32be(buf, self.hscroll)
        util.buffer_util.write32be(buf, self.vscroll)
        util.buffer_util.write32be(buf, self.button.value)
        return buf


@dataclasses.dataclass
class BackOrScreenOn(ControlMessage):
    type = ControlMessageType.BACK_OR_SCREEN_ON
    action: android.input.KeyEventAction

    def serialize(self):
        buf = self.get_buf()
        buf.append(self.action.value)
        return buf


@dataclasses.dataclass
class GetClipboard(ControlMessage):
    type = ControlMessageType.GET_CLIPBOARD
    copy_key: CopyKey

    def serialize(self):
        buf = self.get_buf()
        buf.append(self.copy_key.value)
        return buf


@dataclasses.dataclass
class SetClipboard(ControlMessage):
    type = ControlMessageType.SET_CLIPBOARD
    sequence: int
    text: bytes
    paste: bool

    def serialize(self):
        buf = self.get_buf()
        util.buffer_util.write64be(buf, self.sequence)
        buf.append(self.paste)
        write_string(buf, self.text, CONTROL_MSG_CLIPBOARD_TEXT_MAX_LENGTH)
        return buf


@dataclasses.dataclass
class SetScreenPowerMode(ControlMessage):
    type = ControlMessageType.SET_SCREEN_POWER_MODE
    mode: ScreenPowerMode

    def serialize(self):
        buf = self.get_buf()
        buf.append(self.mode.value)
        return buf


@dataclasses.dataclass
class ExpandNotificationPanel(ControlMessage):
    type = ControlMessageType.EXPAND_NOTIFICATION_PANEL


@dataclasses.dataclass
class ExpandSettingsPanel(ControlMessage):
    type = ControlMessageType.EXPAND_SETTINGS_PANEL


@dataclasses.dataclass
class CollapsePanels(ControlMessage):
    type = ControlMessageType.COLLAPSE_PANELS


@dataclasses.dataclass
class RotateDevice(ControlMessage):
    type = ControlMessageType.ROTATE_DEVICE
