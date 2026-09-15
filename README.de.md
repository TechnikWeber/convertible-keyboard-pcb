[English](README.md) · **Deutsch**

# keyboard-fullsize

> ### 🔎 Gehäuse-Designer gesucht
> Die Platine dieser Tastatur entsteht gerade, ein Gehäuse gibt es noch nicht.
> Wenn du Tastaturgehäuse entwirfst — 3D-gedruckt, CNC-gefräst oder
> lasergeschnitten — und Lust auf dieses Projekt hast, eröffne gern ein
> [Issue](https://github.com/TechnikWeber/keyboard-fullsize/issues).
> Platinenumriss, Befestigungslöcher und die Lage der USB-C-Buchse stehen noch
> nicht fest und können sich nach deinem Gehäuse richten.

Eine mechanische Full-Size-Tastatur mit deutschem ISO-Layout, von Grund auf in
KiCad entworfen.

> **Status: am Anfang.** Die Tastenmatrix ist erzeugt und jeder Schalter hat
> seinen endgültigen Footprint. Controller, Platinenumriss und Routing fehlen
> noch. Gefertigt wurde bisher nichts.

## Eckdaten

- 105 Tasten, Full-Size ISO-DE: Funktionsreihe, Navigationsblock, Ziffernblock
- Cherry-MX-kompatible Schalter, gelötet, mit Stabilisator-Bohrungen für alle
  Tasten ab 2u
- ANSI-Alternativen für Enter, linkes Shift und Backslash geplant
- 6 × 21 Diodenmatrix (SOD-123)
- Geplant: RP2040 als Controller, USB-C
- Tastenfeld: 428,6 × 123,8 mm (22,5 × 6,5 u)

## Repository

| Pfad | Inhalt |
|---|---|
| `keyboard-fullsize.kicad_pro` / `.kicad_sch` / `.kicad_pcb` | KiCad-10-Projekt |
| `fp-lib-table` | Footprint-Bibliothekstabelle des Projekts |
| `lib/MX_Alps_Hybrid` | Schalter-Footprints von ai03 (Git-Submodul) |

Die Footprints liegen in einem Submodul, deshalb so klonen:

```bash
git clone --recurse-submodules https://github.com/TechnikWeber/keyboard-fullsize.git
```

## Fahrplan

- [x] Tastenmatrix und Dioden
- [x] Footprints für alle Tastengrößen
- [ ] ANSI-Alternativpositionen
- [ ] Controller-Blatt: RP2040, Flash, Quarz, LDO, USB-C, ESD-Schutz
- [ ] Platinenumriss und Befestigungslöcher (gemeinsam mit dem Gehäuse)
- [ ] Routing, DRC, Fertigungsdaten
- [ ] Firmware (QMK)

## Lizenz

CC BY-NC-SA 4.0 — siehe [LICENSE](LICENSE). Die Schalter-Footprints in
`lib/MX_Alps_Hybrid` stammen von ai03 und stehen unter der MIT-Lizenz.
