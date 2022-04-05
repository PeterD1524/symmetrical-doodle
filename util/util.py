import android.input
import control_message
import controllers
import coords


async def turn_screen_off(controller: controllers.Controller):
    message = control_message.SetScreenPowerMode(
        control_message.ScreenPowerMode.SC_SCREEN_POWER_MODE_OFF
    )
    await controller.push_message(message)


# https://android.googlesource.com/platform/frameworks/base/+/android-7.1.1_r22/cmds/input/src/com/android/commands/input/Input.java
def send_tap(controller: controllers.Controller, position: coords.Position):
    message = control_message.InjectTouchEvent(
        action=android.input.MotionEventAction.AMOTION_EVENT_ACTION_DOWN,
        pointer_id=control_message.POINTER_ID_MOUSE,
        position=position,
        pressure=1.0,
        buttons=android.input.MotionEventButton.AMOTION_EVENT_BUTTON_PRIMARY.
        value,
    )
    controller.push_message_nowait(message)
    message = control_message.InjectTouchEvent(
        action=android.input.MotionEventAction.AMOTION_EVENT_ACTION_UP,
        pointer_id=control_message.POINTER_ID_MOUSE,
        position=position,
        pressure=0.0,
        buttons=android.input.MotionEventButton.AMOTION_EVENT_BUTTON_PRIMARY.
        value,
    )
    controller.push_message_nowait(message)
