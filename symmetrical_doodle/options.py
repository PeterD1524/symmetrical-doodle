import dataclasses
import enum
from typing import Optional

import symmetrical_doodle.config


class LogLevel(enum.Enum):
    VERBOSE = 0
    DEBUG = enum.auto()
    INFO = enum.auto()
    WARN = enum.auto()
    ERROR = enum.auto()

    def to_server_string(self):
        return self.name.lower()


class RecordFormat(enum.Enum):
    AUTO = 0
    MP4 = enum.auto()
    MKV = enum.auto()


class LockVideoOrientation(enum.Enum):
    UNLOCKED = -1
    # lock the current orientation when scrcpy starts
    INITIAL = -2
    ZERO = 0
    ONE = enum.auto()
    TWO = enum.auto()
    THREE = enum.auto()


class KeyboardInputMode(enum.Enum):
    INJECT = 0
    HID = enum.auto()


class MouseInputMode(enum.Enum):
    INJECT = 0
    HID = enum.auto()


class KeyInjectMode(enum.Enum):
    MIXED = 0
    """Inject special keys, letters and space as key events.

    Inject numbers and punctuation as text events.

    This is the default mode.
    """
    TEXT = enum.auto()
    """Inject special keys as key events.

    Inject letters and space, numbers and punctuation as text events.
    """
    RAW = enum.auto()
    """Inject everything as key events."""


MAX_SHORTCUT_MODS = 8


class ShortcutMod(enum.IntFlag):
    LCTRL = 1 << 0
    RCTRL = 1 << 1
    LALT = 1 << 2
    RALT = 1 << 3
    LSUPER = 1 << 4
    RSUPER = 1 << 5


@dataclasses.dataclass
class ShortcutMods:
    data: tuple[ShortcutMod, ...]


WINDOW_POSITION_UNDEFINED = -0x8000


@dataclasses.dataclass
class Options:
    server_path: str
    serial: Optional[str] = None
    crop: Optional[str] = None
    record_filename: Optional[str] = None
    window_title: Optional[str] = None
    push_target: Optional[str] = '/sdcard/Download/'
    render_driver: Optional[str] = None
    codec_options: Optional[str] = None
    encoder_name: Optional[str] = None
    v4l2_device: Optional[str] = None
    log_level: LogLevel = LogLevel.INFO
    record_format: RecordFormat = RecordFormat.AUTO
    keyboard_input_mode: KeyboardInputMode = KeyboardInputMode.INJECT
    mouse_input_mode: MouseInputMode = MouseInputMode.INJECT
    port: Optional[int] = None
    tunnel_host: Optional[str] = None
    tunnel_port: int = 0
    shortcut_mods: ShortcutMods = dataclasses.field(
        default_factory=lambda:
        ShortcutMods(data=(ShortcutMod.LALT, ShortcutMod.LSUPER))
    )
    max_size: int = 0
    bit_rate: int = symmetrical_doodle.config.DEFAULT_BIT_RATE
    max_fps: int = 0
    lock_video_orientation: LockVideoOrientation = LockVideoOrientation.UNLOCKED
    rotation: int = 0
    window_x: int = WINDOW_POSITION_UNDEFINED
    window_y: int = WINDOW_POSITION_UNDEFINED
    window_width: int = 0
    window_height: int = 0
    display_id: int = 0
    display_buffer: int = 0
    v4l2_buffer: int = 0
    otg: bool = False
    show_touches: bool = False
    fullscreen: bool = False
    always_on_top: bool = False
    control: bool = True
    display: bool = True
    turn_screen_off: bool = False
    key_inject_mode: KeyInjectMode = KeyInjectMode.MIXED
    window_borderless: bool = False
    mipmaps: bool = True
    stay_awake: bool = False
    force_adb_forward: bool = False
    disable_screensaver: bool = False
    forward_key_repeat: bool = True
    forward_all_clicks: bool = False
    legacy_paste: bool = False
    power_off_on_close: bool = False
    clipboard_autosync: bool = True
    downsize_on_error: bool = True
    tcpip_dst: Optional[str] = None
    select_usb: bool = False
    select_tcpip: bool = False
    cleanup: bool = True
    start_fps_counter: bool = False
