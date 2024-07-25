import sys
from pathlib import Path

class _Leds:

    __STA_LED_GREEN_BRIGHTNESS = "/sys/class/leds/usr_led2/brightness"
    __STA_LED_RED_BRIGHTNESS = "/sys/class/leds/usr_led1/brightness"
    __USR_LED_GREEN_BRIGHTNESS = "/sys/class/leds/usr_led0/brightness"

    @property
    def sta_led(self):
        return self.sta_led_green

    @sta_led.setter
    def sta_led(self, value):
        self.sta_led_green = value
        self.sta_led_red = False

    @property
    def sta_led_green(self):
        return True if self.__read_1st_line_from_file(_Leds.__STA_LED_GREEN_BRIGHTNESS) != "0" else False

    @sta_led_green.setter
    def sta_led_green(self, value):
        self.__write_to_file(_Leds.__STA_LED_GREEN_BRIGHTNESS, "1" if value else "0")

    @property
    def sta_led_red(self):
        return True if self.__read_1st_line_from_file(_Leds.__STA_LED_RED_BRIGHTNESS) != "0" else False

    @sta_led_red.setter
    def sta_led_red(self, value):
        self.__write_to_file(_Leds.__STA_LED_RED_BRIGHTNESS, "1" if value else "0")

    @property
    def usr_led(self):
        return True if self.__read_1st_line_from_file(_Leds.__USR_LED_GREEN_BRIGHTNESS) != "0" else False

    @usr_led.setter
    def usr_led(self, value):
        self.__write_to_file(_Leds.__USR_LED_GREEN_BRIGHTNESS, "1" if value else "0")

    def __read_1st_line_from_file(self, file_name):
        with open(file_name, "r") as f:
            return f.readline().replace("\n", "")

    def __write_to_file(self, file_name, value):
        with open(file_name, "w") as f:
            f.write(value)


sys.modules[__name__] = _Leds()
