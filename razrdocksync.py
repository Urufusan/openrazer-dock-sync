#!/usr/bin/python3
# Copyright 2025 Urufusan.
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import time

import openrazer.client
from openrazer.client.devices import RazerDevice

CHROMA_DOCK_MICE_NAMES = ["Razer Naga Pro", "Razer DeathAdder V2 Pro", "Razer Basilisk Ultimate", "Razer Viper Ultimate"]

GRADIENT = [
    {"color": "#220000", "position": 0},
    {"color": "#ff0000", "position": 20},
    {"color": "#ffa600", "position": 50},
    {"color": "#00ff00", "position": 100},
]

POLL_DELAY_CONST = int(os.environ.get("RZR_SLEEPFOR", 360))
QUICK_RETRIES_AMOUT = 6  # Does a shallow check, doesn't reinit dbus
FULL_RETRIES_AMOUT = 2  # Does a 'full' refresh (devices that weren't there before will now be shown)


def hex_to_rgb(hex_value):
    return tuple(int(hex_value.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))


def pick_gradient_color(value, gradient_map, returnmethod="hex"):
    """## Generates color based on the input value

    Define your gradient colors and positions with either floats or ints:
    ```
    gradient = [
       {'color': '#03ee80', 'position': 0},
       {'color': '#ab77ff', 'position': 0.4},
       {'color': '#ff0040', 'position': 1}
    ]
    ```
    """
    # select value
    for i in range(len(gradient_map) - 1):
        if value <= gradient_map[i + 1]["position"]:
            color1 = hex_to_rgb(gradient_map[i]["color"])
            color2 = hex_to_rgb(gradient_map[i + 1]["color"])
            position1 = gradient_map[i]["position"]
            position2 = gradient_map[i + 1]["position"]
            break

    # interpolated color based on the value
    ratio = (value - position1) / (position2 - position1)
    r = int(color1[0] + (color2[0] - color1[0]) * ratio)
    g = int(color1[1] + (color2[1] - color1[1]) * ratio)
    b = int(color1[2] + (color2[2] - color1[2]) * ratio)

    match returnmethod:
        case "hex":
            return "#{:02x}{:02x}{:02x}".format(r, g, b)
        case _:
            return r, g, b


def check_if_present(dock_device: RazerDevice, mouse_device: RazerDevice) -> bool:
    """## Returns ``True`` if both the mouse and the dock are present"""
    # * DPI values that are (0, 0) imply that the dongle is connected but the mouse is not.
    if not (bool(mouse_device) and bool(dock_device)) or getattr(mouse_device, "dpi", None) == (0, 0):
        if dock_device:
            if dock_device.fx.effect != "breathSingle":
                dock_device.fx.breath_single(50, 70, 255)
        print(f"(One or more) required devices is not present:\n({mouse_device=}, {dock_device=})")
        return False
    return True


if __name__ == "__main__":
    for _init_try in range(FULL_RETRIES_AMOUT):
        dock_device = None
        mouse_device = None

        devman = openrazer.client.DeviceManager()
        devman.sync_effects = False
        devices: list[RazerDevice] = devman.devices

        print(devices)

        for razer_device in devices:
            if "Dock" in razer_device.name:
                dock_device = razer_device
            if any(_mouse_name in razer_device.name for _mouse_name in CHROMA_DOCK_MICE_NAMES):
                mouse_device = razer_device
            if not razer_device.battery_level:
                continue

            print(f"{razer_device.name} is at {razer_device.battery_level}% battery.")

        if not (_present := check_if_present(dock_device, mouse_device)):
            # ! I added the this logic because the mouse is not always connected upon OS startup
            for _ in range(QUICK_RETRIES_AMOUT):
                time.sleep(5)
                _present = check_if_present(dock_device, mouse_device)
                if _present:
                    break
            else:
                if _init_try == FULL_RETRIES_AMOUT - 1:
                    print(f"Startup failed, retried {QUICK_RETRIES_AMOUT*FULL_RETRIES_AMOUT} times")
                    if dock_device:
                        dock_device.fx.static(139, 0, 181)
                    exit(1)
                else:
                    print(f"{QUICK_RETRIES_AMOUT} tries failed...")
                    continue

        dock_device.brightness = 100.0

        while _present:
            if not check_if_present(dock_device, mouse_device):
                print("Retrying...")
                time.sleep(5)
                continue

            _gradient_color = pick_gradient_color(mouse_device.battery_level, GRADIENT, 0)
            print("Dock: ", _gradient_color)
            dock_device.fx.static(*_gradient_color)
            time.sleep(POLL_DELAY_CONST)
