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
  Umgesetzt als 2-mm-Schlitz x 377,6–379,6 (Edge.Cuts, Enden r = 1) mit 4 Stegen, Footprint
  `keyboard:Breakaway_Tab_MouseBite` (board_only, BRK1–BRK4): je 2 Reihen × 6 NPTH Ø 0,5 bei x ±0,75,
  lochfreier Kanal |y| < 1 mm für max. 3 Bahnen (0,2 mm) pro Lage. Stege und geplante Netze:
  BRK1 y 52,39 → COL17–COL20, CAPS_K, NUM_K · BRK2 y 76,2 → ROW1, ROW2, +5V ·
  BRK3 y 114,3 → ROW3, ROW4, BL_K · BRK4 y 142,875 → ROW5.
  Beim Routen: Bahnen über den Schlitz NUR durch diese Kanäle, sonst nirgends.
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
  BOM-Felder an LEDn: LCSC, Manufacturer, MPN, LCSC Alternatives. Geprüfte Alternativen (Standard bleibt XL):
  C401114 MEIHUA MHT151WDT (3,2 × 1,3, JLC-Loch Ø 1,05, Vf 3,65 → ~1,35 mA),
  C2827252 TUOZHAN P2-1206WYCS2-0.9T-F (3,2 × 1,6, Anschlüsse 0,9–1,6 wie XL; Polarität im Datenblatt prüfen).
  Nicht passend: runde Kuppel-Typen (Ø 2,0–2,3-Loch), Aussparung quer nur 1,9 mm (breiter kollidiert bei
  LED70/LED76 mit ANSI-Stabi-Löchern).  Mit 1k ≈ 1,6 mA je LED, 107 LEDs ≈ 170 mA – mehr Strom sprengt das USB-Budget (Polyfuse 500 mA).
- Footprint `keyboard:LED_1206_ReverseMount_XL-3216` auf B.Cu bei Schaltermitte (0, +5,08), Orientierung 0.
  Nach JLC/EasyEDA-Footprint `LED-SMD_L3.2-W1.6-RD-EH` (Pads 1,0 × 1,524 bei ±1,651, Aussparung 2,2 × 1,9):
  Pad-Innenkante auf 1,3 mm verschoben (0,2 mm Kupfer zur Aussparung), Aussparung als Edge.Cuts mit r = 0,5.
  Datenblatt (mm.digikey.com, XL-3216UWC-FB.pdf, S. 8): Gehäuse 3,2 × 1,6, Linse 1,85 × 1,4 × 0,8,
  Anschlüsse 0,68 breit, Pad 1 = Kathode (bestätigt), Toleranz ±0,25. Unsere Pads überdecken 0,3 mm Anschluss.
- `convertible-keyboard-pcb.kicad_dru`: Kantenabstand 0,2 mm nur für LED*-Footprints, sonst 0,5 mm
  (dafür steht der Board-Mindestwert auf 0,2 – Regeln können nicht unter den Board-Mindestwert).
- Schalter-Footprints: ai03 `MX_Only:*-NoLED` (keine LED-Löcher mehr, FLIPPED-Sonderfälle entfallen).
- **THT-Variante in der Hinterhand:** `tools/led_variant.py tht|smd` tauscht nur die LED-Footprints
  (`keyboard:MX_LED_THT`, bei LED71/76/107 `MX_LED_THT_FLIPPED`), ERC/DRC/Parität geprüft (Hin- und Rückweg getestet).
  THT-Variante zeigt nur Courtyard-Warnungen an den ISO/ANSI-Stellen.

## GPIO-Belegung RP2040 (alle 30 belegt)

