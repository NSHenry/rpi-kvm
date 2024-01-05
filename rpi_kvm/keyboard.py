#!/usr/bin/python3

import asyncio
import evdev
from evdev import *
import dbus_next
from dbus_next.aio import MessageBus
import logging
from hid_scanner import HidScanner
from usb_hid_decoder import UsbHidDecoder
# from bt_server import BtServer
#Testing out using reTerminal status lights
from leds import _Leds as reTerminal

class Keyboard(object):
    # def __init__(self, input_device):
    def __init__(self, input_device=None):
        self._is_alive = False
        self._idev = input_device
        self._clients_connected_count = int() #Setting up an integer variable for count.
        self._modifiers = [ # One byte size (bit map) to represent the pressed modifier keys
            False, # Right GUI
            False, # Right Alt
            False, # Right Shift
            False, # Right Control
            False, # Left GUI
            False, # Left Alt
            False, # Left Shift
            False] # Left Control
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

    async def run_clear_host(self):
        logging.info("KBD Disconnect: D-Bus service connecting...")
        await self._connect_to_dbus_service()
        await self._clear_active_host()

    # Only capture if there are connected clients
    def _handle_connected_client_count(self, clients_connected_count):
        self._clients_connected_count = clients_connected_count
        # logging.info(f"\033[0;36mConnected Clients: {self._clients_connected_count} \033[0m")
        if self._clients_connected_count == 0:
            try:
                self._idev.ungrab()
                # logging.info(f"\033[0;36m FAKE Keyboard Ungrabbed \033[0m")
                try:
                    reTerminal.sta_led_green = False
                    reTerminal.sta_led_red = True
                except NameError:
                    print("reTerminal led not found.")
            except OSError as e:
                # If the device is already grabbed, print a message
                # logging.info(f"\033[0;36mKeyboard already ungrabbed. \033[0m")
                pass
            else:
                # If the device is successfully grabbed, print a message
                logging.info(f"\033[0;36mKeyboard Ungrabbed \033[0m")
        elif self._clients_connected_count > 0:
            try:
                self._idev.grab()
                # logging.info(f"\033[0;36m FAKE Keyboard Grabbed \033[0m")
                reTerminal.sta_led_green = True
                reTerminal.sta_led_red = False
            except OSError as e:
                # If the device is already grabbed, print a message
                # logging.info(f"\033[0;36mKeyboard already grabbed by another process. \033[0m")
                pass
            # else:
                # If the device is successfully grabbed, print a message
                # logging.info(f"\033[0;36mKeyboard Grabbed \033[0m")

    # poll for keyboard events
    async def _event_loop(self):
        async for event in self._idev.async_read_loop():
            # only bother if we hit a key and its an up or down event
            if event.type == ecodes.EV_KEY and event.value < 2:
                self._handle_event(event)
                await self._send_state()

    async def _connect_to_dbus_service(self):
        self._kvm_dbus_iface = None
        while not self._kvm_dbus_iface:
            try:
                bus = await MessageBus(bus_type=dbus_next.BusType.SYSTEM).connect()
                introspection = await bus.introspect(
                    'org.rpi.kvmservice', '/org/rpi/kvmservice')
                kvm_service_obj = bus.get_proxy_object(
                    'org.rpi.kvmservice', '/org/rpi/kvmservice', introspection)
                self._kvm_dbus_iface = kvm_service_obj.get_interface('org.rpi.kvmservice')
                logging.info(f"{self._idev.path}: D-Bus service connected")
            except dbus_next.DBusError:
                logging.warning(f"{self._idev.path}: D-Bus service not available - reconnecting...")
                await asyncio.sleep(5)

    # Copied over from info_hub
    async def _register_to_dbus_signals(self):
        logging.info("Register on D-Bus signals")
        try:
            self._kvm_dbus_iface.on_signal_connected_client_count(self._handle_connected_client_count)
        except dbus_next.DBusError:
            logging.warning("D-Bus service not available - reconnecting...")
            await self._connect_to_dbus_service()
            await self._register_to_dbus_signals()

    # attempt at creating a disconnect triggered by no keyboard presence that goes through d-bus
    async def _clear_active_host(self):
        try:
            await self._kvm_dbus_iface.call_clear_active_host()
        except dbus_next.DBusError:
            logging.warning(f"{self._idev.path}: D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()

    async def _send_state(self):
        modifier_str = ''
        for i in self._modifiers:
            mod_value_str = "1" if i else "0"
            modifier_str += mod_value_str
        # Turning this off to keep the tmux clean.
        # logging.debug(f"{self._idev.path}: mod: {modifier_str} keys: {self._keys}")
        try:
            await self._kvm_dbus_iface.call_send_keyboard_usb_telegram(self._modifiers, bytes(self._keys))
        except dbus_next.DBusError:
            logging.warning(f"{self._idev.path}: D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()

    def _handle_event(self, event):
        if event.code not in ecodes.KEY:
            logging.warning(f"{self._idev.path}: unsupported key press code: {event.code}")
            return
        evdev_code = ecodes.KEY[event.code]
        if UsbHidDecoder.is_modifier_key(evdev_code):
            modifier_index = UsbHidDecoder.encode_modifier_key_index(evdev_code)
            self._modifiers[modifier_index] = not self._modifiers[modifier_index]
        else:
            usb_key_code = UsbHidDecoder.encode_regular_key(evdev_code)
            for i in range(0, 6):
                if self._keys[i] == usb_key_code and event.value == 0:
                    self._keys[i] = 0x00 # Code 0x00 represents a key release
                elif self._keys[i] == 0x00 and event.value == 1:
                    self._keys[i] = usb_key_code
                    break

async def main():
    logging.basicConfig(format='KB %(levelname)s: %(message)s', level=logging.DEBUG)
    logging.info("Creating HID Manager")
    hid_manager = HidScanner()
    keyboards = dict()
    # bt_server = BtServer()

    while True:
        await hid_manager.scan()

        removed_keyboards = [keyboard for keyboard in keyboards.values() if not keyboard.is_alive]
        for keyboard in removed_keyboards:
            # If no more keyboards are connected then 
            if len(device_paths) == 0:
                kb = Keyboard()
                kb_task = asyncio.create_task(kb.run_clear_host())
                await kb_task
            logging.info(f"Removing keyboard: {keyboard.path}")
            del keyboards[keyboard.path]

        device_paths = [keyboard_device.path for keyboard_device in hid_manager.keyboard_devices]
        logging.info(f"Keyboard Count: {len(device_paths)}")
        
        if len(device_paths) == 0:
            # This does clear the active host, but it doesn't run through the dbus call.
            # bt_server.clear_active_host()
            logging.warning("No keyboard found, waiting till next device scan")
        else:
            new_keyboards = [keyboard_device for keyboard_device in hid_manager.keyboard_devices if keyboard_device.path not in keyboards]
            for keyboard_device in new_keyboards:
                kb = Keyboard(keyboard_device)
                keyboards[keyboard_device.path] = kb
                asyncio.create_task(kb.run())
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run( main() )
