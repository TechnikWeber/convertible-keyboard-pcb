# convertible-keyboard-pcb

Wandelbare Tastaturplatine: Full-Size ISO-DE/ANSI (105 Tasten), Ziffernblock an Sollbruchstelle (Mouse Bites)
abbrechbar → TKL (88 Tasten). Kommunikation auf Deutsch.
Bis 2026-09-15 hieß das Projekt `keyboard-fullsize` (Ordner, Dateien, GitHub-Repo umbenannt).

Öffentlich auf GitHub: `TechnikWeber/convertible-keyboard-pcb`, Lizenz CC BY-NC-SA 4.0 (ohne Military-Zusatz).
README zweisprachig: `README.md` (Englisch, Standard) + `README.de.md`, Umschalter in Zeile 1.
Ganz oben in beiden READMEs: Suche nach einem Gehäuse-Designer – beim Aktualisieren drin lassen.
Anspruch des Projekts (so auch in README): kein Einmal-DIY-Keyboard, sondern standardisiertes Kernprojekt,
auf dem man aufbauen kann – günstig, einfach, aber sehr sauber und modern. NICHT „stetig wachsen“:
Varianten (Gehäuse, Licht, Layouts) setzen auf dem Kern auf, der Kern bleibt schlank.
Controller fest: RP2040 (kein RP2350). Bestückung: JLCPCB (LCSC-Teilenummern als Feld `LCSC`).
README-Fahrplan bei jedem erledigten Schritt mitpflegen.

## Wandel-Konzept Full-Size ↔ TKL

- Alles Aktive (MCU, USB, Treiber für Beleuchtung und Lock-LEDs) auf dem TKL-Teil. Über die Bruchkante nur
  Matrixleitungen des Ziffernblocks (COL17–COL20, ROW1–ROW5) sowie +5V, BL_K, CAPS_K und NUM_K
  (Ziffernblock-LEDs und Lock-Anzeigen über dem Numpad).
- Nach dem Abbrechen: Ziffernblocktasten existieren nicht mehr, Firmware unverändert (QMK mit beiden Layouts).
- Bruchkante: Navigationsblock-Tastenrand x = 376.2375, Ziffernblock-Tastenrand x = 381.0 (mm).
  Kupferfreie Zone ca. x 374.3 … 382.9; Mouse Bites etwa bei x ≈ 378.6.
- Lock-Anzeigen (0805, oben bestückt, Nutzerentscheidung; genaue Lage entscheidet am Ende der Gehäuse-Designer):
  - Standard über dem Numpad, rechtsbündig auf Höhe der F-Reihe (y = 38,1): D128 Num über * (x = 428,625),
    D126 Caps über - (x = 447,675), bestückt. Geht beim Abbrechen mit.
  - TKL: nur Caps Lock (Num Lock ohne Numpad sinnlos), D122 mittig über BildAuf in der Lücke
    F-Reihe/Zahlenreihe (366,7125 / 52,3875), DNP.
  - Je Anzeige eigener 1k auf B.Cu, bestückt (R127 TKL-Caps, R129 Caps, R130 Num).

## USB

- J1 USB-C HRO TYPE-C-31-M-12, standardmäßig bestückt.
- Unified Daughterboard (Nutzerwunsch, beide Footprints): J2 Molex Pico-EZmate 78171-0004 (uDB S1/C4/C5-EZM),
  J3 JST-SH SM04B-SRSS-TB (uDB C3/C5-JSH), beide DNP und parallel zu J1: Pin 1 VBUS, 2 D− (USB_CONN_DM),
  3 D+ (USB_CONN_DP), 4 + MP GND. Belegung aus den KiCad-Quellen von UDB-S und UDB-C-JSH gelesen;
  1:1-Kabel, also nie spiegeln. Für ein Daughterboard J1 weglassen und J2 oder J3 bestücken.

## Schaltplan (KiCad 10, drei Blätter)

