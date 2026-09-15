[English](README.md) · **Deutsch**

# tools

Skripte, mit denen die Schaltplanblätter erzeugt und die Platine für
ANSI-Alternativen, Beleuchtung und Controller aktualisiert wurden. Sie bleiben im
Repository, damit der Entwurf nachvollziehbar ist und man darauf aufbauen kann.

> **Maßgeblich sind die KiCad-Dateien.** `build.sh` beginnt wieder beim
> kbplacer-Basis-Commit und überschreibt Schaltplan und Platine – alles, was
> seitdem in KiCad von Hand geändert wurde, geht verloren. Also auf einem Branch
> verwenden, oder um den erzeugten Stand vor Beginn des Layouts nachzubauen und
> zu erweitern.
>
> Der erzeugte Stand endet mit Commit `2eb5d4f`. Spätere Änderungen – Titelblöcke
> und Blattgrößen, die reduzierten Lock-Anzeigen – wurden direkt in KiCad gemacht.

## Ablauf

| Datei | Aufgabe |
|---|---|
| `build.sh --overwrite` | Führt die drei Schritte unten aus; verweigert den Start, solange KiCad das Projekt geöffnet hat |
| `gen_sch.py <Stufe>` | Baut den Schaltplan auf dem kbplacer-Hauptblatt auf (Basis-Commit `95ce8fa`). Stufe 1: ANSI-Alternativen, 2: Beleuchtung, 3: MCU-Blatt. Schreibt auch `lib/keyboard.kicad_sym` und `sym-lib-table`. UUIDs sind deterministisch |
| `check_sch.py` | Normalisiert die Dateien (`kicad-cli sch upgrade`), führt den ERC aus, exportiert die Netzliste und prüft jede erzeugte Verbindung gegen ihr Soll-Netz |
| `sync_pcb.py` | Aktualisiert die Platine aus der Netzliste wie „PCB aus Schaltplan aktualisieren“: tauscht und ergänzt Footprints, setzt Dioden und LED-Widerstände neben ihren Schalter, verknüpft Footprints mit Symbolen, vergibt Netze, führt den DRC mit Schaltplan-Parität aus |
| `place_override.json` | Dioden-/Widerstandspositionen, die von der Standardlage neben dem Schalter abweichen (ISO/ANSI-Kollisionen) |
| `kicadlib.py` | Minimaler S-Expression-Parser/-Serializer und Hilfen für Symbolbibliotheken |
| `analysis/` | Kollisionsprüfungen zwischen ISO- und ANSI-Footprints, aus denen der gedrehte, unbeleuchtete ANSI-Backslash und die gespiegelten LED-Pads folgen |

## Verwendung

```bash
tools/build.sh --overwrite
```

Voraussetzungen: KiCad 10 mit `kicad-cli` und dem Python-Modul `pcbnew` sowie die
Git-Historie (die Basisdateien werden mit `git show` gelesen). Zwischendateien
landen in `tools/build/`.

pcbnew vergibt neu eingefügten Footprints frische UUIDs, deshalb ändert sich die
Platinendatei bei jedem Lauf, auch wenn elektrisch alles gleich bleibt; die
Schaltplandateien entstehen exakt gleich.
