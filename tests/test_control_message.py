import symmetrical_doodle.android.input
import symmetrical_doodle.android.keycodes
import symmetrical_doodle.control_message
import symmetrical_doodle.coords


def test_serialize_inject_keycode():
    message = symmetrical_doodle.control_message.InjectKeycode(
        action=symmetrical_doodle.android.input.KeyEventAction.
        AKEY_EVENT_ACTION_UP,
        keycode=symmetrical_doodle.android.keycodes.Keycode.AKEYCODE_ENTER,
        repeat=5,
        meta_state=symmetrical_doodle.android.input.MetaState.AMETA_SHIFT_ON.
        value
        | symmetrical_doodle.android.input.MetaState.AMETA_SHIFT_LEFT_ON.value
    )
    buf = message.serialize()
    assert buf == b'\x00\x01\x00\x00\x00B\x00\x00\x00\x05\x00\x00\x00A'


def test_serialize_inject_text():
    message = symmetrical_doodle.control_message.InjectText(
        text=b'hello, world!'
    )
    buf = message.serialize()
    assert buf == b'\x01\x00\x00\x00\rhello, world!'


def test_serialize_inject_text_long():
    text_length = symmetrical_doodle.control_message.CONTROL_MSG_INJECT_TEXT_MAX_LENGTH
    text = b'a' * text_length
    message = symmetrical_doodle.control_message.InjectText(text=text)
    buf = message.serialize()
    expected = b'\x01\x00\x00\x01,' + b'a' * text_length
    assert buf == expected


def test_serialize_inject_touch_event():
    message = symmetrical_doodle.control_message.InjectTouchEvent(
        action=symmetrical_doodle.android.input.MotionEventAction.
        AMOTION_EVENT_ACTION_DOWN,
        buttons=symmetrical_doodle.android.input.MotionEventButton.
        AMOTION_EVENT_BUTTON_PRIMARY.value,
        pointer_id=0x1234567887654321,
        position=symmetrical_doodle.coords.Position(
            screen_size=symmetrical_doodle.coords.Size(
                width=1080, height=1920
            ),
            point=symmetrical_doodle.coords.Point(x=100, y=200)
        ),
        pressure=1.0
    )
    buf = message.serialize()
    assert buf == b'\x02\x00\x124Vx\x87eC!\x00\x00\x00d\x00\x00\x00\xc8\x048\x07\x80\xff\xff\x00\x00\x00\x01'


def test_serialize_inject_scroll_event():
    message = symmetrical_doodle.control_message.InjectScrollEvent(
        position=symmetrical_doodle.coords.Position(
            screen_size=symmetrical_doodle.coords.Size(
                width=1080, height=1920
            ),
            point=symmetrical_doodle.coords.Point(x=260, y=1026)
        ),
        hscroll=1,
        vscroll=0xffffffff,
        buttons=1
    )
    buf = message.serialize()
    assert buf == b'\x03\x00\x00\x01\x04\x00\x00\x04\x02\x048\x07\x80\x00\x00\x00\x01\xff\xff\xff\xff\x00\x00\x00\x01'


def test_serialize_back_or_screen_on():
    message = symmetrical_doodle.control_message.BackOrScreenOn(
        action=symmetrical_doodle.android.input.KeyEventAction.
        AKEY_EVENT_ACTION_UP
    )
    buf = message.serialize()
    assert buf == b'\x04\x01'


def test_serialize_expand_notification_panel():
    message = symmetrical_doodle.control_message.ExpandNotificationPanel()
    buf = message.serialize()
    assert buf == b'\x05'


def test_serialize_expand_settings_panel():
    message = symmetrical_doodle.control_message.ExpandSettingsPanel()
    buf = message.serialize()
    assert buf == b'\x06'


def test_serialize_collapse_panels():
    message = symmetrical_doodle.control_message.CollapsePanels()
    buf = message.serialize()
    assert buf == b'\x07'


def test_serialize_get_clipboard():
    message = symmetrical_doodle.control_message.GetClipboard(
        copy_key=symmetrical_doodle.control_message.CopyKey.COPY
    )
    buf = message.serialize()
    assert buf == b'\x08\x01'


def test_serialize_set_clipboard():
    message = symmetrical_doodle.control_message.SetClipboard(
        sequence=0x102030405060708, text=b'hello, world!', paste=True
    )
    buf = message.serialize()
    assert buf == b'\x09\x01\x02\x03\x04\x05\x06\x07\x08\x01\x00\x00\x00\rhello, world!'


def test_serialize_set_clipboard_long():
    text_length = symmetrical_doodle.control_message.CONTROL_MSG_CLIPBOARD_TEXT_MAX_LENGTH
    text = b'a' * text_length
    message = symmetrical_doodle.control_message.SetClipboard(
        sequence=0x102030405060708, text=text, paste=True
    )
    buf = message.serialize()
    expected = b'\x09\x01\x02\x03\x04\x05\x06\x07\x08\x01\x00\x03\xff\xf2' + b'a' * text_length
    assert buf == expected


def test_serialize_set_screen_power_mode():
    message = symmetrical_doodle.control_message.SetScreenPowerMode(
        mode=symmetrical_doodle.control_message.ScreenPowerMode.NORMAL
    )
    buf = message.serialize()
    assert buf == b'\n\x02'


def test_serialize_rotate_device():
    message = symmetrical_doodle.control_message.RotateDevice()
    buf = message.serialize()
    assert buf == b'\x0b'