- Root `convertible-keyboard-pcb.kicad_sch`: Matrix (kbplacer, `Switch:SW_Push_45deg`) + ANSI-Alternativen
  SW106–108/D106–108 + Blattsymbole. SW71 (ISO-Enter) um 180° gedreht → Pin 2 = COL13, Pin 1 = Diode.
- `backlight.kicad_sch`: je beleuchteter Taste `LEDn` (Device:LED_Small, gleiche Nummer wie die Taste) + `Rn` (1k)
  an +5V, Kathoden an BL_K. Q1 AO3400A (Gate BL_PWM), Q2/Q3 2N7002 für CAPS_K/NUM_K, Gate 100 Ω,
  Pulldown 100k (R121–R126). Lock-Anzeigen D122/D126/D128 mit R127/R129/R130.
- `mcu.kicad_sch`: U1 RP2040, U2 W25Q16JVSS, Y1 12 MHz (2× 15p, 1k an XOUT), U3 AP2112K-3.3, U4 USBLC6-2SC6,
  J1 USB-C (CC 5k1, Schirm 1M‖4n7), J2/J3 Daughterboard, F1 Polyfuse 500 mA, R204/R205 27 Ω,
  SW201 RESET (RUN, 10k Pull-up), SW202 BOOTSEL (1k an QSPI_SS), TP1–TP4 SWCLK/SWDIO/RUN/GND.
- Referenzen: SW/D/R/LED 1–108 = Tasten, R121–R130 + Q1–Q3 = Treiber/Anzeigen, x2xx/U/J/F/Y/TP = MCU-Blatt.
- ERC: 0 Meldungen.

## Tasten-LEDs (Standard: Reverse-Mount-SMD, Nutzerentscheidung)

- Teil: XINGLIGHT XL-3216UWC-FB, weiß, 1206 Reverse Mount, LCSC C3646935 (Extended), Vf 3,4 V.
  Mit 1k ≈ 1,6 mA je LED, 107 LEDs ≈ 170 mA – mehr Strom sprengt das USB-Budget (Polyfuse 500 mA).
- Footprint `keyboard:LED_1206_ReverseMount_XL-3216` auf B.Cu bei Schaltermitte (0, +5,08), Orientierung 0.
  Nach JLC/EasyEDA-Footprint `LED-SMD_L3.2-W1.6-RD-EH` (Pads 1,0 × 1,524 bei ±1,651, Aussparung 2,2 × 1,9):
  Pad-Innenkante auf 1,3 mm verschoben (0,2 mm Kupfer zur Aussparung), Aussparung als Edge.Cuts mit r = 0,5.
  Datenblatt des XL-3216UWC-FB selbst nicht abrufbar (JLC-Link gesperrt); Maße aus Schwester-LED XL-3216UYC-FB
  (Gehäuse 3,2 × 1,6, Linse ca. 1,8 × 1,3) und den EasyEDA-Rohdaten. Vor der ersten Bestellung Pad 1 = Kathode
  am echten Teil prüfen.
- `convertible-keyboard-pcb.kicad_dru`: Kantenabstand 0,2 mm nur für LED*-Footprints, sonst 0,5 mm
  (dafür steht der Board-Mindestwert auf 0,2 – Regeln können nicht unter den Board-Mindestwert).
- Schalter-Footprints: ai03 `MX_Only:*-NoLED` (keine LED-Löcher mehr, FLIPPED-Sonderfälle entfallen).
- **THT-Variante in der Hinterhand:** `tools/led_variant.py tht|smd` tauscht nur die LED-Footprints
  (`keyboard:MX_LED_THT`, bei LED71/76/107 `MX_LED_THT_FLIPPED`), ERC/DRC/Parität geprüft (Hin- und Rückweg getestet).
  THT-Variante zeigt nur Courtyard-Warnungen an den ISO/ANSI-Stellen.

## GPIO-Belegung RP2040 (alle 30 belegt)

GPIO0–20 → COL0–20, GPIO21–26 → ROW0–5, GPIO27 → BL_PWM, GPIO28 → CAPS_LED, GPIO29 → NUM_LED.
Kein Scroll-Lock-Indikator. Debug über SWD-Testpads. Beim Routen dürfen Pins getauscht werden (Schaltplan + QMK).