GPIO0–5 → COL0–5, GPIO6 → ROW0, GPIO7–20 → COL7–20, GPIO21 → BL_PWM, GPIO22 → CAPS_LED, GPIO23 → NUM_LED,
GPIO24 → COL6, GPIO25–29 → ROW1–5. Reihenfolge fürs Fan-out gewählt (Pintausch 2026-09-15 im Schaltplan,
QMK muss diese Zuordnung übernehmen): oben COL0–11 + ROW0 (ROW0 geht über die F-Reihen-Schiene),
rechts COL12–17, unten links ROW1–5 + COL6 nach unten, unten rechts COL18–20 + LED-Steuerung nach rechts.
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

- **Vollständig geroutet** (5349 Leiterbahnen, 899 Vias, 2 GND-Zonen). DRC ohne Meldung, Parität 0,
  keine offenen Verbindungen. ROW5 hat der Nutzer am 2026-09-16 von Hand in KiCad gezogen (Commit c2931ee).
- **Nach jeder Board-Änderung Zonen neu füllen**, sonst meldet DRC Abstandsfehler gegen den alten Füllstand:
  `kicad-cli pcb drc --refill-zones --save-board --schematic-parity …`
- Dioden auf B.Cu bei Schalter +(5.08, 4.0) 90°, Vorwiderstände bei (−5.08, 4.0) 90°, LEDs bei (0, 5.08).
  Ausnahmen ISO/ANSI: D71 (+6.6, +4.0), D106 (−9.2, +3.2), D107 (+6.6, +6.7), R107 (−3.6, +7.2) jeweils 90°;
  R108 (−3.0, +9.7), D108 (+3.5, +9.7) 0°.
- Alle SMD-Bauteile auf B.Cu → einseitige Bestückung. TP1–TP4 sind reines Kupfer auf F.Cu (keine Bestückung).
- Controller-Block in der F4/F5-Lücke (Nutzerentscheidung 2026-09-15):
  - Oberkante über der Lücke: J1 USB-C (147,64/30,975), darunter U4 ESD (147,64/39,3), R201/R202 CC,
    R203/C201 Schirm, R204/R205 27 Ω, F1 + C202 rechts.
  - J2 (Pico-EZmate) und J3 (JST-SH) liegen **im J1-Footprint** (147,64/31,0 bzw. /30,6), Pads auf denselben
    Netzen – nur eine der drei Buchsen wird je bestückt. Ihre Courtyards werden auf der Platine entfernt
    (`tools/udb_courtyard.py`-Prinzip, Attribut `allow_missing_courtyard`), sonst meldet DRC Überlappung.
  - Streifen unter der F-Reihe: U1 RP2040 (148/54,5, 270°), U2 Flash (137,4/54,3), Quarz Y1 (155,8/53,75) mit
    C204 (159,6/52,0 liegend), C205, R206; Entkopplung C210–C221 in einer Reihe bei y 54,3; U3 LDO + C203;
    Treiber Q3/Q2/Q1 bei x 199/207,4/215,8 mit Gate-Widerständen in der unteren Reihe (y 55,25).
  - Links im Streifen: SW201 RESET (115,6/54,3), SW202 BOOTSEL (124,4/54,3), R207/R208, J2/J3 entfallen dort.
  - R127 (TKL-Caps-Vorwiderstand) bei (369,5/58,3) unter den Kanälen.
- Kanal-Konzept beim Routen (0,2 mm Bahnen, 0,35 mm Raster = Design-Mindestabstand 0,15):
  - F-Reihen-Schienen ROW0/BL_K/+5V bei y 44,9 / 45,65 / 46,45, in der F4/F5-Lücke **nur B.Cu**
    (F.Cu bleibt dort für USB frei).
  - Spalten-Kanäle auf B.Cu: links COL5–COL0 (47,95 aufwärts), rechts oben COL7–COL15, rechts unten
    COL16–COL20 + LED-Steuerung; jede Bahn endet mit einem Via auf der vorhandenen Spaltenleitung.
  - Ab x 222 steigen die unteren Kanäle in den mittleren Streifen (Stabi-Löcher der Rücktaste blockieren unten).
  - Steg BRK1 (y 52,3875): F.Cu COL19/COL18/COL17, B.Cu NUM_K/CAPS_K/COL20 – auf der Numpad-Seite fächern
    beide Lagen kreuzungsfrei auf (K-Leitungen nach oben, Spalten in absteigender Reihenfolge nach unten).
