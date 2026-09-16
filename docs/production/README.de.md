[English](README.md) · **Deutsch**

# Fertigungsdaten (JLCPCB)

Alles in diesem Ordner wird aus dem KiCad-Projekt im Hauptverzeichnis erzeugt.
Diese Dateien nicht von Hand bearbeiten — bei jeder Änderung an der Platine neu
erzeugen (siehe unten).

> **Noch nicht bestellt, noch nicht in Hardware geprüft.** Die Dateien bestehen
> DRC und Schaltplan-Parität, aber es wurde noch kein Prototyp daraus gebaut.
> Vor dem Geldausgeben selbst prüfen.

| Datei | Inhalt |
|---|---|
| `convertible-keyboard-pcb-gerber.zip` | Gerber X1 + Excellon-Bohrdatei, direkt hochladbar |
| `BOM.csv` | Stückliste mit den Spaltennamen von JLCPCB |
| `CPL.csv` | Bestückungsdaten (Pick and Place) |

## Platine

| | |
|---|---|
| Größe | 431,225 × 126,425 mm |
| Lagen | 2 (35 µm Kupfer) |
| Min. Leiterbahn / Abstand | 0,2 mm / 0,15 mm |
| Min. Bohrung | 0,3 mm (Vias), NPTH bis herunter zu 0,5 mm (Mouse Bites) |
| Befestigungslöcher | 14 × Ø 2,2 mm für M2, nicht durchkontaktiert |
| Umriss | enthält den Sollbruch-Schlitz und seine vier Mouse-Bite-Stege |

Die `.drl`-Datei enthält durchkontaktierte und nicht durchkontaktierte Löcher
gemeinsam — falls JLCPCB fragt: **mixed plating**. Der Bohrursprung ist absolut,
Bohrdatei und Gerber liegen also im selben Koordinatensystem.

## Bestückung

371 Bauteile in 25 Gruppen. **369 sitzen auf der Unterseite, 2 auf der
Oberseite** (`D126`, `D128`, die Num- und Caps-Lock-Anzeigen über dem
Ziffernblock). Damit ist es ein beidseitiger Bestückungsauftrag, der spürbar
mehr kostet als ein einseitiger. Wer die Lock-Anzeigen nicht braucht, lässt
diese beiden Teile weg und bestückt nur die Unterseite.

Bewusst **nicht** in BOM und CPL:

- `SW1`–`SW108` — MX-Schalter werden von Hand gelötet, nicht von JLCPCB bestückt.
- `J2`, `J3` — Anschlüsse fürs Unified Daughterboard, DNP. Einen davon
  *anstelle* von `J1` bestücken, wenn die USB-Buchse aufs Daughterboard soll.
- `D122` — Caps-Lock-Anzeige der TKL-Variante, DNP. Erst sinnvoll, wenn der
  Ziffernblock abgebrochen ist; dann von Hand nachlöten.

Die Tasten-LEDs (`LED1`–`LED108`, ohne `LED106`) sind Reverse-Mount-Typen, die
*durch* die Platine leuchten, und sitzen deshalb wie alles andere unten.

## Bestellen

1. **Platine:** `convertible-keyboard-pcb-gerber.zip` hochladen. Voreinstellungen
   passen; 2 Lagen, 1,6 mm, HASL genügt. Schlitz und Mouse Bites stecken im
   Umriss, es braucht keine Sonderhinweise.
2. **Bestückung:** einschalten, **beide Seiten** wählen, `BOM.csv` und `CPL.csv`
   hochladen. JLCPCB liest die LCSC-Nummer aus der Spalte `LCSC Part #`, die
   Teile sollten also automatisch zugeordnet werden.
3. Die Bestückungsvorschau prüfen, besonders die Drehung von `U1` (RP2040),
   `U3` (LDO), `U4` (ESD-Array) und der Dioden. Die Winkel in `CPL.csv` folgen
   der KiCad-Konvention, der JLCPCB meistens — aber nicht immer — folgt.

## Neu erzeugen

Im Hauptverzeichnis, mit installiertem KiCad 10:

```sh
kicad-cli pcb drc --refill-zones --save-board --schematic-parity \
    --format json -o /tmp/drc.json convertible-keyboard-pcb.kicad_pcb
kicad-cli pcb export gerbers --no-x2 --subtract-soldermask \
    -o /tmp/gerber convertible-keyboard-pcb.kicad_pcb
kicad-cli pcb export drill --drill-origin absolute --excellon-units mm \
    --generate-map --map-format gerberx2 -o /tmp/gerber convertible-keyboard-pcb.kicad_pcb
```

Immer zuerst die Zonen neu füllen — eine veraltete Füllung erzeugt Phantom-
Abstandsfehler und, schlimmer, Gerber, die nicht zu der Platine passen, die man
geprüft hat.

`BOM.csv` und `CPL.csv` entstehen aus `kicad-cli sch export bom` und
`kicad-cli pcb export pos`, ohne die DNP-Teile und die handgelöteten Schalter
und mit den Spaltennamen, die JLCPCB erwartet. Die Y-Koordinaten in `CPL.csv`
sind negativ und passen damit zum Koordinatensystem der Gerber — das Vorzeichen
nicht umdrehen.
