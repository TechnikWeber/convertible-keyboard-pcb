[English](README.md) · **Deutsch**

# convertible-keyboard-pcb

> ### 🔎 Gehäuse-Designer gesucht
> Die Platine dieser Tastatur entsteht gerade, ein Gehäuse gibt es noch nicht.
> Wenn du Tastaturgehäuse entwirfst — 3D-gedruckt, CNC-gefräst oder
> lasergeschnitten — und Lust auf dieses Projekt hast, eröffne gern ein
> [Issue](https://github.com/TechnikWeber/convertible-keyboard-pcb/issues).
> Platinenumriss, Befestigungslöcher und die Lage der USB-C-Buchse stehen noch
> nicht fest und können sich nach deinem Gehäuse richten — für die
> Full-Size-Variante, die TKL oder beide. Dasselbe gilt für Position und Bauform
> der Lock-Anzeigen.

**Eine Tastaturplatine, zwei Größen.** Eine Full-Size-Platine für ISO-DE und
ANSI, deren Ziffernblock sich an einer Sollbruchstelle abbrechen lässt. Übrig
bleibt eine vollständige Tenkeyless-Tastatur (TKL) — gleiche Platine, gleicher
Controller, gleiche Firmware.

Das soll kein weiteres Einmal-DIY-Keyboard werden. Ziel ist ein standardisiertes
Kernprojekt, auf dem andere aufbauen können: günstig und einfach zu fertigen,
aber sauber und modern — mit aktuellem KiCad, QMK, USB-C und Bauteilen, die man
wirklich kaufen kann. Gehäuse, Beleuchtung oder Layout-Varianten setzen auf
diesem Kern auf, statt ihn zu verbiegen.

> **Status: am Anfang.** Der Schaltplan ist vollständig — Tastenmatrix,
> ANSI-Alternativen, Beleuchtung und Controller — und jedes Bauteil hat seinen
> Footprint auf der Platine. Platzierung, Sollbruchstelle, Platinenumriss und
> Routing fehlen noch. Gefertigt wurde bisher nichts.

## Full-Size oder TKL

- Der Ziffernblock sitzt rechts und hängt über eine Reihe Mouse Bites
  (perforierte Bruchstege) am Rest der Platine.
- Controller, USB-C sowie die Treiber für Beleuchtung und Lock-Anzeigen liegen
  alle auf dem TKL-Teil. Nur die Matrix-, Beleuchtungs- und
  Anzeigeleitungen des Ziffernblocks laufen über die Bruchkante.
- Ziffernblock abbrechen, und die TKL funktioniert unverändert weiter — die
  Ziffernblocktasten gibt es dann einfach nicht mehr. Die Firmware beschreibt
  beide Layouts.
- Die klassischen Lock-Anzeigen über dem Ziffernblock gehen mit; für die TKL
  bestückt man das zweite Paar über dem Navigationsblock.
- Der abgebrochene Ziffernblock hat keinen eigenen Controller und funktioniert
  allein nicht.

## Eckdaten

- Full-Size: 105 Tasten ISO-DE, Tastenfeld 428,6 × 123,8 mm (22,5 × 6,5 u)
- TKL: 88 Tasten ISO-DE, Tastenfeld 347,7 × 123,8 mm (18,25 × 6,5 u)
- ISO-DE und ANSI auf einer Platine: Alternativpositionen für Enter, linkes
  Shift und Backslash (der ANSI-Backslash ist die einzige Taste ohne LED)
- Cherry-MX-kompatible Schalter, gelötet, mit Stabilisator-Bohrungen für alle
  Tasten ab 2u
- 6 × 21 Diodenmatrix (SOD-123)
- RP2040 als Controller mit 16-Mbit-QSPI-Flash, RESET- und BOOTSEL-Taster und
  SWD-Testpads
- USB-C (USB 2.0) mit ESD-Schutz, 500-mA-Polyfuse und 3,3-V-LDO
- Einfarbige Hintergrundbeleuchtung: Widerstände und MOSFET sind auf der Platine,
  die LEDs selbst sind optional — über QMK schaltbar, dimmbar und mit „Breathing“
- Anzeige für Caps Lock und Num Lock an zwei Stellen: klassisch über dem
  Ziffernblock (standardmäßig bestückt) und über dem Navigationsblock für die TKL
  (vorgesehen, nicht bestückt) – jeweils als 3-mm-THT oder 0805-SMD, bestückt
  wird, was das Gehäuse braucht
- Alle 30 GPIOs des RP2040 belegt: 27 Matrixleitungen, Beleuchtungs-PWM,
  Caps Lock und Num Lock

## Repository

| Pfad | Inhalt |
|---|---|
| `convertible-keyboard-pcb.kicad_pro` / `.kicad_pcb` | KiCad-10-Projekt und Platine |
| `convertible-keyboard-pcb.kicad_sch` | Hauptblatt: Tastenmatrix und ANSI-Alternativen |
| `backlight.kicad_sch` | Tasten-LEDs, Vorwiderstände und MOSFET-Treiber |
| `mcu.kicad_sch` | RP2040, Flash, Quarz, USB-C und Stromversorgung |
| `lib/keyboard.kicad_sym`, `lib/keyboard.pretty` | Projektsymbol (Schalter mit LED) und Footprint |
| `sym-lib-table`, `fp-lib-table` | Bibliothekstabellen des Projekts |
| `lib/MX_Alps_Hybrid` | Schalter-Footprints von ai03 (Git-Submodul) |
| `tools/` | Skripte, die die Blätter erzeugt und die Platine aktualisiert haben – siehe [tools/README.de.md](tools/README.de.md) |

Die Footprints liegen in einem Submodul, deshalb so klonen:

```bash
git clone --recurse-submodules https://github.com/TechnikWeber/convertible-keyboard-pcb.git
```

## Fahrplan

- [x] Tastenmatrix und Dioden
- [x] Footprints für alle Tastengrößen
- [x] ANSI-Alternativpositionen
- [x] Einfarbige Hintergrundbeleuchtung
- [x] Controller-Blatt: RP2040, Flash, Quarz, LDO, USB-C, ESD-Schutz
- [ ] Sollbruchstelle für den Ziffernblock
- [ ] Platinenumriss und Befestigungslöcher (gemeinsam mit dem Gehäuse)
- [ ] Platzierung, Routing, DRC, Fertigungsdaten
- [ ] Firmware (QMK) mit Full-Size- und TKL-Layout

## Lizenz

CC BY-NC-SA 4.0 — siehe [LICENSE](LICENSE). Die Schalter-Footprints in
`lib/MX_Alps_Hybrid` stammen von ai03 und stehen unter der MIT-Lizenz;
`lib/keyboard.pretty/MXOnly-ISO-FLIPPED` ist davon abgeleitet.
