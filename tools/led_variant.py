#!/usr/bin/env python3
"""Switch the key LEDs between the standard reverse-mount SMD variant and the THT variant.

    tools/led_variant.py smd    LEDn = reverse-mount 1206 on the back of the PCB (standard)
    tools/led_variant.py tht    LEDn = THT LED through the switch LED slot

Only the LED footprints and their Value/LCSC fields change - schematic, nets and positions stay the same.
Edits the KiCad files in place, so close KiCad first. Runs ERC and DRC with schematic parity afterwards.
"""
import sys, os, json, subprocess, collections

HERE = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kicadlib import parse, dumps, find, findall

NAME = "convertible-keyboard-pcb"
BUILD = os.path.join(HERE, "build")
VARIANTS = {
    "smd": dict(fp="keyboard:LED_1206_ReverseMount_XL-3216", value="XL-3216UWC-FB", side="B",
                fields={"LCSC": "C3646935", "Manufacturer": "XINGLIGHT", "MPN": "XL-3216UWC-FB",
                        # checked against the footprint: body, lens and terminals fit
                        "LCSC Alternatives": "C401114 MEIHUA MHT151WDT; C2827252 TUOZHAN P2-1206WYCS2-0.9T-F"}),
    "tht": dict(fp="keyboard:MX_LED_THT", value="LED THT", side="F",
                fields={"LCSC": "", "Manufacturer": "", "MPN": "", "LCSC Alternatives": ""}),
}
# THT only: the square cathode pad would come too close to a stabilizer hole of an ISO/ANSI alternative key
THT_FLIPPED = {"LED71", "LED76", "LED107"}
KNOWN_DRC = {("error", "invalid_outline"), ("warning", "hole_to_hole"), ("warning", "silk_over_copper"),
             ("warning", "silk_overlap")}


def is_key_led(ref):
    return ref.startswith("LED") and ref[3:].isdigit()


def footprint_for(variant, ref):
    if variant == "tht" and ref in THT_FLIPPED:
        return "keyboard:MX_LED_THT_FLIPPED"
    return VARIANTS[variant]["fp"]


def schematic(variant):
    v = VARIANTS[variant]
    locked = any(f.startswith("~") and f.endswith(".lck") for f in os.listdir(PRJ))
    if subprocess.run(["pgrep", "-x", "kicad"], capture_output=True).returncode == 0 or locked:
        sys.exit("KiCad is running or the project is locked - close KiCad first.")
    os.makedirs(BUILD, exist_ok=True)
    path = os.path.join(PRJ, "backlight.kicad_sch")
    t = parse(open(path).read())
    changed = 0
    for s in findall(t, "symbol"):
        props = {p[1]: p for p in findall(s, "property")}
        ref = props["Reference"][2]
        if not is_key_led(ref):
            continue
        props["Footprint"][2] = footprint_for(variant, ref)
        props["Value"][2] = v["value"]
        for key, val in v["fields"].items():
            if key in props:
                props[key][2] = val
        changed += 1
    open(path, "w").write(dumps(t) + "\n")
    root = os.path.join(PRJ, f"{NAME}.kicad_sch")
    net = os.path.join(BUILD, "variant.net")
    subprocess.run(["kicad-cli", "sch", "upgrade", "--force", root], capture_output=True, check=True)
    subprocess.run(["kicad-cli", "sch", "erc", "--format", "json", "--severity-all",
                    "-o", os.path.join(BUILD, "erc_variant.json"), root], capture_output=True)
    subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", net, root],
                   capture_output=True, check=True)
    erc = sum(len(sh["violations"]) for sh in json.load(open(os.path.join(BUILD, "erc_variant.json")))["sheets"])
    print(f"schematic: {changed} key LEDs -> {variant}, ERC violations: {erc}")
    if erc:
        sys.exit(1)
    # the PCB runs in its own process: pcbnew likes to segfault while Python tears down
    sys.exit(subprocess.run([sys.executable, os.path.abspath(__file__), "--pcb", variant, net]).returncode)


