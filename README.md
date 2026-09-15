**English** · [Deutsch](README.de.md)

# convertible-keyboard-pcb

> ### 🔎 Looking for a case designer
> This keyboard has a PCB in progress but no case yet. If you design keyboard
> cases — 3D-printed, CNC-milled or laser-cut — and would like to take this on,
> please [open an issue](https://github.com/TechnikWeber/convertible-keyboard-pcb/issues).
> Board outline, mounting holes and the USB-C position are not fixed yet, so they
> can be shaped around your case design — for the full-size board, the TKL, or
> both.

**One keyboard PCB, two sizes.** A full-size ISO-DE / ANSI board whose numpad
snaps off along a breakaway line. What remains is a complete tenkeyless (TKL)
keyboard — same PCB, same controller, same firmware.

This is not meant to be yet another one-off DIY keyboard. The goal is a
standardised core design that others can build on: cheap and simple to make, but
clean and modern — current KiCad, QMK, USB-C and parts that can actually be
bought. A case, lighting or layout variants build on this core instead of
bending it into something else.

> **Status: early.** The key matrix is generated and every switch has its final
> footprint. The controller, the breakaway line, board outline and routing are
> still to do. Nothing has been manufactured yet.

## Full-size or TKL

- The numpad sits on the right-hand side, joined to the rest of the board by a
  row of mouse bites (perforated breakaway tabs).
- Controller, USB-C, backlight driver and lock indicators all sit on the TKL
  part. Only the numpad's matrix and backlight lines cross the breakaway line.
- Snap the numpad off and the TKL keeps working unchanged — the numpad keys are
  simply gone. The firmware describes both layouts.
- The snapped-off numpad has no controller of its own and does not work on its
  own.

## Specs

- Full-size: 105 keys ISO-DE, key field 428.6 × 123.8 mm (22.5 × 6.5 u)
- TKL: 88 keys ISO-DE, key field 347.7 × 123.8 mm (18.25 × 6.5 u)
- ISO-DE and ANSI on one PCB: alternative positions for Enter, left Shift and
  backslash
- Cherry MX-compatible switches, soldered, with stabilizer holes on all keys of
  2u and wider
- 6 × 21 diode matrix (SOD-123)
- RP2040 controller, USB-C
- Single-colour backlight: resistors and MOSFET on the board, the LEDs themselves
  are optional — switched, dimmed and "breathing" via QMK
- Caps Lock and Num Lock indicators

## Repository

| Path | Contents |
|---|---|
| `convertible-keyboard-pcb.kicad_pro` / `.kicad_sch` / `.kicad_pcb` | KiCad 10 project |
| `fp-lib-table` | Project footprint library table |
| `lib/MX_Alps_Hybrid` | Switch footprints by ai03 (git submodule) |

The footprints come from a submodule, so clone with:

```bash
git clone --recurse-submodules https://github.com/TechnikWeber/convertible-keyboard-pcb.git
```

## Roadmap

- [x] Key matrix and diodes
- [x] Footprints for all key sizes
- [ ] ANSI alternative positions
- [ ] Single-colour backlight
- [ ] Controller sheet: RP2040, flash, crystal, LDO, USB-C, ESD protection
- [ ] Breakaway line for the numpad
- [ ] Board outline and mounting holes (together with the case)
- [ ] Routing, DRC, manufacturing files
- [ ] Firmware (QMK) with full-size and TKL layouts

## Licence

CC BY-NC-SA 4.0 — see [LICENSE](LICENSE). The switch footprints in
`lib/MX_Alps_Hybrid` are by ai03 under the MIT License.
