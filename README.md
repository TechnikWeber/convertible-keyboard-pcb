**English** · [Deutsch](README.de.md)

# convertible-keyboard-pcb

> ### 🔎 Looking for a case designer
> This keyboard has a PCB in progress but no case yet. If you design keyboard
> cases — 3D-printed, CNC-milled or laser-cut — and would like to take this on,
> please [open an issue](https://github.com/TechnikWeber/convertible-keyboard-pcb/issues).
> Board outline, mounting holes and the USB-C position are not fixed yet, so they
> can be shaped around your case design — for the full-size board, the TKL, or
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
> Controller, USB and drivers are placed on the back; the breakaway line, board
> outline and routing are still to do.
> Nothing has been manufactured yet.

## Full-size or TKL

- The numpad sits on the right-hand side, joined to the rest of the board by a
  row of mouse bites (perforated breakaway tabs).
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

The footprints come from a submodule, so clone with:

```bash
git clone --recurse-submodules https://github.com/TechnikWeber/convertible-keyboard-pcb.git
```

## Roadmap

- [x] Key matrix and diodes
- [x] Footprints for all key sizes
- [x] ANSI alternative positions
- [x] Single-colour backlight
- [x] Controller sheet: RP2040, flash, crystal, LDO, USB-C, ESD protection
- [ ] Breakaway line for the numpad
- [ ] Board outline and mounting holes (together with the case)
- [x] Placement of controller, USB and drivers (preliminary)
- [ ] Routing, DRC, manufacturing files
- [ ] Firmware (QMK) with full-size and TKL layouts

## Licence

CC BY-NC-SA 4.0 — see [LICENSE](LICENSE). The switch footprints in
`lib/MX_Alps_Hybrid` are by ai03 under the MIT License;
the THT LED footprints in `lib/keyboard.pretty` use their pad geometry.
