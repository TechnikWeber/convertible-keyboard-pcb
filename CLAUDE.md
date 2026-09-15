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
Controller fest: RP2040 (kein RP2350).
README-Fahrplan bei jedem erledigten Schritt mitpflegen.

## Wandel-Konzept Full-Size ↔ TKL

- ALLES Aktive (MCU, USB-C, Backlight-MOSFET, Lock-LEDs) auf dem TKL-Teil. Über die Bruchkante nur
  Matrixleitungen des Ziffernblocks (COL17–COL20, ROW1–ROW5) und die Backlight-Leitungen.
- Nach dem Abbrechen: Ziffernblocktasten existieren nicht mehr, Firmware unverändert (QMK mit beiden Layouts).
  Abgebrochener Ziffernblock hat keinen eigenen Controller.
- Bruchkante: Navigationsblock-Tastenrand x = 376.2375, Ziffernblock-Tastenrand x = 381.0 (mm).
  Kupferfreie Zone ca. x 374.3 … 382.9 (Schalterbohrungen ±5,08 + Pad); Mouse Bites etwa bei x ≈ 378.6.

## Werkzeuge

- KiCad 10.0.6 (Fedora), `kicad-cli` und Python-Modul `pcbnew` sind verfügbar → Platine lässt sich per Skript prüfen/ändern.
  `pcbnew` gibt beim Laden harmlose `PROPERTY_ENUM`-Asserts aus, `2>/dev/null` verwenden.
- **SWIG-Falle:** Nach `board.Remove(fp)` liefert `pcbnew.FootprintLoad()` nur noch rohe `SwigPyObject`s.
  Deshalb erst ALLE benötigten Footprints laden (Referenzen behalten), dann ändern, `Remove` ganz am Ende.
- Prüfen: `kicad-cli pcb drc --schematic-parity --format json -o drc.json convertible-keyboard-pcb.kicad_pcb`
- Footprints: Submodul `lib/MX_Alps_Hybrid` (ai03, MIT), eingebunden über Projekt-`fp-lib-table` als `MX_Only`
  (`${KIPRJMOD}/lib/MX_Alps_Hybrid/MX_Only.pretty`).
  Ursprung aller Schalter-Footprints = Schaltermitte, auch ISO und 2U vertikal → Tausch ändert keine Position.
  LED-Varianten (ohne `-NoLED`): Pads 3 (rund) und 4 (eckig) bei (∓1.27, +5.08).
- Dioden: `Diode_SMD:D_SOD-123` (KiCad-Standardbibliothek).
- Matrix erzeugt mit kbplacer aus Layout von editor.keyboard-tools.xyz; kbplacer hat auch schon Matrix-Leiterbahnen gezogen.

**Wichtig:** Dateien nie per Skript ändern, während KiCad sie geöffnet hat (Lockdatei `~*.lck`, `pgrep kicad`) – KiCad überschreibt beim Speichern.
Footprint-Änderungen immer in Schaltplan (`Footprint`-Property der Symbolinstanz) UND PCB machen.

## Matrix

- Netze `ROW0`–`ROW5`, `COL0`–`COL20` = 27 GPIOs. Diode: Pad 1 (Kathode) an ROW, Schalter an COL → Richtung COL→ROW.
- `SWn` gehört immer zu `Dn`. Keine doppelten (ROW, COL)-Paare (geprüft).
- Raster 19,05 mm, Esc-Mitte bei (38.1, 38.1) mm. Tastenfeld 428,625 × 123,825 mm (22,5 × 6,5 u), TKL 347,66 mm breit.

Nicht-1u-Tasten (17, alle getauscht):

| Ref | Taste | Größe | ROW/COL | Footprint |
|---|---|---|---|---|
| SW30 | Backspace | 2u | 1/13 | MXOnly-2U |
| SW38 | Tab | 1.5u | 2/0 | MXOnly-1.5U |
| SW57 | Num + | 2u vertikal | 2/20 | MXOnly-2U-VerticalStabilizers |
| SW58 | Caps | 1.75u | 3/0 | MXOnly-1.75U |
| SW71 | ISO-Enter | ISO | 3/13 | MXOnly-ISO |
| SW75 | Shift links (ISO) | 1.25u | 4/0 | MXOnly-1.25U |
| SW87 | Shift rechts | 2.75u | 4/12 | MXOnly-2.75U |
| SW92 | Num Enter | 2u vertikal | 4/20 | MXOnly-2U-VerticalStabilizers |
| SW93–95 | Strg, Win, Alt | 1.25u | 5/0,1,3 | MXOnly-1.25U |
| SW96 | Leertaste | 6.25u | 5/6 | MXOnly-6.25U |
| SW97–100 | AltGr, Win, Menü, Strg | 1.25u | 5/10–13 | MXOnly-1.25U |
| SW104 | Num 0 | 2u | 5/17 | MXOnly-2U |

(Stand Commit 1b219e1: noch `-NoLED`-Varianten; mit Beleuchtung auf LED-Varianten umstellen.)

ISO-Sondertasten: SW70 `#` (3/12), SW76 `<>` (4/1).

ANSI-Alternativen (je eigener Schalter + Diode, im Schaltplan UND PCB):
- Backslash 1.5u über dem ISO-Enter → neue Position ROW2/COL13 (frei)
- Enter 2.25u → gleiche Netze wie SW71 (3/13)
- Shift links 2.25u → gleiche Netze wie SW75 (4/0)

## Beleuchtung / Pins

- Einfarbig (Farbe = bestückte LED), N-MOSFET low-side an einem PWM-GPIO, QMK `BACKLIGHT_DRIVER = pwm`
  (an/aus, Stufen, Breathing). Kein Dauer-an/Schiebeschalter (USB-Suspend).
- Vorwiderstände + MOSFET werden bestückt, nur die THT-LEDs im Schalter-Footprint sind optional.
- Pinbudget RP2040 (30 GPIO): 27 Matrix + 1 Backlight + Caps- und Num-Lock-LED = 30, Scroll-Lock-LED entfällt
  (vom Nutzer bestätigt). Keine Reserve; Debug über SWD-Testpads (eigene Pins).

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
- [x] Umbenennung in convertible-keyboard-pcb, Wandel-Konzept in README
- [ ] ANSI-Alternativen in Schaltplan + PCB
- [ ] Beleuchtung: Schalter-Symbole mit LED, Vorwiderstände, MOSFET; Footprints auf LED-Varianten
- [ ] MCU-Blatt: RP2040, QSPI-Flash, 12-MHz-Quarz, 3,3-V-LDO, USB-C (5,1k CC), ESD-Schutz, SWD-Testpads
- [ ] Sollbruchstelle (Mouse Bites) zwischen Navigationsblock und Ziffernblock
- [ ] Platinenumriss, Befestigungslöcher (mit Gehäuse-Designer abstimmen)
- [ ] Routing, DRC, Fertigungsdaten
- [ ] Firmware (QMK) mit Full-Size- und TKL-Layout
