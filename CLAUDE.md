# keyboard-fullsize

Eigene Full-Size-Tastatur (ISO-DE, 105 Tasten) als KiCad-Projekt. Kommunikation auf Deutsch.
Öffentlich auf GitHub: `TechnikWeber/keyboard-fullsize`, Lizenz CC BY-NC-SA 4.0 (ohne Military-Zusatz).
README zweisprachig: `README.md` (Englisch, Standard) + `README.de.md`, Umschalter in Zeile 1.
Ganz oben in beiden READMEs: Suche nach einem Gehäuse-Designer – beim Aktualisieren drin lassen.
Anspruch des Projekts (so auch in README): kein Einmal-DIY-Keyboard, sondern aktuell halten und stetig erweitern.
README-Fahrplan bei jedem erledigten Schritt mitpflegen.

## Werkzeuge

- KiCad 10.0.6 (Fedora), `kicad-cli` und Python-Modul `pcbnew` sind verfügbar → Platine lässt sich per Skript prüfen/ändern.
  `pcbnew` gibt beim Laden harmlose `PROPERTY_ENUM`-Asserts aus, `2>/dev/null` verwenden.
- **SWIG-Falle:** `pcbnew.FootprintLoad()` funktioniert pro Python-Prozess nur zuverlässig beim ersten Aufruf
  (danach `SwigPyObject has no attribute …`). Pro Footprint einen eigenen Prozess starten.
- Prüfen: `kicad-cli pcb drc --schematic-parity --format json -o drc.json keyboard-fullsize.kicad_pcb`
- Footprints: Submodul `lib/MX_Alps_Hybrid` (ai03, MIT), eingebunden über Projekt-`fp-lib-table` als `MX_Only`
  (`${KIPRJMOD}/lib/MX_Alps_Hybrid/MX_Only.pretty`). Varianten `…-NoLED`.
  Ursprung aller Schalter-Footprints = Schaltermitte, auch ISO und 2U vertikal → Tausch ändert keine Position.
- Dioden: `Diode_SMD:D_SOD-123` (KiCad-Standardbibliothek).
- Matrix erzeugt mit kbplacer aus Layout von editor.keyboard-tools.xyz; kbplacer hat auch schon Matrix-Leiterbahnen gezogen.

**Wichtig:** Dateien nie per Skript ändern, während KiCad sie geöffnet hat (Lockdatei `~*.lck`, `pgrep kicad`) – KiCad überschreibt beim Speichern.
Footprint-Änderungen immer in Schaltplan (`Footprint`-Property der Symbolinstanz) UND PCB machen.

## Matrix

- Netze `ROW0`–`ROW5`, `COL0`–`COL20` = 27 GPIOs. Diode: Pad 1 (Kathode) an ROW, Schalter an COL → Richtung COL→ROW.
- `SWn` gehört immer zu `Dn`. Keine doppelten (ROW, COL)-Paare (geprüft).
- Raster 19,05 mm, Esc-Mitte bei (38.1, 38.1) mm. Tastenfeld 428,625 × 123,825 mm (22,5 × 6,5 u).

Nicht-1u-Tasten (17, alle getauscht):

| Ref | Taste | Größe | ROW/COL | Footprint |
|---|---|---|---|---|
| SW30 | Backspace | 2u | 1/13 | MXOnly-2U-NoLED |
| SW38 | Tab | 1.5u | 2/0 | MXOnly-1.5U-NoLED |
| SW57 | Num + | 2u vertikal | 2/20 | MXOnly-2U-VerticalStabilizers-NoLED |
| SW58 | Caps | 1.75u | 3/0 | MXOnly-1.75U-NoLED |
| SW71 | ISO-Enter | ISO | 3/13 | MXOnly-ISO-NoLED |
| SW75 | Shift links (ISO) | 1.25u | 4/0 | MXOnly-1.25U-NoLED |
| SW87 | Shift rechts | 2.75u | 4/12 | MXOnly-2.75U-NoLED |
| SW92 | Num Enter | 2u vertikal | 4/20 | MXOnly-2U-VerticalStabilizers-NoLED |
| SW93–95 | Strg, Win, Alt | 1.25u | 5/0,1,3 | MXOnly-1.25U-NoLED |
| SW96 | Leertaste | 6.25u | 5/6 | MXOnly-6.25U-NoLED |
| SW97–100 | AltGr, Win, Menü, Strg | 1.25u | 5/10–13 | MXOnly-1.25U-NoLED |
| SW104 | Num 0 | 2u | 5/17 | MXOnly-2U-NoLED |

ISO-Sondertasten: SW70 `#` (3/12), SW76 `<>` (4/1).

Geplante ANSI-Alternativen (je eigener Schalter + Diode, im Schaltplan UND PCB):
- Backslash 1.5u über dem ISO-Enter → neue Position ROW2/COL13 (frei)
- Enter 2.25u → gleiche Netze wie SW71 (3/13)
- Shift links 2.25u → gleiche Netze wie SW75 (4/0)

## Bekannter DRC-Stand (2026-09-15)

- `invalid_outline`: Edge.Cuts fehlt noch.
- 5× `hole_clearance`: kbplacer-Leiterbahnen zu nah an NPTH (SW10/11/12, SW71-Stabi, SW87-Stabi) → beim Routen beheben.
- 5 unverbundene Stellen aus den kbplacer-Leiterbahnen.
- 105× Parität „Sim.Device fehlt“ an den Dioden – harmlos.

## Stand

- [x] Projekt angelegt, Submodul eingebunden
- [x] Matrix aus kbplacer: 105 SW + 105 D
- [x] Projekt-`fp-lib-table` für `MX_Only`
- [x] 17 Footprints getauscht (Schaltplan + PCB), Parität geprüft
- [x] Öffentliches GitHub-Repo mit README (EN/DE), LICENSE
- [ ] ANSI-Alternativen in Schaltplan + PCB
- [ ] MCU-Blatt: RP2040, QSPI-Flash, 12-MHz-Quarz, 3,3-V-LDO, USB-C (5,1k CC), ESD-Schutz; 27 Matrixnetze auf GPIOs, 2–3 Pins frei halten (Backlight-MOSFET, Debug-UART GPIO0/1)
- [ ] Beleuchtung: einfarbig (MOSFET/PWM) oder per-Key-RGB – offen. MX_Only hat LED-Varianten
      (`MXOnly-*U.kicad_mod` ohne `-NoLED`, auch Hotswap-LED); Entscheidung beeinflusst Footprints und Pinbedarf
- [ ] Platinenumriss, Befestigungslöcher (mit Gehäuse-Designer abstimmen)
- [ ] Routing, DRC, Fertigungsdaten
- [ ] Firmware (QMK)
