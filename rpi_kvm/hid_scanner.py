#!/usr/bin/python3

import asyncio
import evdev
import logging


class HidScanner(object):
    def __init__(self):
        self._devices = []
        self._keyboards = []
        self._mice = []

    @property
    def devices(self):
        return self._devices

    @property
    def keyboard_devices(self):
        return self._keyboards

    @property
    def mouse_devices(self):
        return self._mice

    async def scan(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._scan_for_devices_via_blocking_evdev)
    
    def _scan_for_devices_via_blocking_evdev(self):
        self._devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        self._keyboards = []
        self._mice = []
        for device in self._devices:
            # has device a right button -> it's a mouse
            if evdev.ecodes.BTN_RIGHT in device.capabilities().get(evdev.ecodes.EV_KEY, []):
                self._mice.append(device)
                # logging.info(f"self._mice = {self._mice}")
            # Ignore reTerminal Keys & Touchscreen (Surface touchscreen too)
            # elif device.name == "gpio_keys" or device.name == "seeed-tp" or device.name == "gpio_ir_recv" or device.name == "vc4-hdmi-0" or device.name == "vc4-hdmi-1" or device.name == "vc4-hdmi-0 HDMI Jack" or device.name == "vc4-hdmi-1 HDMI Jack" or device.name == "ELAN9038:00 04F3:2A1C":
                # logging.info(f"{device.name} ignored")
            elif not self._kb_include(device):
                continue
            else:
                self._keyboards.append(device)
                # logging.info(f"self._keyboards = {self._keyboards}")
    
    @staticmethod
    def _kb_include(device):
        match device.name:
            case "gpio_keys":
                return False
            case "seeed-tp":
                return False
            case "gpio_ir_recv":
                return False
            case "vc4-hdmi-0":
                return False
            case "vc4-hdmi-1":
                return False
            case "vc4-hdmi-0 HDMI Jack":
                return False
            case "vc4-hdmi-1 HDMI Jack":
                return False
            # BEGIN: Surface Go 2 Inputs
            # case "ELAN9038:00 04F3:2A1C":
            #     return False
            # case "Power Button":
            #     return False
            # case "Lid Switch":
            #     return False
            # case "AT Translated Set 2 keyboard":
            #     return False
            # case "ELAN9038:00 04F3:2A1C Stylus":
            #     return False
            # case "Microsoft Surface Keyboard Touchpad":
            #     return False
            # case "Intel HID events":
            #     return False
            # case "Intel HID 5 button array":
            #     return False
            # case "Intel HID switches":
            #     return False
            # case "Video Bus":
            #     return False
            # case "HDA Intel PCH Mic":
            #     return False
            # case "HDA Intel PCH Headphone":
            #     return False
            # case "HDA Intel PCH HDMI/DP,pcm=3":
            #     return False
            # case "HDA Intel PCH HDMI/DP,pcm=7":
            #     return False
            # case "HDA Intel PCH HDMI/DP,pcm=8":
            #     return False
            # case "Generic USB Audio Consumer Control":
            #     return False
            # case "Generic USB Audio":
            #     return False
            # END: Surface Go 2 Inputs
            case _:
                return True

    def info(self, verbose=False):
        logging.info(f"=== devices ========================")
        for device in self._devices:
            logging.info(f"{device.path} {device.name} {device.phys}")
            if verbose:
                logging.info(f"{device.capabilities(verbose=True)}")
                logging.info(f"-----------------------------------")
        logging.info(f"=== keyboards ======================")
        for device in self._keyboards:
            logging.info(f"{device.path} {device.name} {device.phys}")
        logging.info(f"=== mice ===========================")
        for device in self._mice:
            logging.info(f"{device.path} {device.name} {device.phys}")


async def main():
    logging.basicConfig(format='HID %(levelname)s: %(message)s', level=logging.DEBUG)
    hid_manager = HidScanner()
    await hid_manager.scan()
    hid_manager.info()

if __name__ == "__main__":
    asyncio.run(main())
