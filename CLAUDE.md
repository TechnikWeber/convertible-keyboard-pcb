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

- Alles Aktive (MCU, USB-C, Treiber für Beleuchtung und Lock-LEDs) auf dem TKL-Teil. Über die Bruchkante nur
  Matrixleitungen des Ziffernblocks (COL17–COL20, ROW1–ROW5) sowie +5V, BL_K und NUM_K für die Ziffernblock-LEDs.
- Nach dem Abbrechen: Ziffernblocktasten existieren nicht mehr, Firmware unverändert (QMK mit beiden Layouts).
  Abgebrochener Ziffernblock hat keinen eigenen Controller.
- Bruchkante: Navigationsblock-Tastenrand x = 376.2375, Ziffernblock-Tastenrand x = 381.0 (mm).
  Kupferfreie Zone ca. x 374.3 … 382.9 (Schalterbohrungen ±5,08 + Pad); Mouse Bites etwa bei x ≈ 378.6.

## Schaltplan (KiCad 10, drei Blätter)

- Root `convertible-keyboard-pcb.kicad_sch`: Matrix (kbplacer) + ANSI-Alternativen SW106–108/D106–108 + Blattsymbole.
- `backlight.kicad_sch`: je beleuchteter Taste Einheit B von `keyboard:SW_MX_LED` + Rn (1k, 0603, gleiche Nummer
  wie die Taste) an +5V, Kathoden an BL_K. Q1 AO3400A (Gate BL_PWM), Q2/Q3 2N7002 für CAPS_K (SW58) und
  NUM_K (SW34); Gate 100 Ω, Pulldown 100k (R121–R126).
- `mcu.kicad_sch`: U1 RP2040, U2 W25Q16JVSS, Y1 12 MHz (2× 15p, 1k an XOUT), U3 AP2112K-3.3, U4 USBLC6-2SC6,
  J1 USB-C HRO TYPE-C-31-M-12 (CC 5k1, Schirm 1M‖4n7), F1 Polyfuse 500 mA, R204/R205 27 Ω,
  SW201 RESET (RUN, 10k Pull-up), SW202 BOOTSEL (1k an QSPI_SS), TP1–TP4 SWCLK/SWDIO/RUN/GND.
- Referenzen: SW/D/R 1–108 = Tasten, R121–R126 + Q1–Q3 = Treiber, x2xx/U1–U4/J1/F1/Y1/TP = MCU-Blatt.
- Symbol `keyboard:SW_MX_LED` (lib/keyboard.kicad_sym): Einheit A = Schalter (Pins exakt wie SW_Push_45deg),
  Einheit B = LED, Pin 3 = Anode, Pin 4 = Kathode (Belegung der ai03-Footprints; KiCads SW_Push_LED ist umgekehrt!).
- SW71 (ISO-Enter) im Schaltplan um 180° gedreht → Pin 2 = COL13, Pin 1 = Diode (sonst Pad-Kollision mit SW106).
- Die Blätter werden mit `tools/` erzeugt: `tools/build.sh --overwrite` startet beim Basis-Commit 95ce8fa und
  überschreibt Schaltplan + PCB! Änderungen am generierten Teil (Symbole, Netze, Standard-Platzierung) im Generator
  machen und neu bauen, solange noch nicht von Hand gelayoutet wurde. Danach sind die KiCad-Dateien die Quelle.
- Nach jedem Neubau: Schaltplandateien müssen identisch sein (`git diff`), PCB unterscheidet sich nur in UUIDs.
- ERC: 0 Meldungen. Netzliste gegen Soll geprüft.

## GPIO-Belegung RP2040 (alle 30 belegt)

GPIO0–20 → COL0–20, GPIO21–26 → ROW0–5, GPIO27 → BL_PWM, GPIO28 → CAPS_LED, GPIO29 → NUM_LED.
Kein Scroll-Lock-Indikator (vom Nutzer bestätigt). Debug über SWD-Testpads (eigene Pins).
Beim Routen dürfen Pins getauscht werden – dann Schaltplan und spätere QMK-Konfiguration anpassen.

## Werkzeuge

- KiCad 10.0.6 (Fedora), `kicad-cli` und Python-Modul `pcbnew` sind verfügbar → Platine lässt sich per Skript prüfen/ändern.
  `pcbnew` gibt beim Laden harmlose `PROPERTY_ENUM`-Asserts aus, `2>/dev/null` verwenden.
- **SWIG-Falle:** Nach `board.Remove(...)` (Footprints UND Leiterbahnen) liefern pcbnew-Aufrufe nur noch rohe
  `SwigPyObject`s. Erst alles laden und ändern, `Remove` ganz am Ende direkt vor dem Speichern.
- Prüfen: `kicad-cli sch erc`, `kicad-cli sch export netlist`,
  `kicad-cli pcb drc --schematic-parity --format json -o drc.json convertible-keyboard-pcb.kicad_pcb`
- `kicad-cli sch upgrade --force` normalisiert Schaltplandateien ins aktuelle Format.
- Footprints: Submodul `lib/MX_Alps_Hybrid` (ai03, MIT) als `MX_Only`, eigene in `lib/keyboard.pretty` als `keyboard`.
  Ursprung aller Schalter-Footprints = Schaltermitte. LED-Varianten: Pad 3 rund (Anode), Pad 4 eckig (Kathode)
  bei (∓1.27, +5.08); `-FLIPPED` tauscht die Seiten.
- Dioden: `Diode_SMD:D_SOD-123` (KiCad-Standardbibliothek).

**Wichtig:** Dateien nie per Skript ändern, während KiCad sie geöffnet hat (Lockdatei `~*.lck`, `pgrep kicad`) – KiCad überschreibt beim Speichern.
Footprint-Änderungen immer in Schaltplan (`Footprint`-Property der Symbolinstanz) UND PCB machen.

