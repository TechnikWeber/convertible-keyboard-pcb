**English** · [Deutsch](README.de.md)

# keyboard-fullsize

> ### 🔎 Looking for a case designer
> This keyboard has a PCB in progress but no case yet. If you design keyboard
> cases — 3D-printed, CNC-milled or laser-cut — and would like to take this on,
> please [open an issue](https://github.com/TechnikWeber/keyboard-fullsize/issues).
> Board outline, mounting holes and the USB-C position are not fixed yet, so they
> can be shaped around your case design.

A full-size mechanical keyboard with a German ISO layout, designed from scratch
in KiCad.

> **Status: early.** The key matrix is generated and every switch has its final
> footprint. The controller, board outline and routing are still to do. Nothing
> has been manufactured yet.

## Specs

- 105 keys, full-size ISO-DE: function row, navigation cluster, numpad
- Cherry MX-compatible switches, soldered, with stabilizer holes on all keys of
  2u and wider
- ANSI alternatives planned for Enter, left Shift and backslash
- 6 × 21 diode matrix (SOD-123)
- Planned: RP2040 controller, USB-C
- Key field: 428.6 × 123.8 mm (22.5 × 6.5 u)

## Repository

| Path | Contents |
|---|---|
| `keyboard-fullsize.kicad_pro` / `.kicad_sch` / `.kicad_pcb` | KiCad 10 project |
| `fp-lib-table` | Project footprint library table |
| `lib/MX_Alps_Hybrid` | Switch footprints by ai03 (git submodule) |

The footprints come from a submodule, so clone with:

```bash
git clone --recurse-submodules https://github.com/TechnikWeber/keyboard-fullsize.git
```

## Roadmap

- [x] Key matrix and diodes
- [x] Footprints for all key sizes
- [ ] ANSI alternative positions
- [ ] Controller sheet: RP2040, flash, crystal, LDO, USB-C, ESD protection
- [ ] Board outline and mounting holes (together with the case)
- [ ] Routing, DRC, manufacturing files
- [ ] Firmware (QMK)

## Licence

CC BY-NC-SA 4.0 — see [LICENSE](LICENSE). The switch footprints in
`lib/MX_Alps_Hybrid` are by ai03 under the MIT License.
