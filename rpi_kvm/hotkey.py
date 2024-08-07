#!/usr/bin/python3

import enum
import numpy
from settings import Settings
from usb_hid_decoder import UsbHidDecoder


class HotkeyAction(enum.Enum):
    SwitchToNextHost = 1
    IndicateHost = 2


class HotkeyConfig(object):
    def __init__(self, settings):
        self._settings = settings
        self.__init_keys()

    def reload_settings(self):
        self._settings.load_from_file()
        self.__init_keys()

    def __init_keys(self):
        self.keys = {
            HotkeyAction.SwitchToNextHost: self._settings['hotkeys']['nextHost'],
        }
        self.__reduce_keys_to_comparable_format()

    def __reduce_keys_to_comparable_format(self):
        for action, hotkey_combination in self.keys.items():
            reduced_combination = self.__combine_bitmask_and_remove_vendor_reserved(hotkey_combination)
            self.keys[action] = reduced_combination

    @staticmethod
    def __combine_bitmask_and_remove_vendor_reserved(keyboard_input):
        modifiers_int = UsbHidDecoder.convert_modifier_bit_mask_to_int(keyboard_input[0])
        return [modifiers_int, *keyboard_input[1:7]]


class RingBuffer(object):
    def __init__(self, size):
        self.data = None
        self.size = size
        self.reset()

    def reset(self):
        self.data = [None for i in range(self.size)]

    def append(self, x):
        self.data.insert(0, x)
        self.data.pop(self.size)

    def get(self):
        return self.data


class HotkeyDetector(object):
    def __init__(self, hotKeyConfig):
        self._config = hotKeyConfig
        self._hot_keys = self._config.keys
        self._key_strokes = RingBuffer(1)
        self._mouse_buttons = [False, False, False, False, False, False, False, False]
        self.activation = None

    def reload_settings(self):
        self._config.reload_settings()
        self._hot_keys = self._config.keys

    def evaluate_new_input(self, new_input):
        self._key_strokes.append(new_input)
        self.activation = None
        for action, key_combination in self._hot_keys.items():
            if numpy.array_equal(key_combination, self._key_strokes.get()[0]):
                self.activation = action
                self._key_strokes.reset()
                break
        return self.activation

    def evaluate_new_mouse_input(self, new_mouse_button_input):
        last_mouse_buttons_buffer = self._mouse_buttons
        self._mouse_buttons = new_mouse_button_input
        if new_mouse_button_input[2] and not last_mouse_buttons_buffer[2]:
            return HotkeyAction.SwitchToNextHost
        return None


if __name__ == "__main__":
    settings = Settings()
    config = HotkeyConfig(settings)
    detector = HotkeyDetector(config)
    print(detector.evaluate_new_input([0, 0, 0, 0, 0, 0, 0]) is None)
    print(detector.evaluate_new_input([0, 0x47, 0, 0, 0, 0, 0]) == HotkeyAction.SwitchToNextHost)
    print(detector.evaluate_new_input([0, 0x46, 0, 0, 0, 0, 0]) is None)
    print(detector.evaluate_new_input([0, 0x47, 0, 0, 0, 0, 0]) == HotkeyAction.SwitchToNextHost)
    print(detector.evaluate_new_input([0, 0, 0, 0, 0, 0, 0]) is None)
