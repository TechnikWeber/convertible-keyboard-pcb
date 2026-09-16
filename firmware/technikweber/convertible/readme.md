# convertible-keyboard-pcb

A full-size ISO-DE / ANSI keyboard whose numpad snaps off along a breakaway
line, leaving a complete TKL. Same PCB, same controller, same firmware — only
the layout macro changes.

* Keyboard maintainer: [TechnikWeber](https://github.com/TechnikWeber)
* Hardware supported: convertible-keyboard-pcb (RP2040)
* Hardware availability: [PCB sources and production files](https://github.com/TechnikWeber/convertible-keyboard-pcb)

The matrix assignment and the key order in every layout macro are generated from
the KiCad board file, not written by hand.

| Layout | Keys | When to use |
|---|---|---|
| `LAYOUT_fullsize_iso` | 105 | Full-size board, ISO (default keymap) |
| `LAYOUT_fullsize_ansi` | 104 | Full-size board, ANSI |
| `LAYOUT_tkl_iso` | 88 | Numpad snapped off, ISO |
| `LAYOUT_tkl_ansi` | 87 | Numpad snapped off, ANSI |

Make example for this keyboard (after setting up your build environment):

    qmk compile -kb technikweber/convertible -km default

Flashing example for this keyboard:

    qmk flash -kb technikweber/convertible -km default

See the [build environment setup](https://docs.qmk.fm/#/getting_started_build_tools)
and the [make instructions](https://docs.qmk.fm/#/getting_started_make_guide) for
more information. Brand new to QMK? Start with our [Complete Newbs Guide](https://docs.qmk.fm/#/newbs).

## Bootloader

Enter the bootloader in three ways:

* **Bootmagic reset**: hold Escape and plug in the keyboard
* **Physical reset button**: press `SW201` on the back of the PCB, or hold
  `SW202` (BOOTSEL) while plugging in
* **Keycode in layout**: press `Fn` + `Escape`

## Fn layer

`Fn` sits on the Menu key — it is unused on most ISO-DE setups, so nothing of
value is lost. On the Fn layer:

| Key | Function |
|---|---|
| `Fn` + `Esc` | Enter the bootloader for flashing |
| `Fn` + `F1` | Backlight on/off |
| `Fn` + `F2` / `F3` | Backlight dimmer / brighter |
| `Fn` + `F4` | Backlight breathing on/off |

## Hardware notes

The backlight is a single white LED per key on `GP21`, driven through a MOSFET;
with 1 kΩ series resistors the whole field draws roughly 170 mA, which keeps the
board inside the USB budget. Caps Lock and Num Lock indicators sit on `GP22` and
`GP23`. There is no Scroll Lock indicator.
