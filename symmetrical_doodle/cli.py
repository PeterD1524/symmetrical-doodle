import argparse
from typing import Optional

import symmetrical_doodle.config
import symmetrical_doodle.options
import symmetrical_doodle.utils.str


def parse_bit_rate(s: str):
    value = symmetrical_doodle.utils.str.parse_integer_with_suffix(s)
    return value


def parse_record_format(s: str):
    if s == 'mp4':
        return symmetrical_doodle.options.RecordFormat.MP4
    elif s == 'mkv':
        return symmetrical_doodle.options.RecordFormat.MKV
    raise ValueError


def parse_lock_video_orientation(s: Optional[str]):
    if s is None or s == 'initial':
        return symmetrical_doodle.options.LockVideoOrientation.INITIAL
    if s == 'unlocked':
        return symmetrical_doodle.options.LockVideoOrientation.UNLOCKED
    if s == '0':
        return symmetrical_doodle.options.LockVideoOrientation.ZERO
    if s == '1':
        return symmetrical_doodle.options.LockVideoOrientation.ONE
    if s == '2':
        return symmetrical_doodle.options.LockVideoOrientation.TWO
    if s == '3':
        return symmetrical_doodle.options.LockVideoOrientation.THREE
    raise ValueError


def parse_port_range(s: str):
    first, sep, last = s.partition(':')
    first = int(first, base=0)
    if not sep:
        return first
    last = int(last, base=0)
    return first, last


def parse_log_level(s: str):
    if s == 'verbose':
        return symmetrical_doodle.options.LogLevel.VERBOSE
    if s == 'debug':
        return symmetrical_doodle.options.LogLevel.DEBUG
    if s == 'info':
        return symmetrical_doodle.options.LogLevel.INFO
    if s == 'warn':
        return symmetrical_doodle.options.LogLevel.WARN
    if s == 'error':
        return symmetrical_doodle.options.LogLevel.ERROR
    raise ValueError


def parse_window_position(s: str):
    if s == 'auto':
        return symmetrical_doodle.options.WINDOW_POSITION_UNDEFINED
    value = int(s, base=0)
    if value == symmetrical_doodle.options.WINDOW_POSITION_UNDEFINED:
        raise ValueError
    return ValueError


def parse_shortcut_mods_item(s: str):
    item = 0
    for mod in s.split('+'):
        if mod == 'lctrl':
            item |= symmetrical_doodle.options.ShortcutMod.LCTRL
        elif mod == 'rctrl':
            item |= symmetrical_doodle.options.ShortcutMod.RCTRL
        elif mod == 'lalt':
            item |= symmetrical_doodle.options.ShortcutMod.LALT
        elif mod == 'ralt':
            item |= symmetrical_doodle.options.ShortcutMod.RALT
        elif mod == 'lsuper':
            item |= symmetrical_doodle.options.ShortcutMod.LSUPER
        elif mod == 'rsuper':
            item |= symmetrical_doodle.options.ShortcutMod.RSUPER
        else:
            raise ValueError
    if item == 0:
        raise ValueError
    return item


def parse_shortcut_mods(s: str):
    data = tuple(parse_shortcut_mods_item(mod) for mod in s.split(','))
    return symmetrical_doodle.options.ShortcutMods(data)


def guess_record_format(filename: str):
    if len(filename) < 4:
        raise ValueError
    ext = filename[-4:]
    if ext == '.mp4':
        return symmetrical_doodle.options.RecordFormat.MP4
    if ext == '.mkv':
        return symmetrical_doodle.options.RecordFormat.MKV
    raise ValueError


