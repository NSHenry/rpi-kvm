#!/bin/bash

case "$1" in
    install)
        sudo ./scripts/install.sh
        ;;
    uninstall)
        sudo ./scripts/uninstall.sh
        ;;
    debug)
        sudo ./rpi-kvm.sh restart
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led0/brightness'
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led1/brightness'
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led2/brightness'
        sudo ./rpi-kvm.sh attach
        ;;
    attach)
        sudo tmux attach-session -t rpi-kvm
        ;;
    kill)
        sudo tmux kill-session -t rpi-kvm
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led0/brightness'
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led1/brightness'
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led2/brightness'
        ;;
    stop)
        sudo tmux kill-session -t rpi-kvm
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led0/brightness'
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led1/brightness'
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led2/brightness'
        ;;
    quit)
        sudo tmux kill-session -t rpi-kvm
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led0/brightness'
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led1/brightness'
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led2/brightness'
        ;;
    start)
        sudo ./scripts/init.sh
        ;;
    restart)
        sudo tmux kill-session -t rpi-kvm
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led0/brightness'
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led1/brightness'
        sudo sh -c 'echo 0 > /sys/class/leds/usr_led2/brightness'
        sudo ./scripts/init.sh
        ;;
    update-mac)
        sudo ./scripts/update-mac.sh
        ;;
    update-name)
        sudo ./scripts/update-name.sh
        ;;
    *)
        echo "Incorrect input provided"
esac