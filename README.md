# LegionControllerLinux

I made this fan-curve and power-mode controller for my **Lenovo Legion** laptop because Lenovo Vantage doesn't exist on Linux.
It has two parts:

- a **kernel module** that maps the laptop's Embedded Controller (EC) memory and exposes it through `sysfs`
- a **GUI app** (Python + CustomTkinter) where you switch power modes and drag points on a fan curve for each mode

> ⚠️ **Status: experimental.** The app is nearly finished, but there's no stable release yet. The module writes directly into EC memory, so only use it on a supported model, and at your own risk.

---

## Features

- **Power mode switching:** Balanced, Performance and Quiet, the same modes as the Fn+Q hotkey. The active mode is highlighted in the app (light blue, red or dark blue).
- **Custom fan curve for each power mode:** 6 points (temperature → RPM) that you edit by dragging them on a graph. The points snap to a 100 RPM / 5 °C grid and always stay in order.
- **Live readings:** current fan speed (RPM) plus CPU and GPU temperatures, refreshed every 2 seconds.
- **Choice of temperature source:** the curve can follow either the CPU or the GPU temperature.
- **Saved config:** curves and settings are saved to `~/.lc/LegionController.ini`, and you can reset the current curve or the settings to their defaults.
- **Clean exit:** closing the app unloads the module, and the EC goes back to its stock fan table.

## Supported hardware

Right now I support the **`GKCN` BIOS family** (Legion 5 / 5 Pro / 7, 2021 AMD models).

To check your BIOS version:

```bash
sudo dmidecode -s bios-version
```

If it doesn't start with `GKCN`, don't use the module yet. Other models use different EC offsets (see [EC notes](#ec-notes)).

## How it works

### Kernel module (`Module/LegionController.c`)

When it loads, the module:

1. maps the EC memory region starting at physical address `0xFE00D400`
2. turns off the EC "fan off" temperature thresholds, so the fans follow the custom curve
3. creates `/sys/kernel/LegionController/` with these files:

| File | Content |
|---|---|
| `fanSpeedCurrent` | Current fan speed (in units of 100 RPM) |
| `tempCurrentCPU` | CPU temperature (°C) |
| `tempCurrentGPU` | GPU temperature (°C) |
| `fanCurve` | The EC fan table (left and right fan, 11 points each) |
| `powerMode` | `0` = Balanced, `1` = Performance, `2` = Quiet |

You control it through module parameters:

| Parameter | Meaning |
|---|---|
| `/sys/module/LegionController/parameters/cPowerMode` | Power mode to set (`0`–`2`) |
| `/sys/module/LegionController/parameters/cFanCurve` | Target fan speed in units of 100 RPM (`0`–`45`) |

New values are applied the next time `powerMode` is read. The target speed is written to every point of the EC fan table, which holds the fans at that speed.

### GUI app (`App/LegionController.py`)

Every 2 seconds, the app:

1. reads the selected temperature (CPU or GPU)
2. finds which segment of the current mode's curve that temperature falls in
3. sends the matching RPM to the module through `cFanCurve`

So the curve logic runs in the app, and the EC only gets a single target speed.

## Requirements

**Module**
- kernel headers for your running kernel (e.g. `linux-headers`)
- `make` and `gcc`

**App**
- Python 3
- `customtkinter` 4.x
- `Pillow` < 10
- `numpy`
- `pyinstaller`

```bash
pip install "customtkinter<5" "Pillow<10" numpy pyinstaller
```

## Building

### Kernel module

```bash
cd Module
make
```

This builds `LegionController.ko`. `make clean` removes the build files.

### App

The app is packaged as a single binary with PyInstaller, with the icons bundled inside:

```bash
cd App
sh make.sh
```

Before building, set `--workpath` and `--distpath` in `make.sh` to wherever you want the build output to go.

## Installation

Put the built `LegionController` binary in the repository root, then run:

```bash
sudo sh InstallationScript/LCInstall.sh
```

The installer:

1. creates `~/.lc/` with an empty `LegionController.ini`
2. builds the kernel module and copies `LegionController.ko` to `~/.lc/`
3. copies the `LegionController` binary to `/usr/bin`
4. deletes the cloned repository folder

> Note: because of step 4, the folder you run the installer from is removed once it finishes.

## Usage

```bash
sudo LegionController
```

The app loads the module when it starts and unloads it when you close it, so it needs `sudo`.

- **Mode buttons:** Performance, Balanced, Quiet
- **Fan curve graph:** drag the white points to change the curve (X = RPM, Y = °C)
- **Save:** saves the curve for the current mode
- **Reset Curve:** restores the default curve for the current mode
- **Settings:** choose CPU or GPU as the temperature source, or reset the settings

### Default curves

| Point | Balanced | Performance | Quiet |
|---|---|---|---|
| 1 | 0 °C → 0 RPM | 0 °C → 0 RPM | 0 °C → 0 RPM |
| 2 | 45 °C → 1800 | 45 °C → 1800 | 45 °C → 1800 |
| 3 | 55 °C → 2200 | 55 °C → 2200 | 55 °C → 2200 |
| 4 | 70 °C → 2600 | 70 °C → 2600 | 70 °C → 2600 |
| 5 | 80 °C → 3500 | 80 °C → 3500 | 75 °C → 2900 |
| 6 | 85 °C → 3800 | 90 °C → 4400 | 80 °C → 3500 |

## EC notes

I found the EC offsets by dumping EC RAM while switching modes and fan speeds. My raw notes and screenshots of the dumps are in [`infos/`](infos/).

| Data | 2021 | 2020 |
|---|---|---|
| Table base (offset) | `0x520` | `0x520` |
| CPU temp trigger points | row `0x70` | row `0x80` |
| GPU temp trigger points | row `0x90` | row `0x90` |
| Left fan speeds | row `0x20` | row `0x20` |
| Right fan speeds | row `0x30` | row `0x30` |
| Power mode | `0x10` | `0x10` |

Current fan speed is at left `0xE0` / `0xDC` and right `0xE1` / `0xDD`. Current temperatures are at CPU `0x18` and GPU `0x19`.

## Roadmap

- Support for more models and BIOS versions
- Separate curves for the left and right fans
- Tray icon
- Stable release

## Project layout

```
App/                  GUI app, icons, PyInstaller build script
Module/               Kernel module source + Makefile
InstallationScript/   Installer
infos/                EC offset notes and EC dump screenshots
```

## Credits

- **SmokelessCPU**: the kernel module base
