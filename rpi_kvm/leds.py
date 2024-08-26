import sys
import os


class Leds:
    __STA_LED_GREEN_BRIGHTNESS = "/sys/class/leds/usr_led2/brightness"
    __STA_LED_RED_BRIGHTNESS = "/sys/class/leds/usr_led1/brightness"
    __USR_LED_GREEN_BRIGHTNESS = "/sys/class/leds/usr_led0/brightness"

    # BEGIN: AI Suggestions
    def __init__(self):
        self.__verify_files_existence()

    @staticmethod
    def __verify_files_existence():

        for file in [__STA_LED_GREEN_BRIGHTNESS, __STA_LED_RED_BRIGHTNESS, __USR_LED_GREEN_BRIGHTNESS]:
            if not os.path.exists(file):
                raise FileNotFoundError(f"LED control file does not exist: {file}")
    # END: AI Suggestions

    @property
    def sta_led(self):
        return self.sta_led_green

    @sta_led.setter
    def sta_led(self, value):
        self.sta_led_green = value
        self.sta_led_red = False

    @property
    def sta_led_green(self):
        return True if self.__read_1st_line_from_file(Leds.__STA_LED_GREEN_BRIGHTNESS) != "0" else False

    @sta_led_green.setter
    def sta_led_green(self, value):
        self.__write_to_file(Leds.__STA_LED_GREEN_BRIGHTNESS, "1" if value else "0")

    @property
    def sta_led_red(self):
        return True if self.__read_1st_line_from_file(Leds.__STA_LED_RED_BRIGHTNESS) != "0" else False

    @sta_led_red.setter
    def sta_led_red(self, value):
        self.__write_to_file(Leds.__STA_LED_RED_BRIGHTNESS, "1" if value else "0")

    @property
    def usr_led(self):
        return True if self.__read_1st_line_from_file(Leds.__USR_LED_GREEN_BRIGHTNESS) != "0" else False

    @usr_led.setter
    def usr_led(self, value):
        self.__write_to_file(Leds.__USR_LED_GREEN_BRIGHTNESS, "1" if value else "0")

    @staticmethod
    def __read_1st_line_from_file(file_name):
        try:
            with open(file_name, "r") as f:
                return f.readline().replace("\n", "")
        except NameError as e:
            # Handle/Log exception
            pass

    @staticmethod
    def __write_to_file(file_name, value):
        try:
            with open(file_name, "w") as f:
                f.write(value)
        except NameError as e:
            # Handle/Log exception
            pass


# BEGIN: AI Suggestions
# Create _Leds instance for further use instead of modifying sys.modules
leds_instance = Leds()
# END: AI Suggestions
