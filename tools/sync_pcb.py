#!/usr/bin/env python3
"""Update the PCB from the exported netlist (like 'Update PCB from Schematic'), starting from base/.

- swaps footprints whose library id changed (position/orientation/side kept)
- adds new footprints: ANSI switches at their key positions, diodes/LED resistors next to their switch
  on B.Cu, everything else in a staging grid below the board
- links footprints to symbols (path, sheet), copies fields, assigns every pad net
- removes the kbplacer tracks (they run through the new LED pads; routing is redone later)
"""
import sys, os, re, json, subprocess, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kicadlib import parse, find, findall, git_base
import pcbnew

PRJ = os.path.dirname(HERE)
NAME = "convertible-keyboard-pcb"
PCB = f"{PRJ}/{NAME}.kicad_pcb"
OUT = f"{HERE}/build"
U = 19.05

KEYPOS = {"SW106": (314.325 - 1.5 * U / 2, 85.725, 270),
          "SW107": (314.325 - 2.25 * U / 2, 104.775, 0),
          "SW108": (28.575 + 2.25 * U / 2, 123.825, 0)}
REL = {"D": (5.08, 4.0), "R": (-5.08, 4.0)}          # relative to the switch, B.Cu, 90°
_place = json.load(open(f"{HERE}/place_override.json"))
OVERRIDE = _place["relative"]   # ref: (dx, dy, rot) from its switch, B.Cu
ABSOLUTE = _place["absolute"]   # ref: (x, y, rot, side)


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


# ---------------------------------------------------------------- netlist
nl = parse(open(f"{OUT}/{NAME}.net").read())
comps = {}
for c in findall(find(nl, "components"), "comp"):
    ref = find(c, "ref")[1]
    fp = find(c, "footprint")
    props = {find(p, "name")[1]: (find(p, "value") or [None, ""])[1] for p in findall(c, "property")}
    sp = find(c, "sheetpath")
    fields = {}
    if find(c, "fields"):
        for f in findall(find(c, "fields"), "field"):
            fields[find(f, "name")[1]] = f[2] if len(f) > 2 and isinstance(f[2], str) else ""
    comps[ref] = dict(fp=fp[1] if fp else "", value=find(c, "value")[1],
                      path=find(sp, "tstamps")[1] + find(c, "tstamps")[1],
                      sheetname=find(sp, "names")[1], sheetfile=props.get("Sheetfile", ""), fields=fields,
                      dnp="dnp" in props)
pinnet = {}
for n in findall(find(nl, "nets"), "net"):
    for nd in findall(n, "node"):
        pinnet[(find(nd, "ref")[1], find(nd, "pin")[1])] = find(n, "name")[1]

# ---------------------------------------------------------------- board
for ext in ("kicad_pcb", "kicad_pro"):   # project file carries the design rules
    open(f"{OUT}/base.{ext}", "w").write(git_base(PRJ, f"{NAME}.{ext}"))
b = pcbnew.LoadBoard(f"{OUT}/base.kicad_pcb")
old = {f.GetReference(): f for f in b.GetFootprints()}
missing_fp = [r for r, c in comps.items() if not c["fp"]]
assert not missing_fp, f"symbols without footprint: {missing_fp}"


def libpath(lib):
    return {"MX_Only": f"{PRJ}/lib/MX_Alps_Hybrid/MX_Only.pretty",
            "keyboard": f"{PRJ}/lib/keyboard.pretty"}.get(lib, f"/usr/share/kicad/footprints/{lib}.pretty")


# load everything first - pcbnew's SWIG wrappers break once footprints get removed
todo = []
for ref, c in sorted(comps.items()):
    o = old.get(ref)
    if o is None or o.GetFPIDAsString() != c["fp"]:
        lib, name = c["fp"].split(":", 1)
        new = pcbnew.FootprintLoad(libpath(lib), name)
        assert type(new).__name__ == "FOOTPRINT", (ref, c["fp"], type(new))
        new.SetFPID(pcbnew.LIB_ID(lib, name))
        todo.append((ref, o, new))

