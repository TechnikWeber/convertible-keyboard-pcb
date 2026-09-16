[English](README.md) · **Deutsch**

# Firmware (QMK)

QMK-Definition für die convertible-keyboard-pcb. Die Matrixzuordnung und die
Tastenreihenfolge aller Layout-Makros werden **aus der KiCad-Platine erzeugt**,
nicht von Hand getippt — die Firmware kann also nicht von der Platine
abdriften.

> **Kompiliert, aber noch nie auf Hardware gelaufen.** Alle vier Varianten
> bauen bis zum `.uf2` durch, `qmk lint` ist sauber. Es gibt noch keine Platine,
> auf der sie sich testen ließen.

## Layouts

| Layout-Makro | Tasten | Keymap-Ordner |
|---|---|---|
| `LAYOUT_fullsize_iso` | 105 | `keymaps/default` |
| `LAYOUT_fullsize_ansi` | 104 | `keymaps/fullsize_ansi` |
| `LAYOUT_tkl_iso` | 88 | `keymaps/tkl_iso` |
| `LAYOUT_tkl_ansi` | 87 | `keymaps/tkl_ansi` |

Die TKL-Varianten sind die, die man **nach** dem Abbrechen des Ziffernblocks
aufspielt. Alle vier sind als QMK-Community-Layouts angemeldet, fremde Keymaps
für andere `fullsize_iso`- oder `tkl_ansi`-Tastaturen laufen also unverändert.

## Bauen

Dieser Ordner ist die Quelle. Ihn in eine QMK-Arbeitskopie verlinken, statt zu
kopieren:

```sh
git clone --depth 1 --recurse-submodules https://github.com/qmk/qmk_firmware.git
mkdir -p qmk_firmware/keyboards/technikweber
ln -s "$(pwd)/technikweber/convertible" qmk_firmware/keyboards/technikweber/convertible

python3 -m venv qmkenv && ./qmkenv/bin/pip install qmk
export QMK_HOME="$(pwd)/qmk_firmware"
./qmkenv/bin/qmk compile -kb technikweber/convertible -km default
```

Statt `-km default` auch `fullsize_ansi`, `tkl_iso` oder `tkl_ansi`. Es braucht
eine `arm-none-eabi-gcc`; jede generische ARM-Toolchain genügt, es muss nicht
die aus QMKs eigenem Installationsskript sein.

## Aufspielen

Die Platine in den Bootloader bringen — Esc beim Einstecken halten, `SW201` auf
der Rückseite drücken, `SW202` (BOOTSEL) beim Einstecken halten oder `Fn` + `Esc`
— dann die `.uf2` auf das erscheinende Laufwerk `RPI-RP2` kopieren, oder statt
`qmk compile` einfach `qmk flash` benutzen.

## Fn-Ebene

`Fn` liegt auf der Menü-Taste, die unter ISO-DE praktisch ungenutzt ist. Die
Menü-Funktion selbst bleibt als `Fn` + Menü erreichbar.

| Taste | Funktion |
|---|---|
| `Fn` + `Esc` | Bootloader |
| `Fn` + `F1` | Beleuchtung an/aus |
| `Fn` + `F2` / `F3` | dunkler / heller |
| `Fn` + `F4` | Breathing an/aus |

## Zuordnung zur Hardware

21 Spalten × 6 Reihen, Dioden `COL2ROW`. Alle 30 GPIOs sind belegt: `GP0`–`GP5`
und `GP7`–`GP20` plus `GP24` für die Spalten, `GP6` und `GP25`–`GP29` für die
Reihen, `GP21` Beleuchtung, `GP22` Caps Lock, `GP23` Num Lock.

Die Beleuchtung läuft über PWM. Beim RP2040 gehört ein GPIO zum Slice
`(n / 2) % 8`, Kanal A bei geradem und B bei ungeradem Pin — `GP21` braucht
also `PWMD2` und Kanal B, genau das setzt `config.h`, während `halconf.h` und
`mcuconf.h` die Peripherie freischalten. Ohne diese drei Dateien fällt der Bau
auf eine STM32-Vorgabe (`PWMD4`) zurück und scheitert.

## USB-VID/PID

`0xFEED` / `0x0001` sind QMKs Platzhalter und kollidieren mit vielen anderen
Tastaturen. Zum Testen in Ordnung; wer das in Stückzahl baut, sollte eigene
Kennungen anmelden.
