import dataclasses

import symmetrical_doodle.android.input
import symmetrical_doodle.control_message
import symmetrical_doodle.input_events


@dataclasses.dataclass
class MouseInject:
    pass


def convert_mouse_buttons(state: int):
    state &= 0xffffffff
    buttons = 0
    if state & symmetrical_doodle.input_events.MouseButton.LEFT.value:
        buttons |= symmetrical_doodle.android.input.MotionEventButton.AMOTION_EVENT_BUTTON_PRIMARY.value
    if state & symmetrical_doodle.input_events.MouseButton.RIGHT.value:
        buttons |= symmetrical_doodle.android.input.MotionEventButton.AMOTION_EVENT_BUTTON_SECONDARY.value
    if state & symmetrical_doodle.input_events.MouseButton.MIDDLE.value:
        buttons |= symmetrical_doodle.android.input.MotionEventButton.AMOTION_EVENT_BUTTON_TERTIARY.value
    if state & symmetrical_doodle.input_events.MouseButton.X1.value:
        buttons |= symmetrical_doodle.android.input.MotionEventButton.AMOTION_EVENT_BUTTON_BACK.value
    if state & symmetrical_doodle.input_events.MouseButton.X2.value:
        buttons |= symmetrical_doodle.android.input.MotionEventButton.AMOTION_EVENT_BUTTON_FORWARD.value
    return buttons


def convert_mouse_action(action: symmetrical_doodle.input_events.Action):
    if action is symmetrical_doodle.input_events.Action.DOWN:
        return symmetrical_doodle.android.input.MotionEventAction.AMOTION_EVENT_ACTION_DOWN
    assert action is symmetrical_doodle.input_events.Action.UP
    return symmetrical_doodle.android.input.MotionEventAction.AMOTION_EVENT_ACTION_UP


def process_click(event: symmetrical_doodle.input_events.MouseClickEvent):
    message = symmetrical_doodle.control_message.InjectTouchEvent(
        action=convert_mouse_action(event.action),
        pointer_id=symmetrical_doodle.control_message.POINTER_ID_MOUSE,
        position=event.position,
        pressure=1.0 if
        event.action is symmetrical_doodle.input_events.Action.DOWN else 0.0,
        buttons=convert_mouse_buttons(event.buttons_state),
    )
    return message