def pcb(variant, net):
    import pcbnew
    v = VARIANTS[variant]
    nl = parse(open(net).read())
    comps = {}
    for c in findall(find(nl, "components"), "comp"):
        ref = find(c, "ref")[1]
        if not is_key_led(ref):
            continue
        fields = {find(f, "name")[1]: (f[2] if len(f) > 2 and isinstance(f[2], str) else "")
                  for f in findall(find(c, "fields"), "field")} if find(c, "fields") else {}
        comps[ref] = dict(fp=find(c, "footprint")[1], value=find(c, "value")[1], fields=fields)
    pinnet = {}
    for n in findall(find(nl, "nets"), "net"):
        for nd in findall(n, "node"):
            pinnet[(find(nd, "ref")[1], find(nd, "pin")[1])] = find(n, "name")[1]

    path = os.path.join(PRJ, f"{NAME}.kicad_pcb")
    b = pcbnew.LoadBoard(path)
    old = {f.GetReference(): f for f in b.GetFootprints() if f.GetReference() in comps}
    missing = sorted(set(comps) - set(old))
    assert not missing, f"LED footprints missing on the PCB: {missing}"
    todo = []                                  # load everything before touching the board
    for ref, c in sorted(comps.items()):
        if old[ref].GetFPIDAsString() == c["fp"]:
            continue
        lib, name = c["fp"].split(":", 1)
        libdir = os.path.join(PRJ, "lib", "keyboard.pretty") if lib == "keyboard" \
            else f"/usr/share/kicad/footprints/{lib}.pretty"
        f = pcbnew.FootprintLoad(libdir, name)
        assert type(f).__name__ == "FOOTPRINT", (ref, c["fp"])
        f.SetFPID(pcbnew.LIB_ID(lib, name))
        todo.append((ref, old[ref], f))
    for ref, o, f in todo:
        b.Add(f)
        f.SetPosition(o.GetPosition())
        if v["side"] == "B":
            f.SetLayerAndFlip(pcbnew.B_Cu)
        f.SetOrientationDegrees(0)
        f.SetReference(ref)
        f.SetValue(comps[ref]["value"])
        f.SetPath(o.GetPath())
        f.SetSheetname(o.GetSheetname())
        f.SetSheetfile(o.GetSheetfile())
        f.SetDNP(o.IsDNP())
        for k, val in comps[ref]["fields"].items():
            if k not in ("Reference", "Value", "Footprint"):
                f.SetField(k, val)
                if k not in ("Datasheet", "Description") and f.GetField(k) is not None:
                    f.GetField(k).SetVisible(False)
        for pad in f.Pads():
            key = (ref, pad.GetNumber())
            if pad.GetNumber() and key in pinnet:
                ni = b.FindNet(pinnet[key])
                assert ni is not None, pinnet[key]
                pad.SetNet(ni)
    for ref, o, f in todo:                     # removals last
        b.Remove(o)
    b.Save(path)
    print(f"PCB: {len(todo)} LED footprints swapped")
    sys.stdout.flush()

    out = os.path.join(BUILD, "drc_variant.json")
    subprocess.run(["kicad-cli", "pcb", "drc", "--schematic-parity", "--severity-all", "--format", "json",
                    "-o", out, path], capture_output=True)
    d = json.load(open(out))
    cnt = collections.Counter((x["severity"], x["type"]) for x in d["violations"])
    parity = d.get("schematic_parity", [])
    print("DRC:", dict(cnt), "| parity:", len(parity))
    shown = collections.Counter()
    for x in d["violations"]:
        key = (x["severity"], x["type"])
        if key in KNOWN_DRC or shown[key] >= 8:
            continue
        shown[key] += 1
        print(f"  [{x['type']}] {x['description'][:70]} | " +
              " ; ".join(f"{i['description'][:50]} @({i['pos']['x']:.2f},{i['pos']['y']:.2f})" for i in x["items"]))
    sys.stdout.flush()
    os._exit(1 if parity or set(cnt) - KNOWN_DRC else 0)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--pcb":
        pcb(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 2 and sys.argv[1] in VARIANTS:
        schematic(sys.argv[1])
    else:
        print(__doc__)
        sys.exit(2)