- GND: Flächen auf F.Cu und B.Cu über dem TKL-Teil (x 27–377,2; der Ziffernblock braucht kein GND, und über die
  Stege soll kein Kupfer laufen). Voller Pad-Anschluss statt Wärmefallen (Reflow), Inseln werden entfernt,
  dazu ~100 GND-Vias (Exposed Pad, Bauteil-Pads, Stitching-Raster).

## Bekannter DRC-Stand

- 5× `hole_to_hole`: gewollte NPTH-Überlappungen ISO/ANSI (SW70/107, SW71/107 ×2, SW75/108, SW76/108).
- Wenige Silkscreen-Warnungen an ISO/ANSI-Stellen → beim Layout aufräumen.
- 2× `silk_edge_clearance`: Silkscreen von J1 an der Oberkante (Buchse bündig) – unkritisch.

## Stand

- [x] Matrix, 17 Nicht-1u-Footprints, ANSI-Alternativen
- [x] Öffentliches GitHub-Repo mit README (EN/DE), LICENSE; Umbenennung in convertible-keyboard-pcb
- [x] Beleuchtung: Reverse-Mount-SMD-LEDs (Standard), THT-Variante per tools/led_variant.py
- [x] Lock-Anzeigen (0805): Num + Caps über dem Numpad (bestückt), Caps über BildAuf für die TKL (DNP)
- [x] MCU-Blatt: RP2040, Flash, Quarz, LDO, USB-C, ESD, Taster, SWD-Testpads
- [x] Unified-Daughterboard-Anschlüsse J2 (Pico-EZmate) + J3 (JST-SH), DNP; USB-C J1 bestückt
- [x] Vorläufige Platzierung MCU/USB/Treiber auf B.Cu (Esc/F1-Lücke, Streifen unter der F-Reihe, F4/F5-Lücke)
- [x] Platinenumriss: Tastenfeld + 1,3 mm (x 27,275–458,5, y 27,275–153,7), Ecken r = 1; 1,3 mm nötig wegen
      Stabi-Löchern Leertaste/Num 0 (bis y 153,12) und Num+ (bis x 457,92)
- [x] Sollbruchstelle: Schlitz + 4 Mouse-Bite-Stege mit Leitungskanälen (siehe Wandel-Konzept)
- [ ] Befestigungslöcher (mit Gehäuse-Designer)
- [x] Routing vollständig: Tastenfeld und Controller-Bereich (eigener Grid-Router, Kanäle konstruiert, kurze
      Stücke per Wegsuche, ROW5 vom Nutzer von Hand); DRC ohne Meldung, Parität 0, keine offenen Verbindungen
- [x] Bilder für Review ohne KiCad in `docs/images/`, eingebunden in beide READMEs:
      - vom Nutzer beigesteuert: `layout-iso.png`, `layout-ansi.png` (Tastenlayouts, Grundlage des Projekts),
        `pcb-3d-front.png`, `pcb-3d-back.png` (3D-Ansichten aus dem KiCad-Viewer)
      - aus `kicad-cli` erzeugt: `pcb-both-layers.png`, `pcb-controller.png`, `pcb-front.png`, `pcb-back.png`
        (Layout ohne Kupferflächen, sonst überdeckt GND die Bahnen), `schematic-matrix.png`,
        `schematic-backlight.png`, `schematic-mcu.png`
      - bei Layout-/Schaltplanänderungen neu erzeugen: `kicad-cli sch export svg` bzw. `pcb export svg`,
        danach mit ImageMagick auf 1600–2000 px Breite verkleinern
- [ ] Fertigungsdaten (LCSC-Nummern für alle Teile ergänzen)
- [ ] Firmware (QMK) mit Full-Size- und TKL-Layout
