import symmetrical_doodle.android.input
import symmetrical_doodle.control_message
import symmetrical_doodle.controllers
import symmetrical_doodle.coords


async def turn_screen_off(
    controller: symmetrical_doodle.controllers.Controller
):
    message = symmetrical_doodle.control_message.SetScreenPowerMode(
        symmetrical_doodle.control_message.ScreenPowerMode.OFF
    )
    await controller.push_message(message)


# https://android.googlesource.com/platform/frameworks/base/+/android-7.1.1_r22/cmds/input/src/com/android/commands/input/Input.java
def send_tap(
    controller: symmetrical_doodle.controllers.Controller,
    position: symmetrical_doodle.coords.Position
):
    message = symmetrical_doodle.control_message.InjectTouchEvent(
        action=symmetrical_doodle.android.input.MotionEventAction.
        AMOTION_EVENT_ACTION_DOWN,
        pointer_id=symmetrical_doodle.control_message.POINTER_ID_MOUSE,
        position=position,
        pressure=1.0,
        buttons=symmetrical_doodle.android.input.MotionEventButton.
        AMOTION_EVENT_BUTTON_PRIMARY.value,
    )
    controller.push_message_nowait(message)
    message = symmetrical_doodle.control_message.InjectTouchEvent(
        action=symmetrical_doodle.android.input.MotionEventAction.
        AMOTION_EVENT_ACTION_UP,
        pointer_id=symmetrical_doodle.control_message.POINTER_ID_MOUSE,
        position=position,
        pressure=0.0,
        buttons=symmetrical_doodle.android.input.MotionEventButton.
        AMOTION_EVENT_BUTTON_PRIMARY.value,
    )
    controller.push_message_nowait(message)
