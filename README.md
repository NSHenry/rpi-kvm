# Raspberry Pi K(V)M (USB - Bluetooth)

## Overview

![Overview](/.github/Screenshots/overview.png)

- Use one keyboard/mouse at multiple bluetooth devices (PC/Laptop/Mac/Mobile Phones)
- Switch via hotkey between the connected bluetooth clients
- Build-in web service
    - Overview of the connected bluetooth clients
    - Change the hotkey configuration

## Getting started

### Step 1: Install

Connect to your raspberry pi via ssh:

``` bash
cd /home/pi
git clone https://github.com/BLeeEZ/rpi-kvm.git
cd rpi-kvm
sudo ./rpi-kvm.sh install
```

### Step 2: Start the RPI-K(V)M service

``` bash
sudo ./rpi-kvm.sh start
```

### Step 3: Optional steps

#### a) Display status and additional information

RPI-K(V)M is running in a tmux session. To see the service logger messages:

``` bash
sudo ./rpi-kvm.sh attach
```

#### b) Open the web interface

To see detailed bluetooth client information go the RPI-K(V)M web interface: [http://raspberrypi:8080](http://raspberrypi:8080)
>Note: If the host name has been changed during initial Raspberry Pi set up, then the webserver is reachable at its new RPI-KVM host name or its IP address

![Web page](/.github/Screenshots/web.png)

#### c) Connect a HD44780 LCD

Follow [this](/docu/lcd.md) wiring guide to display the bluetooth clients on an LCD.

![Animated lcd bluetooth client switch](/.github/Screenshots/lcd.gif)

## Technologies / Attributions

### Linux

- Tmux
- D-Bus
- Bluetooth (BLueZ)
- HD44780-LCD support (optional)

### Python

- asyncio
- evdev
- dbus_next
- aiohttp

### Web

- [Typescript](https://www.typescriptlang.org): JavaScript with syntax for types.
- [React Js](https://reactjs.org/): A JavaScript library for building user interfaces
- [Bootstrap](https://getbootstrap.com/): Responsive mobile-first websites
- [Bootstrap Icons](https://icons.getbootstrap.com/?#icons): Beautiful web icons and used for doc/overview pictures