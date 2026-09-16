**English** · [Deutsch](README.de.md)

# Production files (JLCPCB)

Everything in this folder is generated from the KiCad project in the repository
root. Do not edit these files by hand — regenerate them (see the bottom of this
page) whenever the board changes.

> **Not yet ordered or verified in hardware.** These files have passed DRC and
> schematic parity, but no prototype has been built from them. Review them
> before spending money.

| File | What it is |
|---|---|
| `gerber.zip` | Gerber X1 + Excellon drill, ready to upload |
| `BOM.csv` | Bill of materials, JLCPCB column names |
| `CPL.csv` | Component placement (pick and place) |

## Board

| | |
|---|---|
| Size | 431.225 × 126.425 mm |
| Layers | 2 (1 oz copper) |
| Min. track / clearance | 0.2 mm / 0.15 mm |
| Min. drill | 0.3 mm (vias), NPTH down to 0.5 mm (mouse bites) |
| Mounting holes | 14 × Ø 2.2 mm for M2, non-plated |
| Board outline | includes the breakaway slot and its four mouse-bite tabs |

The `.drl` file contains plated and non-plated holes together — pick
**mixed plating** if JLCPCB asks. Drill origin is absolute, so the drill file
and the gerbers share the gerbers' coordinate system.

## Assembly

371 parts in 25 groups. **369 sit on the bottom side, 2 on the top** (`D126`,
`D128`, the Num-Lock and Caps-Lock indicators above the numpad). That makes it a
double-sided assembly job, which costs noticeably more than a single-sided one.
If you do not need the lock indicators, drop those two parts and the order
becomes bottom-side only.

Deliberately **not** in the BOM or CPL:

- `SW1`–`SW108` — MX switches are hand-soldered, not assembled by JLCPCB.
- `J2`, `J3` — Unified Daughterboard connectors, DNP. Fit one of them *instead*
  of `J1` if you want the USB port on a daughterboard.
- `D122` — Caps-Lock indicator for the TKL variant, DNP. Only useful once the
  numpad has been snapped off; solder it by hand then.

The key LEDs (`LED1`–`LED108`, minus `LED106`) are reverse-mount parts that
shine *through* the board, so they sit on the bottom side like everything else.

## What it costs

JLCPCB's minimum order is **5 boards**. Prices checked on 2026-09-16, in US
dollars, shipping included, customs and import VAT **not** included:

| Order | Price | Per board |
|---|---|---|
| 5 bare PCBs, Standard Global Direct Line | $45 | $9 |
| 5 PCBs, 2 of them assembled, Euro Packet | $112 | — |

The assembled order is the honest number to plan with: you cannot buy a single
assembled board, and the two populated ones carry most of the $112. Switches,
keycaps, stabilisers and a case are on top of this and are not part of any
JLCPCB order.

## Ordering

1. **PCB:** upload `gerber.zip`. Leave the defaults;
   2 layers, 1.6 mm, HASL is fine. The breakaway slot and mouse bites are part
   of the outline, so no extra instructions are needed.
2. **Assembly:** turn it on, choose **both sides**, upload `BOM.csv` and
   `CPL.csv`. JLCPCB reads the LCSC number from the `LCSC Part #` column, so the
   parts should be matched automatically.
3. Check the placement preview, especially the rotation of `U1` (RP2040),
   `U3` (LDO), `U4` (ESD array) and the diodes. Rotations in `CPL.csv` follow
   KiCad's convention, which JLCPCB usually — but not always — agrees with.

## Regenerating

From the repository root, with KiCad 10 installed:

```sh
kicad-cli pcb drc --refill-zones --save-board --schematic-parity \
    --format json -o /tmp/drc.json convertible-keyboard-pcb.kicad_pcb
kicad-cli pcb export gerbers --no-x2 --subtract-soldermask \
    -o /tmp/gerber convertible-keyboard-pcb.kicad_pcb
kicad-cli pcb export drill --drill-origin absolute --excellon-units mm \
    --generate-map --map-format gerberx2 -o /tmp/gerber convertible-keyboard-pcb.kicad_pcb
```

Always refill the zones first — a stale zone fill produces phantom clearance
errors and, worse, gerbers that do not match the board you checked.

**The uploaded archive must not have `convert` in its name.** JLCPCB rejects
such uploads, which is why it is called `gerber.zip` and not
`convertible-keyboard-pcb-gerber.zip`. The twelve files *inside* the archive
keep the project name and are accepted as they are.

`BOM.csv` and `CPL.csv` come from `kicad-cli sch export bom` and
`kicad-cli pcb export pos`, with the DNP parts and the hand-soldered switches
removed and the columns renamed to what JLCPCB expects. The Y coordinates in
`CPL.csv` are negative, matching the gerbers' coordinate system — do not flip
the sign.
