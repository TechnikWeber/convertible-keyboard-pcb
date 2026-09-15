[English](README.md) · **Deutsch**

# convertible-keyboard-pcb

> ### 🔎 Gehäuse-Designer gesucht
> Die Platine dieser Tastatur entsteht gerade, ein Gehäuse gibt es noch nicht.
> Wenn du Tastaturgehäuse entwirfst — 3D-gedruckt, CNC-gefräst oder
> lasergeschnitten — und Lust auf dieses Projekt hast, eröffne gern ein
> [Issue](https://github.com/TechnikWeber/convertible-keyboard-pcb/issues).
> Platinenumriss, Befestigungslöcher und die Lage der USB-C-Buchse stehen noch
> nicht fest und können sich nach deinem Gehäuse richten — für die
> Full-Size-Variante, die TKL oder beide.

**Eine Tastaturplatine, zwei Größen.** Eine Full-Size-Platine für ISO-DE und
ANSI, deren Ziffernblock sich an einer Sollbruchstelle abbrechen lässt. Übrig
bleibt eine vollständige Tenkeyless-Tastatur (TKL) — gleiche Platine, gleicher
Controller, gleiche Firmware.

Das soll kein weiteres Einmal-DIY-Keyboard werden. Ziel ist ein standardisiertes
Kernprojekt, auf dem andere aufbauen können: günstig und einfach zu fertigen,
aber sauber und modern — mit aktuellem KiCad, QMK, USB-C und Bauteilen, die man
wirklich kaufen kann. Gehäuse, Beleuchtung oder Layout-Varianten setzen auf
diesem Kern auf, statt ihn zu verbiegen.

> **Status: am Anfang.** Die Tastenmatrix ist erzeugt und jeder Schalter hat
> seinen endgültigen Footprint. Controller, Sollbruchstelle, Platinenumriss und
> Routing fehlen noch. Gefertigt wurde bisher nichts.

## Full-Size oder TKL

- Der Ziffernblock sitzt rechts und hängt über eine Reihe Mouse Bites
  (perforierte Bruchstege) am Rest der Platine.
- Controller, USB-C, Beleuchtungstreiber und Lock-Anzeigen liegen alle auf dem
  TKL-Teil. Nur die Matrix- und Beleuchtungsleitungen des Ziffernblocks laufen
  über die Bruchkante.
- Ziffernblock abbrechen, und die TKL funktioniert unverändert weiter — die
  Ziffernblocktasten gibt es dann einfach nicht mehr. Die Firmware beschreibt
  beide Layouts.
- Der abgebrochene Ziffernblock hat keinen eigenen Controller und funktioniert
  allein nicht.

## Eckdaten

- Full-Size: 105 Tasten ISO-DE, Tastenfeld 428,6 × 123,8 mm (22,5 × 6,5 u)
- TKL: 88 Tasten ISO-DE, Tastenfeld 347,7 × 123,8 mm (18,25 × 6,5 u)
- ISO-DE und ANSI auf einer Platine: Alternativpositionen für Enter, linkes
  Shift und Backslash
- Cherry-MX-kompatible Schalter, gelötet, mit Stabilisator-Bohrungen für alle
  Tasten ab 2u
- 6 × 21 Diodenmatrix (SOD-123)
- RP2040 als Controller, USB-C
- Einfarbige Hintergrundbeleuchtung: Widerstände und MOSFET sind auf der Platine,
  die LEDs selbst sind optional — über QMK schaltbar, dimmbar und mit „Breathing“
- Anzeige für Caps Lock und Num Lock

## Repository

| Pfad | Inhalt |
|---|---|
| `convertible-keyboard-pcb.kicad_pro` / `.kicad_sch` / `.kicad_pcb` | KiCad-10-Projekt |
| `fp-lib-table` | Footprint-Bibliothekstabelle des Projekts |
| `lib/MX_Alps_Hybrid` | Schalter-Footprints von ai03 (Git-Submodul) |

Die Footprints liegen in einem Submodul, deshalb so klonen:

```bash
git clone --recurse-submodules https://github.com/TechnikWeber/convertible-keyboard-pcb.git
```

## Fahrplan

- [x] Tastenmatrix und Dioden
- [x] Footprints für alle Tastengrößen
- [ ] ANSI-Alternativpositionen
- [ ] Einfarbige Hintergrundbeleuchtung
- [ ] Controller-Blatt: RP2040, Flash, Quarz, LDO, USB-C, ESD-Schutz
- [ ] Sollbruchstelle für den Ziffernblock
- [ ] Platinenumriss und Befestigungslöcher (gemeinsam mit dem Gehäuse)
- [ ] Routing, DRC, Fertigungsdaten
- [ ] Firmware (QMK) mit Full-Size- und TKL-Layout

## Lizenz

CC BY-NC-SA 4.0 — siehe [LICENSE](LICENSE). Die Schalter-Footprints in
`lib/MX_Alps_Hybrid` stammen von ai03 und stehen unter der MIT-Lizenz.