## Werkzeuge

- KiCad 10.0.6 (Fedora), `kicad-cli` und Python-Modul `pcbnew`. `pcbnew` gibt harmlose `PROPERTY_ENUM`-Asserts aus.
- **SWIG-Falle:** Nach `board.Remove(...)` liefern pcbnew-Aufrufe nur noch rohe `SwigPyObject`s → erst alles laden und
  ändern, `Remove` direkt vor dem Speichern. Beim Beenden kann pcbnew segfaulten → am Ende `os._exit(0)`.
- **KiCad-Speichern** ergänzt in Symbolinstanzen die Pins aller Einheiten – Skripte müssen damit rechnen.
- Prüfen: `kicad-cli sch erc`, `kicad-cli sch export netlist`,
  `kicad-cli pcb drc --schematic-parity --format json -o drc.json convertible-keyboard-pcb.kicad_pcb`.
  `kicad-cli sch upgrade --force` normalisiert die Schaltplandateien.
- `tools/` = Generator (Stand Commit 2eb5d4f, NICHT mehr ausführen – überschreibt spätere Änderungen) und
  `led_variant.py` (arbeitet auf den aktuellen Dateien).
- Footprints: Submodul `lib/MX_Alps_Hybrid` (ai03, MIT) als `MX_Only`, eigene in `lib/keyboard.pretty` als `keyboard`.
  Ursprung aller Schalter-Footprints = Schaltermitte.
- Datenblätter von JLC (aliyuncs) sind per curl gesperrt; EasyEDA-API geht über WebFetch
  (`https://easyeda.com/api/products/<LCSC>/components?version=6.4.19.5`, 1 Einheit = 0,254 mm).

**Wichtig:** Nie Dateien ändern, während KiCad sie geöffnet hat (`pgrep kicad`, Lockdatei `~*.lck`).
Ungesicherte Nutzeränderungen aus KiCad getrennt committen (ohne Co-Author).

## Matrix und Tasten-Footprints

- Netze `ROW0`–`ROW5`, `COL0`–`COL20`. Diode: Pad 1 (Kathode) an ROW, Schalter an COL → Richtung COL→ROW.
- Raster 19,05 mm, Esc-Mitte bei (38.1, 38.1) mm. Tastenfeld 428,625 × 123,825 mm, TKL 347,66 mm breit.

| Ref | Taste | Größe | ROW/COL | Footprint (MX_Only) |
|---|---|---|---|---|
| SW30 | Backspace | 2u | 1/13 | MXOnly-2U-NoLED |
| SW38 | Tab | 1.5u | 2/0 | MXOnly-1.5U-NoLED |
| SW57 | Num + | 2u vertikal | 2/20 | MXOnly-2U-VerticalStabilizers-NoLED |
| SW58 | Caps | 1.75u | 3/0 | MXOnly-1.75U-NoLED |
| SW70 | `#` (ISO) | 1u | 3/12 | MXOnly-1U-NoLED |
| SW71 | ISO-Enter | ISO | 3/13 | MXOnly-ISO-NoLED |
| SW75 | Shift links (ISO) | 1.25u | 4/0 | MXOnly-1.25U-NoLED |
| SW76 | `<>` (ISO) | 1u | 4/1 | MXOnly-1U-NoLED |
| SW87 | Shift rechts | 2.75u | 4/12 | MXOnly-2.75U-NoLED |
| SW92 | Num Enter | 2u vertikal | 4/20 | MXOnly-2U-VerticalStabilizers-NoLED |
| SW93–95, SW97–100 | Strg, Win, Alt, AltGr, Win, Menü, Strg | 1.25u | 5/… | MXOnly-1.25U-NoLED |
| SW96 | Leertaste | 6.25u | 5/6 | MXOnly-6.25U-NoLED |
| SW104 | Num 0 | 2u | 5/17 | MXOnly-2U-NoLED |
| SW106 | ANSI Backslash | 1.5u | 2/13 | MXOnly-1.5U-NoLED, auf PCB 270° gedreht, ohne LED |
| SW107 | ANSI Enter | 2.25u | 3/13 | MXOnly-2.25U-NoLED |
| SW108 | ANSI Shift links | 2.25u | 4/0 | MXOnly-2.25U-NoLED |

