**English** · [Deutsch](README.de.md)

# Firmware (QMK)

QMK keyboard definition for the convertible-keyboard-pcb. The matrix assignment
and the key order of every layout macro are **generated from the KiCad board
file**, not typed by hand — so the firmware cannot drift away from the PCB.

> **Compiled, not yet run on hardware.** All four variants build to a `.uf2`,
> and `qmk lint` passes. No board exists yet to test them on.

## Layouts

| Layout macro | Keys | Keymap folder |
|---|---|---|
| `LAYOUT_fullsize_iso` | 105 | `keymaps/default` |
| `LAYOUT_fullsize_ansi` | 104 | `keymaps/fullsize_ansi` |
| `LAYOUT_tkl_iso` | 88 | `keymaps/tkl_iso` |
| `LAYOUT_tkl_ansi` | 87 | `keymaps/tkl_ansi` |

The TKL variants are the ones to flash **after** snapping the numpad off. All
four are registered as QMK community layouts, so keymaps written for any other
`fullsize_iso` or `tkl_ansi` board can be used as-is.

## Building

This folder is the source of truth. Link it into a QMK checkout rather than
copying it:

```sh
git clone --depth 1 --recurse-submodules https://github.com/qmk/qmk_firmware.git
mkdir -p qmk_firmware/keyboards/technikweber
ln -s "$(pwd)/technikweber/convertible" qmk_firmware/keyboards/technikweber/convertible

python3 -m venv qmkenv && ./qmkenv/bin/pip install qmk
export QMK_HOME="$(pwd)/qmk_firmware"
./qmkenv/bin/qmk compile -kb technikweber/convertible -km default
```

Swap `-km default` for `fullsize_ansi`, `tkl_iso` or `tkl_ansi`. An
`arm-none-eabi-gcc` is required; any generic ARM build works, it does not have
to be the one from QMK's own installer.

## Flashing

Put the board into the bootloader — hold Escape while plugging it in, press
`SW201` on the back, hold `SW202` (BOOTSEL) while plugging in, or press
`Fn` + `Escape` — then drop the `.uf2` onto the `RPI-RP2` drive that appears, or
run `qmk flash` instead of `qmk compile`.

## Fn layer

`Fn` sits on the Menu key, which is unused on most ISO-DE setups. The Menu key
itself stays reachable as `Fn` + Menu.

| Key | Function |
|---|---|
| `Fn` + `Esc` | Bootloader |
| `Fn` + `F1` | Backlight on/off |
| `Fn` + `F2` / `F3` | Dimmer / brighter |
| `Fn` + `F4` | Breathing on/off |

## Hardware mapping

21 columns × 6 rows, diodes `COL2ROW`. All 30 GPIOs are in use: `GP0`–`GP5` and
`GP7`–`GP20` plus `GP24` for the columns, `GP6` and `GP25`–`GP29` for the rows,
`GP21` backlight, `GP22` Caps Lock, `GP23` Num Lock.

The backlight runs on PWM. On RP2040 a GPIO maps to slice `(n / 2) % 8`, channel
A on even and B on odd pins — `GP21` therefore needs `PWMD2` and channel B,
which is what `config.h` sets, with `halconf.h` and `mcuconf.h` enabling the
peripheral. Without those three files the build falls back to an STM32 default
(`PWMD4`) and fails.

## USB VID/PID

`0xFEED` / `0x0001` are QMK's placeholders and collide with plenty of other
boards. They are fine for testing; anyone producing these in numbers should
register their own.
