#!/usr/bin/env bash
# Regenerates the schematic sheets and updates the PCB, starting from the kbplacer base commit.
# Overwrites convertible-keyboard-pcb.kicad_sch/.kicad_pcb, backlight.kicad_sch, mcu.kicad_sch and lib/keyboard.kicad_sym.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ "${1:-}" != "--overwrite" ]]; then
    echo "usage: tools/build.sh --overwrite   (replaces schematic and PCB with the generated state)" >&2
    exit 2
fi
if pgrep -x kicad >/dev/null || compgen -G "./~*.lck" >/dev/null; then
    echo "KiCad is running or the project is locked - close KiCad first." >&2
    exit 1
fi
python3 tools/gen_sch.py 3
python3 tools/check_sch.py
python3 tools/sync_pcb.py 2>&1 | { grep -v -e PROPERTY_ENUM -e 'memory leak' || true; }
