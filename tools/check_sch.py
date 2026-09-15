#!/usr/bin/env python3
"""Upgrade, ERC and netlist check against out/expect.json."""
import sys, os, json, subprocess, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kicadlib import parse, find, findall

PRJ = os.path.dirname(HERE)
NAME = "convertible-keyboard-pcb"
SCH = f"{PRJ}/{NAME}.kicad_sch"
OUT = f"{HERE}/build"


def run(*a):
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode not in (0, 5):
        print("FAILED:", " ".join(a), r.stdout[-800:], r.stderr[-800:])
        sys.exit(1)
    return r


run("kicad-cli", "sch", "upgrade", "--force", SCH)
run("kicad-cli", "sch", "erc", "--format", "json", "--severity-all", "-o", f"{OUT}/erc.json", SCH)
run("kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", f"{OUT}/{NAME}.net", SCH)

erc = json.load(open(f"{OUT}/erc.json"))
cnt = collections.Counter()
details = collections.defaultdict(list)
for sheet in erc["sheets"]:
    for v in sheet["violations"]:
        cnt[(v["severity"], v["type"])] += 1
        details[v["type"]].append(sheet["path"] + " " + v["description"] + " | " +
                                  "; ".join(i["description"] for i in v["items"]))
print("ERC:", dict(cnt))
for t, d in details.items():
    for line in d[:6]:
        print(f"  [{t}] {line}")
    if len(d) > 6:
        print(f"  [{t}] ... {len(d) - 6} more")

nl = parse(open(f"{OUT}/{NAME}.net").read())
pinnet = {}
for n in findall(find(nl, "nets"), "net"):
    name = find(n, "name")[1]
    for nd in findall(n, "node"):
        pinnet[(find(nd, "ref")[1], find(nd, "pin")[1])] = name
exp = {tuple(k.split("|")): v for k, v in json.load(open(f"{OUT}/expect.json")).items()}
bad = []
groups = collections.defaultdict(set)
for (ref, pin), want in exp.items():
    got = pinnet.get((ref, pin))
    if got is None:
        bad.append(f"{ref}.{pin}: not in netlist (want {want})")
    elif want is None:
        if not got.startswith("unconnected-"):
            bad.append(f"{ref}.{pin}: want NC, got {got}")
    elif want.startswith("~"):
        groups[want].add(got)
    elif got.split("/")[-1] != want:
        bad.append(f"{ref}.{pin}: want {want}, got {got}")
for g, nets in groups.items():
    if len(nets) != 1:
        bad.append(f"group {g}: split over {nets}")
# net sanity: group nets must not collide with each other
seen = collections.Counter(next(iter(n)) for n in groups.values() if len(n) == 1)
bad += [f"groups share net {n}" for n, c in seen.items() if c > 1]
# matrix sanity for all switches
comps = [find(c, "ref")[1] for c in findall(find(nl, "components"), "comp")]
for ref in comps:
    if ref.startswith("SW") and ref[2:].isdigit() and int(ref[2:]) <= 108:
        n = ref[2:]
        a, b_ = pinnet.get((ref, "1")), pinnet.get((ref, "2"))
        dnet, rnet = pinnet.get((f"D{n}", "2")), pinnet.get((f"D{n}", "1"))
        cols = [x for x in (a, b_) if x and x.startswith("COL")]
        if len(cols) != 1 or dnet not in (a, b_) or not (rnet or "").startswith("ROW"):
            bad.append(f"matrix {ref}: pins {a},{b_} diode {dnet}->{rnet}")
print(f"netlist: {len(comps)} components, {len(exp)} expected connections checked, {len(bad)} problems")
for b in bad[:40]:
    print("  ", b)