def get_parser():
    options_default = symmetrical_doodle.options.Options(None)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--always-on-top',
        action='store_true',
        help='Make scrcpy window always on top (above other windows).'
    )
    parser.add_argument(
        '-b',
        '--bit-rate',
        default=options_default.bit_rate,
        help=
        "Encode the video at the gitven bit-rate, expressed in bits/s. Unit suffixes are supported: 'K' (x1000) and 'M' (x1000000). Default is %(default)s.",
        metavar='value'
    )
    parser.add_argument(
        '--codec-options',
        help=
        "Set a list of comma-separated key:type=value options for the device encoder. The possible values for 'type' are 'int' (default), 'long', 'float' and 'string'. The list of possible codec options is available in the Android documentation: <https://d.android.com/reference/android/media/MediaFormat>",
        metavar='key[:type]=value[,...]'
    )
    parser.add_argument(
        '--crop',
        help=
        'Crop the device screen on the server. The values are expressed in the device natural orientation (typically, portrait for a phone, landscape for a tablet). Any --max-size value is computed on the cropped size.',
        metavar='width:height:x:y'
    )
    parser.add_argument(
        '-d',
        '--select-usb',
        action='store_true',
        help=
        'Use USB device (if there is exactly one, like adb -d). Also see -e (--select-tcpip).'
    )
    parser.add_argument(
        '--disable-screensaver',
        action='store_true',
        help='Disable screensaver while scrcpy is running.'
    )
    parser.add_argument(
        '--display',
        default=options_default.display_id,
        type=int,
        help=
        'Specify the display id to mirror. The list of possible display ids can be listed by: adb shell dumpsys display (search "mDisplayId=" in the output). Default is %(default)s.',
        metavar='id'
    )
    parser.add_argument(
        '--display-buffer',
        default=options_default.display_buffer,
        type=int,
        help=
        'Add a buffering delay (in milliseconds) before displaying. This increases latency to compensate for jitter. Default is %(default)s (no buffering).',
        metavar='ms'
    )
    parser.add_argument(
        '-e',
        '--select-tcpip',
        action='store_true',
        help=
        'Use TCP/IP device (if there is exactly one, like adb -e). Also see -d (--select-usb).'
    )
    parser.add_argument(
        '--encoder',
        help='Use a specific MediaCodec encoder (must be a H.264 encoder).',
        metavar='name'
    )
    parser.add_argument(
        '--force-adb-forward',
        action='store_true',
        help='Do not attempt to use "adb reverse" to connect to the device.'
    )
    parser.add_argument(
        '--forward-all-clicks',
        action='store_true',
        help=
        'By default, right-click triggers BACK (or POWER on) and middle-click triggers HOME. This option disables these shortcuts and forwards the clicks to the device instead.'
    )
    parser.add_argument(
        '-f', '--fullscreen', action='store_true', help='Start in fullscreen.'
    )
    parser.add_argument(
        '-K',
        '--hid-keyboard',
        action='store_true',
        help=
        'Simulate a physical keyboard by using HID over AOAv2. It provides a better experience for IME users, and allows to generate non-ASCII characters, contrary to the default injection method. It may only work over USB. The keyboard layout must be configured (once and for all) on the device, via Settings -> System -> Languages and input -> Physical keyboard. This settings page can be started directly: `adb shell am start -a android.settings.HARD_KEYBOARD_SETTINGS`. However, the option is only available when the HID keyboard is enabled (or a physical keyboard is connected). Also see --hid-mouse.'
    )
    parser.add_argument(
        '--legacy-paste',
        action='store_true',
        help=
        'Inject computer clipboard text as a sequence of key events on Ctrl+v (like MOD+Shift+v). This is a workaround for some devices not behaving as expected when setting the device clipboard programmatically.'
    )
    parser.add_argument(
        '--lock-video-orientation',
        nargs='?',
        default=options_default.lock_video_orientation.name.lower(),
        help=
        'Lock video orientation to value. Possible values are "unlocked", "initial" (locked to the initial orientation), 0, 1, 2 and 3. Natural device orientation is 0, and each increment adds a 90 degrees rotation counterclockwise. Default is "%(default)s". Passing the option without argument is equivalent to passing "initial".',
        metavar='value'
    )
    parser.add_argument(
        '--max-fps',
        default=options_default.max_fps,
        type=int,
        help=
        'Limit the frame rate of screen capture (officially supported since Android 10, but may work on earlier versions).',
        metavar='value'
    )
    parser.add_argument(
        '-M',
        '--hid-mouse',
        action='store_true',
        help=
        'Simulate a physical mouse by using HID over AOAv2. In this mode, the computer mouse is captured to control the device directly (relative mouse mode). LAlt, LSuper or RSuper toggle the capture mode, to give control of the mouse back to the computer. It may only work over USB. Also see --hid-keyboard.'
    )
    parser.add_argument(
        '-m',
        '--max-size',
        default=options_default.max_size,
        type=int,
        help=
        'Limit both the width and height of the video to value. The other dimension is computed so that the device aspect-ratio is preserved. Default is %(default)s (unlimited).',
        metavar='value'
    )
    parser.add_argument(
        '--no-cleanup',
        action='store_true',
        help=
        'By default, scrcpy removes the server binary from the device and restores the device state (show touches, stay awake and power mode) on exit. This option disables this cleanup.'
    )
    parser.add_argument(
        '--no-clipboard-autosync',
        action='store_true',
        help=
        'By default, scrcpy automatically synchronizes the computer clipboard to the device clipboard before injecting Ctrl+v, and the device clipboard to the computer clipboard whenever it changes. This option disables this automatic synchronization.'
    )
    parser.add_argument(
        '--no-downsize-on-error',
        action='store_true',
        help=
        'By default, on MediaCodec error, scrcpy automatically tries again with a lower definition. This option disables this behavior.'
    )
    parser.add_argument(
        '-n',
        '--no-control',
        action='store_true',
        help='Disable device control (mirror the device in read-only).'
    )
    parser.add_argument(
        '-N',
        '--no-display',
        action='store_true',
        help=
        'Do not display device (only when screen recording or V4L2 sink is enabled).'
    )
    parser.add_argument(
        '--no-key-repeat',
        action='store_true',
        help='Do not forward repeated key events when a key is held down.'
    )
    parser.add_argument(
        '--no-mipmaps',
        action='store_true',
        help=
        'If the renderer is OpenGL 3.0+ or OpenGL ES 2.0+, then mipmaps are automatically generated to improve downscaling quality. This option disables the generation of mipmaps.'
    )
    parser.add_argument(
        '--otg',
        action='store_true',
        help=
        'Run in OTG mode: simulate physical keyboard and mouse, as if the computer keyboard and mouse were plugged directly to the device via an OTG cable. In this mode, adb (USB debugging) is not necessary, and mirroring is disabled. LAlt, LSuper or RSuper toggle the mouse capture mode, to give control of the mouse back to the computer. If any of --hid-keyboard or --hid-mouse is set, only enable keyboard or mouse respectively, otherwise enable both. It may only work over USB. See --hid-keyboard and --hid-mouse.'
    )
    parser.add_argument(
        '-p',
        '--port',
        default=
        f'{options_default.port_range[0]}:{options_default.port_range[1]}',
        help=
        'Set the TCP port (range) used by the client to listen. Default is %(default)s.',
        metavar='port[:port]'
    )
    parser.add_argument(
        '--power-off-on-close',
        action='store_true',
        help='Turn the device screen off when closing scrcpy.'
    )
    parser.add_argument(
        '--prefer-text',
        action='store_true',
        help=
        'Inject alpha characters and space as text events instead of key events. This avoids issues when combining multiple keys to enter a special character, but breaks the expected behavior of alpha keys in games (typically WASD).'
    )
    parser.add_argument(
        '--print-fps',
        action='store_true',
        help=
        'Start FPS counter, to print framerate logs to the console. It can be started or stopped at any time with MOD+i.'
    )
    parser.add_argument(
        '--push-target',
        default=options_default.push_target,
        help=
        'Set the target directory for pushing files to the device by drag & drop. It is passed as is to "adb push". Default is "%(default)s".',
        metavar='path'
    )
    parser.add_argument(
        '--raw-key-events',
        action='store_true',
        help='Inject key events for all input keys, and ignore text events.'
    )
    parser.add_argument(
        '-r',
        '--record',
        help=
        'Record screen to file. The format is determined by the --record-format option if set, or by the file extension (.mp4 or .mkv).',
        metavar='file.mp4'
    )
    parser.add_argument(
        '--record-format',
        default=options_default.record_format,
        help='Force recording format (either mp4 or mkv).',
        metavar='format'
    )
    parser.add_argument(
        '--render-driver',
        help=
        'Request SDL to use the given render driver (this is just a hint). Supported names are currently "direct3d", "opengl", "opengles2", "opengles", "metal" and "software". <https://wiki.libsdl.org/SDL_HINT_RENDER_DRIVER>',
        metavar='name'
    )
    parser.add_argument(
        '--rotation',
        choices=range(4),
        help=
        'Set the initial display rotation. Possible values are 0, 1, 2 and 3. Each increment adds a 90 degrees rotation counterclockwise.',
        metavar='value'
    )
    parser.add_argument(
        '-s',
        '--serial',
        help=
        'The device serial number. Mandatory only if several devices are connected to adb.',
        metavar='serial'
    )
    parser.add_argument(
        '--shortcut-mod',
        default=','.join(
            shortcut_mod.name.lower()
            for shortcut_mod in options_default.shortcut_mods.data
        ),
        help=
        'Specify the modifiers to use for scrcpy shortcuts. Possible keys are "lctrl", "rctrl", "lalt", "ralt", "lsuper" and "rsuper". A shortcut can consist in several keys, separated by \'+\'. Several shortcuts can be specified, separated by \',\'. For example, to use either LCtrl+LAlt or LSuper for scrcpy shortcuts, pass "lctrl+lalt,lsuper". Default is "%(default)s" (left-Alt or left-Super).',
        metavar='key[+...][,...]'
    )
    parser.add_argument(
        '-S',
        '--turn-screen-off',
        action='store_true',
        help='Turn the device screen off immediately.'
    )
    parser.add_argument(
        '-t',
        '--show-touches',
        action='store_true',
        help=
        'Enable "show touches" on start, restore the initial value on exit. It only shows physical touches (not clicks from scrcpy).'
    )
    parser.add_argument(
        '--tcpip',
        nargs='?',
        default=argparse.SUPPRESS,
        help=
        'Configure and reconnect the device over TCP/IP. If a destination address is provided, then scrcpy connects to this address before starting. The device must listen on the given TCP port (default is 5555). If no destination address is provided, then scrcpy attempts to find the IP address of the current device (typically connected over USB), enables TCP/IP mode, then connects to this address before starting.',
        metavar='ip[:port]'
    )
    parser.add_argument(
        '--tunnel-host',
        help=
        'Set the IP address of the adb tunnel to reach the scrcpy server. This option automatically enables --force-adb-forward. Default is localhost.',
        metavar='ip'
    )
    parser.add_argument(
        '--tunnel-port',
        default=options_default.tunnel_port,
        type=int,
        help=
        'Set the TCP port of the adb tunnel to reach the scrcpy server. This option automatically enables --force-adb-forward. Default is %(default)s (not forced): the local port used for establishing the tunnel will be used.'
    )
    parser.add_argument(
        '--v4l2-sink',
        metavar='/dev/videoN',
        help=
        'Output to v4l2loopback device. It requires to lock the video orientation (see --lock-video-orientation). This feature is only available on Linux.'
    )
    parser.add_argument(
        '--v4l2-buffer',
        default=options_default.v4l2_buffer,
        type=int,
        help=
        'Add a buffering delay (in milliseconds) before pushing frames. This increases latency to compensate for jitter. This option is similar to --display-buffer, but specific to V4L2 sink. Default is %(default)s (no buffering). This option is only available on Linux.',
        metavar='ms'
    )
    parser.add_argument(
        '-V',
        '--verbosity',
        default=options_default.log_level.name.lower(),
        help=
        'Set the log level (verbose, debug, info, warn or error). Default is %(default)s.',
        metavar='value'
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        help='Print the version of scrcpy.',
        version=symmetrical_doodle.config.SCRCPY_VERSION
    )
    parser.add_argument(
        '-w',
        '--stay-awake',
        action='store_true',
        help=
        'Keep the device on while scrcpy is running, when the device is plugged in.'
    )
    parser.add_argument(
        '--window-borderless',
        action='store_true',
        help='Disable window decorations (display borderless window).'
    )
    parser.add_argument(
        '--window-title', help='Set a custom window title.', metavar='text'
    )
    window_x_default = options_default.window_x
    if window_x_default == symmetrical_doodle.options.WINDOW_POSITION_UNDEFINED:
        window_x_default = 'auto'
    parser.add_argument(
        '--window-x',
        default=window_x_default,
        help=
        'Set the initial window horizontal position. Default is "%(default)s".',
        metavar='value'
    )
    window_y_default = options_default.window_y
    if window_y_default == symmetrical_doodle.options.WINDOW_POSITION_UNDEFINED:
        window_y_default = 'auto'
    parser.add_argument(
        '--window-y',
        default=window_y_default,
        help=
        'Set the initial window vertical position. Default is "%(default)s".',
        metavar='value'
    )
    parser.add_argument(
        '--window-width',
        default=options_default.window_width,
        type=int,
        help=
        'Set the initial window width. Default is %(default)s (automatic).',
        metavar='value'
    )
    parser.add_argument(
        '--window-height',
        default=options_default.window_height,
        type=int,
        help=
        'Set the initial window height. Default is %(default)s (automatic).',
        metavar='value'
    )

    parser.add_argument('--server', required=True, metavar='path')
    return parser


