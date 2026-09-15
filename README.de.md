[English](README.md) · **Deutsch**

# keyboard-fullsize

> ### 🔎 Gehäuse-Designer gesucht
> Die Platine dieser Tastatur entsteht gerade, ein Gehäuse gibt es noch nicht.
> Wenn du Tastaturgehäuse entwirfst — 3D-gedruckt, CNC-gefräst oder
> lasergeschnitten — und Lust auf dieses Projekt hast, eröffne gern ein
> [Issue](https://github.com/TechnikWeber/keyboard-fullsize/issues).
> Platinenumriss, Befestigungslöcher und die Lage der USB-C-Buchse stehen noch
> nicht fest und können sich nach deinem Gehäuse richten.

Eine mechanische Full-Size-Tastatur für ISO-DE und ANSI, von Grund auf in KiCad
entworfen.

Das soll kein weiteres Einmal-DIY-Keyboard werden. Ziel ist ein standardisiertes
Full-Size-Kernprojekt, auf dem andere aufbauen können: günstig und einfach zu
fertigen, aber sauber und modern — mit aktuellem KiCad, QMK, USB-C und Bauteilen,
die man wirklich kaufen kann. Gehäuse, Beleuchtung oder Layout-Varianten setzen
auf diesem Kern auf, statt ihn zu verbiegen.

> **Status: am Anfang.** Die Tastenmatrix ist erzeugt und jeder Schalter hat
> seinen endgültigen Footprint. Controller, Platinenumriss und Routing fehlen
> noch. Gefertigt wurde bisher nichts.

## Eckdaten

- 105 Tasten, Full-Size ISO-DE: Funktionsreihe, Navigationsblock, Ziffernblock
- Cherry-MX-kompatible Schalter, gelötet, mit Stabilisator-Bohrungen für alle
  Tasten ab 2u
- ISO-DE und ANSI auf einer Platine: Alternativpositionen für Enter, linkes
  Shift und Backslash (in Arbeit)
- 6 × 21 Diodenmatrix (SOD-123)
- Geplant: RP2040 als Controller, USB-C
- Geplant: einfarbige Hintergrundbeleuchtung, Bestückung optional — über QMK
  schaltbar, dimmbar und mit „Breathing“; Anzeige für Caps Lock und Num Lock
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
- [ ] Einfarbige Hintergrundbeleuchtung: LED-Footprints und MOSFET auf der
  Platine, Bestückung optional
- [ ] Platinenumriss und Befestigungslöcher (gemeinsam mit dem Gehäuse)
- [ ] Routing, DRC, Fertigungsdaten
- [ ] Firmware (QMK)

## Lizenz

CC BY-NC-SA 4.0 — siehe [LICENSE](LICENSE). Die Schalter-Footprints in
`lib/MX_Alps_Hybrid` stammen von ai03 und stehen unter der MIT-Lizenz.
