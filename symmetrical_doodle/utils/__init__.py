import asyncio
import time

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
    await controller.send_message(message)


def lerp(a: float, b: float, alpha: float):
    return (b - a) * alpha + a


def run_tap():
    pass


# https://android.googlesource.com/platform/frameworks/base/+/android-7.1.1_r22/cmds/input/src/com/android/commands/input/Input.java
async def send_tap(
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
    await controller.send_message(message)
    message = symmetrical_doodle.control_message.InjectTouchEvent(
        action=symmetrical_doodle.android.input.MotionEventAction.
        AMOTION_EVENT_ACTION_UP,
        pointer_id=symmetrical_doodle.control_message.POINTER_ID_MOUSE,
        position=position,
        pressure=0.0,
        buttons=symmetrical_doodle.android.input.MotionEventButton.
        AMOTION_EVENT_BUTTON_PRIMARY.value,
    )
    await controller.send_message(message)


async def send_swipe_bad(
    controller: symmetrical_doodle.controllers.Controller,
    screen_size: symmetrical_doodle.coords.Size,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    duration: float = 0.3,
    interval: float = 0.005,
):
    down = time.time()
    message = symmetrical_doodle.control_message.InjectTouchEvent(
        action=symmetrical_doodle.android.input.MotionEventAction.
        AMOTION_EVENT_ACTION_DOWN,
        pointer_id=symmetrical_doodle.control_message.POINTER_ID_MOUSE,
        position=symmetrical_doodle.coords.Position(
            screen_size, symmetrical_doodle.coords.Point(x1, y1)
        ),
        pressure=1.0,
        buttons=symmetrical_doodle.android.input.MotionEventButton.
        AMOTION_EVENT_BUTTON_PRIMARY.value,
    )
    await controller.send_message(message)
    end_time = down + duration
    now = time.time()
    while now < end_time:
        elapsed_time = now - down
        alpha = elapsed_time / duration
        message = symmetrical_doodle.control_message.InjectTouchEvent(
            action=symmetrical_doodle.android.input.MotionEventAction.
            AMOTION_EVENT_ACTION_MOVE,
            pointer_id=symmetrical_doodle.control_message.POINTER_ID_MOUSE,
            position=symmetrical_doodle.coords.Position(
                screen_size,
                symmetrical_doodle.coords.Point(
                    round(lerp(x1, x2, alpha)), round(lerp(y1, y2, alpha))
                )
            ),
            pressure=1.0,
            buttons=symmetrical_doodle.android.input.MotionEventButton.
            AMOTION_EVENT_BUTTON_PRIMARY.value,
        )
        await controller.send_message(message)
        await asyncio.sleep(interval)
        now = time.time()
    message = symmetrical_doodle.control_message.InjectTouchEvent(
        action=symmetrical_doodle.android.input.MotionEventAction.
        AMOTION_EVENT_ACTION_UP,
        pointer_id=symmetrical_doodle.control_message.POINTER_ID_MOUSE,
        position=symmetrical_doodle.coords.Position(
            screen_size, symmetrical_doodle.coords.Point(x2, y2)
        ),
        pressure=1.0,
        buttons=symmetrical_doodle.android.input.MotionEventButton.
        AMOTION_EVENT_BUTTON_PRIMARY.value,
    )
    await controller.send_message(message)
