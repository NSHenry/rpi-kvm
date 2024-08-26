#!/usr/bin/python3

import asyncio
import evdev
# from evdev import *
import dbus_fast
from dbus_fast.aio import MessageBus
import logging
from hid_scanner import HidScanner
from usb_hid_decoder import UsbHidDecoder
# reTerminal Status Lights
from leds import Leds


class Keyboard(object):
    is_host_active = bool
    # So I guess this is a class attribute type vs. setting the attribute as a "literal" boolean. The program runs correctly either way. Pylance only seems to whine about this.
    is_kb_connected: bool

    # def __init__(self, input_device):
    def __init__(self, input_device=None):
        self._is_alive = False
        self._idev = input_device
        self._modifiers = [  # One byte size (bit map) to represent the pressed modifier keys
            False,  # Right GUI
            False,  # Right Alt
            False,  # Right Shift
            False,  # Right Control
            False,  # Left GUI
            False,  # Left Alt
            False,  # Left Shift
            False]  # Left Control
        # Place for 6 simultaneously pressed regular keys
        self._keys = [0, 0, 0, 0, 0, 0]

    @property
    def is_alive(self):
        return self._is_alive

    @property
    def path(self):
        return self._idev.path

    @property
    def name(self):
        return self._idev.name

    async def run(self):
        logging.info(f"{self._idev.path}: Init Keyboard - {self._idev.name}")
        logging.info(f"{self._idev.path}: D-Bus service connecting...")
        await self._connect_to_dbus_service()
        await self._register_to_dbus_signals()
        logging.info(f"{self._idev.path}: Starting event loop")
        self._is_alive = True
        try:
            await self._event_loop()
        except Exception as e:
            logging.error(f"{self._idev.path}: {e}")
        self._is_alive = False

    def _handle_active_host(self, is_host_active):
        Keyboard.is_host_active = is_host_active
        # logging.info(f"HAF Keyboard._s_host_active = {Keyboard.is_host_active}")
        # logging.info(f"\033[0;36mConnected Clients: {self._clients_connected_count} \033[0m")
        if Keyboard.is_host_active is True:
            try:
                self._idev.grab()
                Leds().sta_led_green = False
                Leds().sta_led_red = True
            except OSError:
                # logging.info(f"\033[0;36mKeyboard already captured by another process. \033[0m")
                pass
        elif Keyboard.is_host_active is False:
            try:
                self._idev.ungrab()
                Leds().sta_led_green = True
                Leds().sta_led_red = False
            except OSError:
                # logging.info(f"\033[0;36mKeyboard already released. \033[0m")
                pass

    # Reactivates the bt host if connected client count is greater than 0, a keyboard is connected, and the host is not active.
    async def _handle_connected_client_count(self, clients_connected_count):
        self._clients_connected_count = clients_connected_count
        # logging.info(f"HCCC self._clients_connected_count: {self._clients_connected_count}")
        # logging.info(f"HCCC Keyboard.is_kb_connected: {Keyboard.is_kb_connected}")
        # logging.info(f"HCCC Keyboard.is_host_active: {Keyboard.is_host_active}")
        if self._clients_connected_count > 0 and Keyboard.is_kb_connected is True and Keyboard.is_host_active is False:
            try:
                await self._kvm_dbus_iface.call_connect_active_host()
            except dbus_fast.DBusError:
                logging.warning(f"_handle_connected_client_count: D-Bus connection terminated - reconnecting...")
                await self._connect_to_dbus_service()
                await self._handle_connected_client_count(self)

    # poll for keyboard events
    async def _event_loop(self):
        async for event in self._idev.async_read_loop():
            # only bother if we hit a key and it's an up or down event
            if event.type == evdev.ecodes.EV_KEY and event.value < 2:
                self._handle_event(event)
                await self._send_state()

    async def _connect_to_dbus_service(self):
        self._kvm_dbus_iface = None
        while not self._kvm_dbus_iface:
            try:
                bus = await MessageBus(bus_type=dbus_fast.BusType.SYSTEM).connect()
                introspection = await bus.introspect(
                    'org.rpi.kvmservice', '/org/rpi/kvmservice')
                kvm_service_obj = bus.get_proxy_object(
                    'org.rpi.kvmservice', '/org/rpi/kvmservice', introspection)
                self._kvm_dbus_iface = kvm_service_obj.get_interface('org.rpi.kvmservice')
                logging.info(f"KB: D-Bus Service Connected")
            except dbus_fast.DBusError:
                logging.info(f"KB: D-Bus service not available - reconnecting...")
                await asyncio.sleep(5)

    # Register to D-Bus signals
    async def _register_to_dbus_signals(self):
        logging.info("Register on D-Bus signals")
        try:
            self._kvm_dbus_iface.on_signal_is_host_active(self._handle_active_host)
            self._kvm_dbus_iface.on_signal_connected_client_count(self._handle_connected_client_count)
        except dbus_fast.DBusError:
            logging.warning("D-Bus service not available - reconnecting...")
            await self._connect_to_dbus_service()
            await self._register_to_dbus_signals()

    # Clear active host when no keyboard is present.
    async def kb_clear_active_bt_host(self):
        await self._connect_to_dbus_service()
        try:
            await self._kvm_dbus_iface.call_clear_active_host()
        except dbus_fast.DBusError:
            logging.warning(f"{self._idev.path}: D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()
            await self.kb_clear_active_bt_host()

    async def _send_state(self):
        modifier_str = ''
        for i in self._modifiers:
            mod_value_str = "1" if i else "0"
            modifier_str += mod_value_str
        # Turning this off to keep the tmux clean.
        # logging.debug(f"{self._idev.path}: mod: {modifier_str} keys: {self._keys}")
        try:
            await self._kvm_dbus_iface.call_send_keyboard_usb_telegram(self._modifiers, bytes(self._keys))
        except dbus_fast.DBusError:
            logging.warning(f"{self._idev.path}: D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()

    def _handle_event(self, event):
        # noinspection PyUnresolvedReferences
        if event.code not in ecodes.KEY:
            logging.warning(f"{self._idev.path}: unsupported key press code: {event.code}")
            return
        # noinspection PyUnresolvedReferences
        evdev_code = ecodes.KEY[event.code]
        if UsbHidDecoder.is_modifier_key(evdev_code):
            modifier_index = UsbHidDecoder.encode_modifier_key_index(evdev_code)
            self._modifiers[modifier_index] = not self._modifiers[modifier_index]
        else:
            usb_key_code = UsbHidDecoder.encode_regular_key(evdev_code)
            for i in range(0, 6):
                if self._keys[i] == usb_key_code and event.value == 0:
                    self._keys[i] = 0x00  # Code 0x00 represents a key release
                elif self._keys[i] == 0x00 and event.value == 1:
                    self._keys[i] = usb_key_code
                    break


async def main():
    logging.basicConfig(format='KB %(levelname)s: %(message)s', level=logging.DEBUG)
    logging.info("Creating HID Manager")
    hid_manager = HidScanner()
    keyboards = dict()

    while True:
        await hid_manager.scan()

        removed_keyboards = [keyboard for keyboard in keyboards.values() if not keyboard.is_alive]
        for keyboard in removed_keyboards:
            logging.info(f"Removing keyboard: {keyboard.path}")
            del keyboards[keyboard.path]

        device_paths = [keyboard_device.path for keyboard_device in hid_manager.keyboard_devices]
        # logging.info(f"Keyboard Count: {len(device_paths)}")

        if len(device_paths) == 0:
            Keyboard.is_kb_connected = False
            logging.warning("No keyboard found, waiting till next device scan")
            logging.info(f"MAIN Keyboard.is_host_active = {Keyboard.is_host_active}")
            if Keyboard.is_host_active is True:
                logging.info("No more keyboards connected, clearing active host.")
                try:
                    await asyncio.create_task(Keyboard().kb_clear_active_bt_host())
                except dbus_fast.DBusError as e:
                    logging.error(f"kb_clear_active_bt_host Error : {e}")
        else:
            Keyboard.is_kb_connected = True
            new_keyboards = [keyboard_device for keyboard_device in hid_manager.keyboard_devices if keyboard_device.path not in keyboards]
            for keyboard_device in new_keyboards:
                kb = Keyboard(keyboard_device)
                keyboards[keyboard_device.path] = kb
                asyncio.create_task(kb.run())
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