def parse_args(args=None):
    args = get_parser().parse_args(args=args)

    kwargs = {}

    bit_rate = args.bit_rate
    if not isinstance(bit_rate, int):
        bit_rate = parse_bit_rate(bit_rate)
    assert 0 <= bit_rate <= 0x7fffffff

    display_id = args.display
    assert 0 <= display_id <= 0x7fffffff

    record_format = args.record_format
    if not isinstance(record_format, symmetrical_doodle.options.RecordFormat):
        record_format = parse_record_format(record_format)

    if args.hid_keyboard:
        kwargs['keyboard_input_mode'
               ] = symmetrical_doodle.options.KeyboardInputMode.HID

    max_fps = args.max_fps
    assert 0 <= max_fps <= 1000

    max_size = args.max_size
    assert 0 <= max_size <= 0xffff

    if args.hid_mouse:
        kwargs['mouse_input_mode'
               ] = symmetrical_doodle.options.MouseInputMode.HID

    lock_video_orientation = parse_lock_video_orientation(
        args.lock_video_orientation
    )

    port_range = parse_port_range(args.port)

    log_level = parse_log_level(args.verbosity)

    window_x = parse_window_position(args.window_x)
    assert -0x7fff <= window_x <= 0x7fff or window_x == symmetrical_doodle.options.WINDOW_POSITION_UNDEFINED

    window_y = parse_window_position(args.window_y)
    assert -0x7fff <= window_y <= 0x7fff or window_y == symmetrical_doodle.options.WINDOW_POSITION_UNDEFINED

    window_width = args.window_width
    assert 0 <= window_width <= 0xffff

    window_height = args.window_height
    assert 0 <= window_height <= 0xffff

    prefer_text = args.prefer_text
    raw_key_events = args.raw_key_events
    assert not (prefer_text and raw_key_events)
    if prefer_text:
        kwargs['key_inject_mode'
               ] = symmetrical_doodle.options.KeyInjectMode.TEXT
    if raw_key_events:
        kwargs['key_inject_mode'
               ] = symmetrical_doodle.options.KeyInjectMode.RAW

    shortcut_mods = parse_shortcut_mods(args.shortcut_mod)

    display_buffer = args.display_buffer
    assert 0 <= display_buffer <= 0x7fffffff
    display_buffer *= 1000

    try:
        tcpip_dst = args.tcpip
    except AttributeError:
        tcpip = False
        tcpip_dst = None
    else:
        tcpip = True

    v4l2_buffer = args.v4l2_buffer
    assert 0 <= v4l2_buffer <= 0x7fffffff
    v4l2_buffer *= 1000

    select_usb = args.select_usb
    select_tcpip = args.select_tcpip
    serial = args.serial
    assert sum(
        [serial is not None, tcpip_dst is not None, select_tcpip, select_usb]
    ) <= 1

    display = not args.no_display
    record_filename = args.record
    v4l2_device = args.v4l2_sink
    assert not (
        not display and record_filename is None and v4l2_device is None
    )

    downsize_on_error = not args.no_downsize_on_error
    if v4l2_device is not None:
        assert lock_video_orientation != symmetrical_doodle.options.LockVideoOrientation.UNLOCKED
        downsize_on_error = False

    assert not (v4l2_buffer and v4l2_device is None)

    tunnel_host = args.tunnel_host
    tunnel_port = args.tunnel_port
    force_adb_forward = args.force_adb_forward
    if (tunnel_host is not None or tunnel_port) and not force_adb_forward:
        force_adb_forward = True

    assert not (
        record_format != symmetrical_doodle.options.RecordFormat.AUTO
        and record_filename is None
    )

    if record_filename and record_format == symmetrical_doodle.options.RecordFormat.AUTO:
        record_format = guess_record_format(record_filename)

    control = not args.no_control
    turn_screen_off = args.turn_screen_off
    stay_awake = args.stay_awake
    show_touches = args.show_touches
    power_off_on_close = args.power_off_on_close
    if not control:
        assert not turn_screen_off
        assert not stay_awake
        assert not show_touches
        assert not power_off_on_close

    otg = args.otg
    if otg:
        assert record_filename is None
        assert not turn_screen_off
        assert not stay_awake
        assert not show_touches
        assert not power_off_on_close
        assert not display_id
        assert v4l2_device is None

    options = symmetrical_doodle.options.Options(
        args.server,
        bit_rate=bit_rate,
        crop=args.crop,
        display_id=display_id,
        select_usb=args.select_usb,
        select_tcpip=args.select_tcpip,
        fullscreen=args.fullscreen,
        record_format=record_format,
        max_fps=max_fps,
        lock_video_orientation=lock_video_orientation,
        tunnel_host=tunnel_host,
        tunnel_port=tunnel_port,
        control=control,
        display=display,
        port_range=port_range,
        record_filename=record_filename,
        serial=serial,
        turn_screen_off=turn_screen_off,
        show_touches=show_touches,
        always_on_top=args.always_on_top,
        log_level=log_level,
        stay_awake=stay_awake,
        window_title=args.window_title,
        window_x=window_x,
        window_y=window_y,
        window_width=window_width,
        window_height=window_height,
        window_borderless=args.window_borderless,
        push_target=args.push_target,
        rotation=args.rotation,
        render_driver=args.render_driver,
        mipmaps=not args.no_mipmaps,
        forward_key_repeat=not args.no_key_repeat,
        codec_options=args.codec_options,
        encoder_name=args.encoder,
        force_adb_forward=force_adb_forward,
        disable_screensaver=args.disable_screensaver,
        shortcut_mods=shortcut_mods,
        forward_all_clicks=args.forward_all_clicks,
        legacy_paste=args.legacy_paste,
        power_off_on_close=power_off_on_close,
        display_buffer=display_buffer,
        clipboard_autosync=not args.no_clipboard_autosync,
        tcpip=tcpip,
        tcpip_dst=tcpip_dst,
        downsize_on_error=downsize_on_error,
        cleanup=not args.no_cleanup,
        start_fps_counter=args.print_fps,
        otg=otg,
        v4l2_device=v4l2_device,
        **kwargs
    )
    return options


if __name__ == '__main__':
    args = parse_args()
    import dataclasses
    import pprint
    pprint.pprint(dataclasses.asdict(args), sort_dicts=False)
