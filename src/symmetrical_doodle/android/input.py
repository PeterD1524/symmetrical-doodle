# copied from <https://android.googlesource.com/platform/frameworks/native/+/master/include/android/input.h>
# blob 76422154f124e81fbab75476b141d464dde7ccad
# (and modified)
#  Copyright (C) 2010 The Android Open Source Project
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import enum


class MetaState(enum.Enum):
    AMETA_NONE = 0
    AMETA_ALT_ON = 0x02
    AMETA_ALT_LEFT_ON = 0x10
    AMETA_ALT_RIGHT_ON = 0x20
    AMETA_SHIFT_ON = 0x01
    AMETA_SHIFT_LEFT_ON = 0x40
    AMETA_SHIFT_RIGHT_ON = 0x80
    AMETA_SYM_ON = 0x04
    AMETA_FUNCTION_ON = 0x08
    AMETA_CTRL_ON = 0x1000
    AMETA_CTRL_LEFT_ON = 0x2000
    AMETA_CTRL_RIGHT_ON = 0x4000
    AMETA_META_ON = 0x10000
    AMETA_META_LEFT_ON = 0x20000
    AMETA_META_RIGHT_ON = 0x40000
    AMETA_CAPS_LOCK_ON = 0x100000
    AMETA_NUM_LOCK_ON = 0x200000
    AMETA_SCROLL_LOCK_ON = 0x400000


class KeyEventAction(enum.Enum):
    AKEY_EVENT_ACTION_DOWN = 0
    AKEY_EVENT_ACTION_UP = 1
    AKEY_EVENT_ACTION_MULTIPLE = 2


#  */?\*.*\n
class MotionEventAction(enum.Enum):
    AMOTION_EVENT_ACTION_MASK = 0xFF
    AMOTION_EVENT_ACTION_POINTER_INDEX_MASK = 0xFF00
    AMOTION_EVENT_ACTION_DOWN = 0
    AMOTION_EVENT_ACTION_UP = 1
    AMOTION_EVENT_ACTION_MOVE = 2
    AMOTION_EVENT_ACTION_CANCEL = 3
    AMOTION_EVENT_ACTION_OUTSIDE = 4
    AMOTION_EVENT_ACTION_POINTER_DOWN = 5
    AMOTION_EVENT_ACTION_POINTER_UP = 6
    AMOTION_EVENT_ACTION_HOVER_MOVE = 7
    AMOTION_EVENT_ACTION_SCROLL = 8
    AMOTION_EVENT_ACTION_HOVER_ENTER = 9
    AMOTION_EVENT_ACTION_HOVER_EXIT = 10
    AMOTION_EVENT_ACTION_BUTTON_PRESS = 11
    AMOTION_EVENT_ACTION_BUTTON_RELEASE = 12


class MotionEventButton(enum.Enum):
    AMOTION_EVENT_BUTTON_PRIMARY = 1 << 0
    AMOTION_EVENT_BUTTON_SECONDARY = 1 << 1
    AMOTION_EVENT_BUTTON_TERTIARY = 1 << 2
    AMOTION_EVENT_BUTTON_BACK = 1 << 3
    AMOTION_EVENT_BUTTON_FORWARD = 1 << 4
    AMOTION_EVENT_BUTTON_STYLUS_PRIMARY = 1 << 5
    AMOTION_EVENT_BUTTON_STYLUS_SECONDARY = 1 << 6