SW106 ohne LED und gedreht ist die einzige kollisionsfreie Lösung gegen den ISO-Enter-Stabilisator.

## PCB-Stand

- Keine Leiterbahnen. Footprints mit Schaltplan verknüpft, Parität sauber.
- Dioden auf B.Cu bei Schalter +(5.08, 4.0) 90°, Vorwiderstände bei (−5.08, 4.0) 90°, LEDs bei (0, 5.08).
  Ausnahmen ISO/ANSI: D71 (+6.6, +4.0), D106 (−9.2, +3.2), D107 (+6.6, +6.7), R107 (−3.6, +7.2) jeweils 90°;
  R108 (−3.0, +9.7), D108 (+3.5, +9.7) 0°.
- Lock-Anzeigen stehen an ihren Positionen.
- Vorläufige Platzierung (alles B.Cu, Feinschliff beim Routing):
  - Esc/F1-Lücke (x 45–70): J1 USB-C (57,15 / 32,9, Öffnung zur Oberkante – Board-Oberkante muss dort an der
    Buchse liegen), U4 ESD, R201/R202 CC, R203/C201 Schirm, R204/R205 27 Ω, F1 + C202, U3 LDO + C203,
    J2 Pico-EZmate (51,5 / 56,5), J3 JST-SH (63,5 / 56,5).
  - Streifen unter der F-Reihe (frei y 44,5–60,5): U2 Flash (79 / 52,5), U1 RP2040 (90 / 52,5, 270°: USB/QSPI
    links, XIN rechts), Entkopplung C210–C221 in Reihen bei y 46,3 und 58,6 (Referenzen ausgeblendet),
    Y1 + C204/C205 + R206 rechts davon, SW202 BOOTSEL (110), SW201 RESET (120,5), TP1–TP4 (127,5–135).
  - F4/F5-Lücke: Q1/Q2/Q3 bei x 144 / 150,5 / 157,5 (y 48) mit Gate- und Pulldown-Widerständen darunter.

## Bekannter DRC-Stand

- 5× `hole_to_hole`: gewollte NPTH-Überlappungen ISO/ANSI (SW70/107, SW71/107 ×2, SW75/108, SW76/108).
- Wenige Silkscreen-Warnungen an ISO/ANSI-Stellen → beim Layout aufräumen.
- Platinenumriss fehlt noch (die LED-Aussparungen sind Edge.Cuts, daher meldet KiCad kein `invalid_outline` mehr).

## Stand

- [x] Matrix, 17 Nicht-1u-Footprints, ANSI-Alternativen
- [x] Öffentliches GitHub-Repo mit README (EN/DE), LICENSE; Umbenennung in convertible-keyboard-pcb
- [x] Beleuchtung: Reverse-Mount-SMD-LEDs (Standard), THT-Variante per tools/led_variant.py
- [x] Lock-Anzeigen (0805): Num + Caps über dem Numpad (bestückt), Caps über BildAuf für die TKL (DNP)
- [x] MCU-Blatt: RP2040, Flash, Quarz, LDO, USB-C, ESD, Taster, SWD-Testpads
- [x] Unified-Daughterboard-Anschlüsse J2 (Pico-EZmate) + J3 (JST-SH), DNP; USB-C J1 bestückt
- [x] Vorläufige Platzierung MCU/USB/Treiber auf B.Cu (Esc/F1-Lücke, Streifen unter der F-Reihe, F4/F5-Lücke)
- [ ] Sollbruchstelle (Mouse Bites) zwischen Navigationsblock und Ziffernblock
- [ ] Platinenumriss, Befestigungslöcher
- [ ] Routing, DRC, Fertigungsdaten (LCSC-Nummern für alle Teile ergänzen)
- [ ] Firmware (QMK) mit Full-Size- und TKL-Layout