swpos = {r: (pcbnew.ToMM(f.GetPosition().x), pcbnew.ToMM(f.GetPosition().y)) for r, f in old.items() if r.startswith("SW")}
swpos.update({r: (x, y) for r, (x, y, _) in KEYPOS.items()})
stage_i = 0
for ref, o, new in todo:
    b.Add(new)
    m = re.match(r"(SW|D|R)(\d+)$", ref)
    if o is not None:
        new.SetPosition(o.GetPosition())
        if o.IsFlipped():
            new.SetLayerAndFlip(pcbnew.B_Cu)
        new.SetOrientation(o.GetOrientation())
    elif ref in ABSOLUTE:
        x, y, rot, side = ABSOLUTE[ref]
        new.SetPosition(mm(x, y))
        if side == "B":
            new.SetLayerAndFlip(pcbnew.B_Cu)
        new.SetOrientationDegrees(rot)
    elif ref in KEYPOS:
        x, y, rot = KEYPOS[ref]
        new.SetPosition(mm(x, y))
        new.SetOrientationDegrees(rot)
    elif m and m.group(1) in REL and int(m.group(2)) <= 108 and f"SW{m.group(2)}" in swpos:
        sx, sy = swpos[f"SW{m.group(2)}"]
        dx, dy, rot = OVERRIDE.get(ref, (*REL[m.group(1)], 90))
        new.SetPosition(mm(sx + dx, sy + dy))
        new.SetLayerAndFlip(pcbnew.B_Cu)
        new.SetOrientationDegrees(rot)
    else:
        new.SetPosition(mm(30 + (stage_i % 20) * 10, 175 + (stage_i // 20) * 10))
        stage_i += 1
fps = dict(old)
fps.update({ref: new for ref, o, new in todo})
for ref, (dx, dy, rot) in OVERRIDE.items():
    if ref in fps:
        sx, sy = swpos[f"SW{re.match(r'[A-Z]+(\d+)$', ref).group(1)}"]
        f = fps[ref]
        f.SetPosition(mm(sx + dx, sy + dy))
        if not f.IsFlipped():
            f.SetLayerAndFlip(pcbnew.B_Cu)
        f.SetOrientationDegrees(rot)
nets = {}


def getnet(name):
    if name not in nets:
        ni = b.FindNet(name)
        if ni is None:
            ni = pcbnew.NETINFO_ITEM(b, name)
            b.Add(ni)
        nets[name] = ni
    return nets[name]


for ref, c in comps.items():
    f = fps[ref]
    f.SetReference(ref)
    f.SetValue(c["value"])
    f.SetPath(pcbnew.KIID_PATH(c["path"]))
    f.SetSheetname(c["sheetname"])
    f.SetSheetfile(c["sheetfile"])
    f.SetDNP(c["dnp"])
    for k, v in c["fields"].items():
        if k in ("Reference", "Value", "Footprint"):
            continue
        f.SetField(k, v)
        fld = f.GetField(k)
        if fld is not None and k not in ("Datasheet", "Description"):
            fld.SetVisible(False)
    for p in f.Pads():
        n = p.GetNumber()
        if n and (ref, n) in pinnet:
            p.SetNet(getnet(pinnet[(ref, n)]))
        else:
            p.SetNetCode(0)
extra = sorted(set(fps) - set(comps))
# removals last: afterwards the SWIG wrappers of remaining items are unreliable
for ref, o, new in todo:
    if o is not None:
        b.Remove(o)
for t in list(b.GetTracks()):
    b.Remove(t)
try:
    b.RemoveUnusedNets(None)
except TypeError:
    b.RemoveUnusedNets()
b.Save(PCB)
print(f"PCB: {len(todo)} footprints added/swapped, {len(fps)} total, without symbol: {extra}")

# ---------------------------------------------------------------- DRC
subprocess.run(["kicad-cli", "pcb", "drc", "--schematic-parity", "--severity-all", "--format", "json",
                "-o", f"{OUT}/drc.json", PCB], capture_output=True)
d = json.load(open(f"{OUT}/drc.json"))
cnt = collections.Counter((v["severity"], v["type"]) for v in d["violations"])
print("DRC:", dict(cnt))
print("unconnected:", len(d.get("unconnected_items", [])))
par = collections.Counter(v["type"] for v in d.get("schematic_parity", []))
print("parity:", dict(par))
IGN = {"invalid_outline", "unconnected_items"}
shown = collections.Counter()
for v in d["violations"] + d.get("schematic_parity", []):
    if v["type"] in IGN or shown[v["type"]] >= int(os.environ.get("SHOW", "12")):
        continue
    shown[v["type"]] += 1
    print(f"  [{v['type']}] {v['description'][:70]} | " + " ; ".join(i["description"][:60] for i in v["items"]))

sys.stdout.flush()
os._exit(0)   # pcbnew tends to segfault while Python tears down its SWIG objects
