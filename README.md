**English** · [Deutsch](README.de.md)

# convertible-keyboard-pcb

> ### 🔎 Looking for a case designer
> This keyboard has a PCB in progress but no case yet. If you design keyboard
> cases — 3D-printed, CNC-milled or laser-cut — and would like to take this on,
> please [open an issue](https://github.com/TechnikWeber/convertible-keyboard-pcb/issues).
> A first board outline exists (key field + 1.3 mm), but outline, mounting holes
> and the USB-C position can still be shaped around your case design — for the full-size board, the TKL, or
> both. The same goes for where exactly the lock indicators sit. The USB port
> can sit on the PCB or on a Unified Daughterboard (Pico-EZmate or JST-SH).

**One keyboard PCB, two sizes.** A full-size ISO-DE / ANSI board whose numpad
snaps off along a breakaway line. What remains is a complete tenkeyless (TKL)
keyboard — same PCB, same controller, same firmware.

This is not meant to be yet another one-off DIY keyboard. The goal is a
standardised core design that others can build on: cheap and simple to make, but
clean and modern — current KiCad, QMK, USB-C and parts that can actually be
bought. A case, lighting or layout variants build on this core instead of
bending it into something else.

> **Status: early.** The schematic is complete — key matrix, ANSI alternatives,
> backlight and controller — and every part has its footprint on the PCB.
> Controller, USB and drivers are placed on the back, board outline and breakaway
> line are drawn; mounting holes and routing are still to do.
> Nothing has been manufactured yet.

## Full-size or TKL

- The numpad sits on the right-hand side behind a 2 mm slot, held by four
  mouse-bite tabs (perforated breakaway bridges). Each tab keeps a hole-free
  channel in the middle for the traces that cross over.
- Controller, USB-C and the drivers for backlight and lock indicators all sit
  on the TKL part. Only the numpad's matrix, backlight and indicator lines cross the breakaway
  line.
- Snap the numpad off and the TKL keeps working unchanged — the numpad keys are
  simply gone. The firmware describes both layouts.
- The lock indicators above the numpad go with it – without a numpad Num Lock is
  pointless anyway; for the TKL populate the Caps Lock indicator above Page Up.
- The snapped-off numpad has no controller of its own and does not work on its
  own.

## Specs

- Full-size: 105 keys ISO-DE, key field 428.6 × 123.8 mm (22.5 × 6.5 u)
- TKL: 88 keys ISO-DE, key field 347.7 × 123.8 mm (18.25 × 6.5 u)
- ISO-DE and ANSI on one PCB: alternative positions for Enter, left Shift and
  backslash (the ANSI backslash is the only key without an LED)
- Cherry MX-compatible switches, soldered, with stabilizer holes on all keys of
  2u and wider
- 6 × 21 diode matrix (SOD-123)
- RP2040 controller with 16 Mbit QSPI flash, RESET and BOOTSEL buttons and SWD
  test pads
- USB-C (USB 2.0) on the board with ESD protection, 500 mA polyfuse and a 3.3 V
  LDO – or a Unified Daughterboard instead: connectors for Molex Pico-EZmate
  (uDB S1, C4, C5-EZM) and JST-SH (uDB C3, C5-JSH) are provided, not populated
- Single-colour backlight with reverse-mount 1206 LEDs on the back of the PCB
  (white, XINGLIGHT XL-3216UWC-FB), machine-assembled; switched, dimmed and
  "breathing" via QMK. A THT-LED variant uses the same design with different LED
  footprints
- Checked alternative backlight LEDs for the same footprint: MEIHUA MHT151WDT
  (LCSC C401114) and TUOZHAN P2-1206WYCS2-0.9T-F (LCSC C2827252)
- Caps Lock and Num Lock indicators (0805) above the numpad; for the TKL a Caps
  Lock indicator above Page Up is prepared but not populated
- All 30 RP2040 GPIOs in use: 27 matrix lines, backlight PWM, Caps Lock and
  Num Lock

## Repository

| Path | Contents |
|---|---|
| `convertible-keyboard-pcb.kicad_pro` / `.kicad_pcb` | KiCad 10 project and PCB |
| `convertible-keyboard-pcb.kicad_sch` | Root sheet: key matrix and ANSI alternatives |
| `backlight.kicad_sch` | Key LEDs, series resistors and MOSFET drivers |
| `mcu.kicad_sch` | RP2040, flash, crystal, USB-C and power |
| `lib/keyboard.pretty` | Project footprints: reverse-mount LED, THT LED for the variant |
| `fp-lib-table`, `convertible-keyboard-pcb.kicad_dru` | Footprint library table, design rule for the LED cutouts |
| `lib/MX_Alps_Hybrid` | Switch footprints by ai03 (git submodule) |
| `tools/` | Scripts that generated the sheets and updated the PCB – see [tools/README.md](tools/README.md) |
| `docs/production/` | Gerbers, drill file, BOM and placement file for JLCPCB |
| `firmware/` | QMK keyboard definition and keymaps – see [firmware/README.md](firmware/README.md) |

The footprints come from a submodule, so clone with:

```bash
git clone --recurse-submodules https://github.com/TechnikWeber/convertible-keyboard-pcb.git
```

## What it looks like

These renders let you review the design without installing KiCad.

### Key layouts

Everything is built around these two: ISO-DE with 105 keys and ANSI with 104. The board carries both. The ANSI
positions are alternative footprints that stay unpopulated on an ISO build, and the other way round.

![ISO-DE layout](docs/images/layout-iso.png)

![ANSI layout](docs/images/layout-ansi.png)

### Board in 3D

Switch side: through holes for the switches and their stabilisers, no components. Note the breakaway line in
front of the numpad.

![3D, switch side](docs/images/pcb-3d-front.png)

Component side: nearly everything sits here. Diodes and resistors per key, the reverse-mount LEDs shining
through their cutouts, and the controller in the gap between F4 and F5. The only parts on the other side are
the two lock indicators above the numpad.

![3D, component side](docs/images/pcb-3d-back.png)

### Board

Both copper layers, zone fills hidden so the traces stay readable. The numpad on the right snaps off along the
breakaway line; only matrix lines, +5V, BL_K and the two lock-LED lines cross it, through the four tabs.

![Both copper layers](docs/images/pcb-both-layers.png)

The controller sits in the gap between F4 and F5. Column and row buses run in fixed lanes and each one ends on a
via that drops onto the column trace of its key. Every SMD part in this area is on the back.

![Controller area](docs/images/pcb-controller.png)

Front (switch side, mostly through holes and the key matrix) and back (all components, reverse-mount LEDs):

![Front](docs/images/pcb-front.png)

![Back](docs/images/pcb-back.png)

### Schematic

Key matrix with the ANSI alternatives:

![Matrix](docs/images/schematic-matrix.png)

Backlight, lock indicators and their drivers:

![Backlight](docs/images/schematic-backlight.png)

Controller: RP2040, flash, crystal, LDO, USB-C with ESD protection, daughterboard connectors, buttons, test pads:

![Controller](docs/images/schematic-mcu.png)

## Having it made

Gerbers, drill file, BOM and placement file for JLCPCB are in
[`docs/production/`](docs/production/README.md), all generated from the KiCad project. The board is
431.225 × 126.425 mm on two layers. 371 parts are machine-assembled; the 108 MX switches are soldered by
hand, and three parts are deliberately left unpopulated.

Nothing here has been built in hardware yet. The files pass DRC and schematic parity, nothing more —
review them before you spend money.

## Roadmap

- [x] Key matrix and diodes
- [x] Footprints for all key sizes
- [x] ANSI alternative positions
- [x] Single-colour backlight
- [x] Controller sheet: RP2040, flash, crystal, LDO, USB-C, ESD protection
- [x] Breakaway line for the numpad
- [x] Board outline (first draft)
- [x] Mounting holes: 14 × M2, placed in the free areas; final positions together with the case designer
- [x] Placement of controller, USB and drivers (preliminary)
- [x] Routing complete: key matrix and controller area (DRC clean, schematic parity clean, no open nets)
- [x] Manufacturing files for JLCPCB: gerbers, drill, BOM and placement file, an LCSC number on every part
- [x] Firmware (QMK): four layouts (full-size and TKL, each ISO and ANSI), matrix generated from the
      board file, backlight and lock indicators; compiles, not yet run on hardware

## Licence

CC BY-NC-SA 4.0 — see [LICENSE](LICENSE). The switch footprints in
`lib/MX_Alps_Hybrid` are by ai03 under the MIT License;
the THT LED footprints in `lib/keyboard.pretty` use their pad geometry.
