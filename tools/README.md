**English** · [Deutsch](README.de.md)

# tools

Scripts that generated the schematic sheets and updated the PCB for the ANSI
alternatives, the backlight and the controller. They are kept so the design can
be traced and built upon.

> **The KiCad files are the source of truth.** `build.sh` starts again from the
> kbplacer base commit and overwrites schematic and PCB – any manual work done in
> KiCad since then is lost. Use it on a branch, or to reproduce and extend the
> generated state before the layout begins.
>
> The generated state ends at commit `2eb5d4f`. Later changes – title blocks and
> sheet sizes, the reduced lock indicators – were made directly in KiCad.

## Pipeline

| File | What it does |
|---|---|
| `build.sh --overwrite` | Runs the three steps below; refuses to run while KiCad has the project open |
| `gen_sch.py <stage>` | Builds the schematic on top of the kbplacer root sheet (base commit `95ce8fa`). Stage 1: ANSI alternatives, 2: backlight, 3: MCU sheet. Also writes `lib/keyboard.kicad_sym` and `sym-lib-table`. UUIDs are deterministic |
| `check_sch.py` | Normalises the files (`kicad-cli sch upgrade`), runs ERC, exports the netlist and checks every generated connection against its expected net |
| `sync_pcb.py` | Updates the PCB from the netlist like "Update PCB from Schematic": swaps and adds footprints, places diodes and LED resistors next to their switch, links footprints to symbols, assigns nets, runs DRC with schematic parity |
| `place_override.json` | Diode/resistor positions that differ from the default next to the switch (ISO/ANSI collisions) |
| `kicadlib.py` | Minimal S-expression parser/serializer and symbol-library helpers |
| `analysis/` | Collision checks between ISO and ANSI footprints that led to the rotated, unlit ANSI backslash and the flipped LED pads |

## Usage

```bash
tools/build.sh --overwrite
```

Requires KiCad 10 with `kicad-cli` and the `pcbnew` Python module, and the git
history (the base files are read with `git show`). Intermediate files go to
`tools/build/`.

pcbnew gives newly added footprints fresh UUIDs, so the PCB file changes on every
run even when nothing changed electrically; the schematic files are reproduced
exactly.