## Matrix und Tasten-Footprints

- Netze `ROW0`–`ROW5`, `COL0`–`COL20`. Diode: Pad 1 (Kathode) an ROW, Schalter an COL → Richtung COL→ROW.
- `SWn` gehört immer zu `Dn` (und bei Beleuchtung zu `Rn`). Keine doppelten (ROW, COL)-Paare außer den
  gewollten ISO/ANSI-Paaren.
- Raster 19,05 mm, Esc-Mitte bei (38.1, 38.1) mm. Tastenfeld 428,625 × 123,825 mm (22,5 × 6,5 u), TKL 347,66 mm breit.
- Alle Tasten mit LED-Footprint (`MX_Only:MXOnly-1U` usw.) außer SW106.

| Ref | Taste | Größe | ROW/COL | Footprint |
|---|---|---|---|---|
| SW30 | Backspace | 2u | 1/13 | MXOnly-2U |
| SW38 | Tab | 1.5u | 2/0 | MXOnly-1.5U |
| SW57 | Num + | 2u vertikal | 2/20 | MXOnly-2U-VerticalStabilizers |
| SW58 | Caps (LED = Caps-Lock-Anzeige) | 1.75u | 3/0 | MXOnly-1.75U |
| SW34 | Num Lock (LED = Num-Lock-Anzeige) | 1u | 1/17 | MXOnly-1U |
| SW70 | `#` (ISO) | 1u | 3/12 | MXOnly-1U |
| SW71 | ISO-Enter | ISO | 3/13 | keyboard:MXOnly-ISO-FLIPPED |
| SW75 | Shift links (ISO) | 1.25u | 4/0 | MXOnly-1.25U |
| SW76 | `<>` (ISO) | 1u | 4/1 | MXOnly-1U-FLIPPED |
| SW87 | Shift rechts | 2.75u | 4/12 | MXOnly-2.75U |
| SW92 | Num Enter | 2u vertikal | 4/20 | MXOnly-2U-VerticalStabilizers |
| SW93–95 | Strg, Win, Alt | 1.25u | 5/0,1,3 | MXOnly-1.25U |
| SW96 | Leertaste | 6.25u | 5/6 | MXOnly-6.25U |
| SW97–100 | AltGr, Win, Menü, Strg | 1.25u | 5/10–13 | MXOnly-1.25U |
| SW104 | Num 0 | 2u | 5/17 | MXOnly-2U |
| SW106 | ANSI Backslash | 1.5u | 2/13 | MXOnly-1.5U-NoLED, auf PCB 270° gedreht |
| SW107 | ANSI Enter | 2.25u | 3/13 | MXOnly-2.25U-FLIPPED |
| SW108 | ANSI Shift links | 2.25u | 4/0 | MXOnly-2.25U |

FLIPPED bei SW71/SW76/SW107: eckiges LED-Pad sonst < 0,25 mm an einem Stabi-Loch der Alternativtaste.
SW106 ohne LED und gedreht ist die einzige kollisionsfreie Lösung gegen den ISO-Enter-Stabilisator (per Suche geprüft).

## PCB-Stand

- Keine Leiterbahnen (kbplacer-Bahnen entfernt – ROW-Bahnen liefen bei y+5,65 durch die LED-Pads).
- Footprints mit Schaltplan verknüpft (Pfade), Parität sauber.
- Dioden auf B.Cu bei Schalter +(5.08, 4.0) 90°, Vorwiderstände bei (−5.08, 4.0) 90°. Ausnahmen wegen ISO/ANSI:
  D71 (+6.6, +4.0), D106 (−9.2, +3.2), D107 (+6.6, +6.7), R107 (−3.6, +7.2) jeweils 90°; R108 (−3.0, +9.7) und
  D108 (+3.5, +9.7) 0°.
- MCU-, USB- und Treiberbauteile liegen unplatziert in einem Raster unterhalb der Tasten (y ≥ 175 mm).

## Bekannter DRC-Stand (2026-09-15)

- `invalid_outline`: Edge.Cuts fehlt noch.
- 5× `hole_to_hole`: gewollte NPTH-Überlappungen ISO/ANSI (SW70/107, SW71/107 ×2, SW75/108, SW76/108).
- 2× `silk_over_copper`: Referenztexte von R107 und D75 → beim Layout verschieben.
- ~500 unverbundene Stellen (noch kein Routing).

## Stand

- [x] Projekt angelegt, Submodul eingebunden
- [x] Matrix aus kbplacer: 105 SW + 105 D
- [x] 17 Nicht-1u-Footprints, Projekt-Bibliothekstabellen
- [x] Öffentliches GitHub-Repo mit README (EN/DE), LICENSE; Umbenennung in convertible-keyboard-pcb
- [x] ANSI-Alternativen (Schaltplan + PCB)
- [x] Einfarbige Beleuchtung: LED-Footprints, Vorwiderstände, MOSFET-Treiber, Caps-/Num-Lock-Anzeige
- [x] MCU-Blatt: RP2040, Flash, Quarz, LDO, USB-C, ESD, Taster, SWD-Testpads
- [ ] Platzierung MCU/USB/Treiber auf dem TKL-Teil (USB-C-Lage mit Gehäuse-Designer abstimmen)
- [ ] Sollbruchstelle (Mouse Bites) zwischen Navigationsblock und Ziffernblock
- [ ] Platinenumriss, Befestigungslöcher
- [ ] Routing, DRC, Fertigungsdaten (Bestückungsteilenummern ergänzen)
- [ ] Firmware (QMK) mit Full-Size- und TKL-Layout
