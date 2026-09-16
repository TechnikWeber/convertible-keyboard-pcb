[English](README.md) · **Deutsch**

# convertible-keyboard-pcb

> ### 🔎 Gehäuse-Designer gesucht
> Die Platine dieser Tastatur entsteht gerade, ein Gehäuse gibt es noch nicht.
> Wenn du Tastaturgehäuse entwirfst — 3D-gedruckt, CNC-gefräst oder
> lasergeschnitten — und Lust auf dieses Projekt hast, eröffne gern ein
> [Issue](https://github.com/TechnikWeber/convertible-keyboard-pcb/issues).
> Ein erster Platinenumriss steht (Tastenfeld + 1,3 mm), aber Umriss,
> Befestigungslöcher und die Lage der USB-C-Buchse können sich noch nach deinem
> Gehäuse richten — für die
> Full-Size-Variante, die TKL oder beide. Dasselbe gilt für die genaue Position
> der Lock-Anzeigen. Die USB-Buchse kann auf der Platine sitzen oder auf einem
> Unified Daughterboard (Pico-EZmate oder JST-SH).

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
> Footprint auf der Platine; Controller, USB und Treiber sind auf der Rückseite
> platziert, Platinenumriss und Sollbruchstelle sind gezeichnet.
> Befestigungslöcher und Routing fehlen noch. Gefertigt wurde bisher nichts.

## Full-Size oder TKL

- Der Ziffernblock sitzt rechts hinter einem 2 mm breiten Schlitz und hängt an
  vier Mouse-Bite-Stegen (perforierte Bruchstege). Jeder Steg hat in der Mitte
  einen lochfreien Kanal für die Leitungen, die hinüberlaufen.
- Controller, USB-C sowie die Treiber für Beleuchtung und Lock-Anzeigen liegen
  alle auf dem TKL-Teil. Nur die Matrix-, Beleuchtungs- und
  Anzeigeleitungen des Ziffernblocks laufen über die Bruchkante.
- Ziffernblock abbrechen, und die TKL funktioniert unverändert weiter — die
  Ziffernblocktasten gibt es dann einfach nicht mehr. Die Firmware beschreibt
  beide Layouts.
- Die Lock-Anzeigen über dem Ziffernblock gehen mit – ohne Ziffernblock ist
  Num Lock ohnehin sinnlos; für die TKL bestückt man die Caps-Lock-Anzeige über
  Bild auf.
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
- USB-C (USB 2.0) auf der Platine mit ESD-Schutz, 500-mA-Polyfuse und 3,3-V-LDO –
  oder stattdessen ein Unified Daughterboard: Anschlüsse für Molex Pico-EZmate
  (uDB S1, C4, C5-EZM) und JST-SH (uDB C3, C5-JSH) sind vorgesehen, nicht bestückt
- Einfarbige Hintergrundbeleuchtung mit Reverse-Mount-1206-LEDs auf der Rückseite
  (weiß, XINGLIGHT XL-3216UWC-FB), maschinell bestückt; über QMK schaltbar,
  dimmbar und mit „Breathing“. Eine THT-LED-Variante nutzt denselben Entwurf mit
  anderen LED-Footprints
- Geprüfte Alternativ-LEDs für denselben Footprint: MEIHUA MHT151WDT
  (LCSC C401114) und TUOZHAN P2-1206WYCS2-0.9T-F (LCSC C2827252)
- Anzeige für Caps Lock und Num Lock (0805) über dem Ziffernblock; für die TKL ist
  eine Caps-Lock-Anzeige über Bild auf vorgesehen, aber nicht bestückt
- Alle 30 GPIOs des RP2040 belegt: 27 Matrixleitungen, Beleuchtungs-PWM,
  Caps Lock und Num Lock

## Repository

| Pfad | Inhalt |
|---|---|
| `convertible-keyboard-pcb.kicad_pro` / `.kicad_pcb` | KiCad-10-Projekt und Platine |
| `convertible-keyboard-pcb.kicad_sch` | Hauptblatt: Tastenmatrix und ANSI-Alternativen |
| `backlight.kicad_sch` | Tasten-LEDs, Vorwiderstände und MOSFET-Treiber |
| `mcu.kicad_sch` | RP2040, Flash, Quarz, USB-C und Stromversorgung |
| `lib/keyboard.pretty` | Projekt-Footprints: Reverse-Mount-LED, THT-LED für die Variante |
| `fp-lib-table`, `convertible-keyboard-pcb.kicad_dru` | Footprint-Bibliothekstabelle, Designregel für die LED-Aussparungen |
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
- [x] Sollbruchstelle für den Ziffernblock
- [x] Platinenumriss (erster Entwurf)
- [ ] Befestigungslöcher (gemeinsam mit dem Gehäuse)
- [x] Platzierung von Controller, USB und Treibern (vorläufig)
- [x] Routing von Tastenfeld und Controller-Bereich (DRC ohne Meldung, Parität sauber)
- [ ] Letzte Verbindung (ROW5) und Fertigungsdaten
- [ ] Firmware (QMK) mit Full-Size- und TKL-Layout

## Lizenz

CC BY-NC-SA 4.0 — siehe [LICENSE](LICENSE). Die Schalter-Footprints in
`lib/MX_Alps_Hybrid` stammen von ai03 und stehen unter der MIT-Lizenz;
die THT-LED-Footprints in `lib/keyboard.pretty` übernehmen deren Pad-Geometrie.
