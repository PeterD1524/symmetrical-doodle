import dataclasses

import android.input
import control_message
import input_events


@dataclasses.dataclass
class MouseInject:
    pass


def convert_mouse_buttons(state: int):
    state &= 0xffffffff
    buttons = 0
    if state & input_events.MouseButton.LEFT.value:
        buttons |= android.input.MotionEventButton.AMOTION_EVENT_BUTTON_PRIMARY.value
    if state & input_events.MouseButton.RIGHT.value:
        buttons |= android.input.MotionEventButton.AMOTION_EVENT_BUTTON_SECONDARY.value
    if state & input_events.MouseButton.MIDDLE.value:
        buttons |= android.input.MotionEventButton.AMOTION_EVENT_BUTTON_TERTIARY.value
    if state & input_events.MouseButton.X1.value:
        buttons |= android.input.MotionEventButton.AMOTION_EVENT_BUTTON_BACK.value
    if state & input_events.MouseButton.X2.value:
        buttons |= android.input.MotionEventButton.AMOTION_EVENT_BUTTON_FORWARD.value
    return buttons


def convert_mouse_action(action: input_events.Action):
    if action is input_events.Action.DOWN:
        return android.input.MotionEventAction.AMOTION_EVENT_ACTION_DOWN
    assert action is input_events.Action.UP
    return android.input.MotionEventAction.AMOTION_EVENT_ACTION_UP


def process_click(event: input_events.MouseClickEvent):
    message = control_message.InjectTouchEvent(
        action=convert_mouse_action(event.action),
        pointer_id=control_message.POINTER_ID_MOUSE,
        position=event.position,
        pressure=1.0 if event.action is input_events.Action.DOWN else 0.0,
        buttons=convert_mouse_buttons(event.buttons_state),
    )
    return message
