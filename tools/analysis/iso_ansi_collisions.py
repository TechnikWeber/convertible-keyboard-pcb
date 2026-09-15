"""Hole/copper collisions between ISO keys and their ANSI alternatives (drill-to-drill and copper < 0.25 mm)."""
import re, math, itertools, sys
import os
LIB=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib/MX_Alps_Hybrid/MX_Only.pretty/")
def pads(name):
    s=open(LIB+name+".kicad_mod").read()
    out=[]
    for m in re.finditer(r'\(pad\s+"?([^"\s]*)"?\s+(\w+)\s+(\w+)\s+\(at ([-\d.]+) ([-\d.]+)[^)]*\)\s+\(size ([\d.]+) [\d.]+\)\s+\(drill ([\d.]+)\)', s):
        num,typ,shape,x,y,size,drill=m.groups()
        out.append(dict(num=num,typ=typ,x=float(x),y=float(y),r=float(size)/2,dr=float(drill)/2))
    return out
def place(name,cx,cy,nets):
    return [dict(p,x=p['x']+cx,y=p['y']+cy,net=nets.get(p['num'])) for p in pads(name)]
def check(A,B,label):
    worst=[]
    for p,q in itertools.product(A,B):
        d=math.hypot(p['x']-q['x'],p['y']-q['y'])
        hole=d-(p['dr']+q['dr'])            # drill to drill
        cu=None
        if p['typ']=='thru_hole' and q['typ']=='thru_hole' and p['net']!=q['net']:
            cu=d-(p['r']+q['r'])
        elif p['typ']=='thru_hole' and q['typ']=='np_thru_hole': cu=d-(p['r']+q['dr'])
        elif q['typ']=='thru_hole' and p['typ']=='np_thru_hole': cu=d-(q['r']+p['dr'])
        bad=[]
        if hole<0.25: bad.append(f"Bohrung-Bohrung {hole:+.2f}")
        if cu is not None and cu<0.25: bad.append(f"Kupfer {cu:+.2f}")
        if bad: worst.append(f"   {p['num'] or 'NPTH'}({p['x']:.2f},{p['y']:.2f}) ↔ {q['num'] or 'NPTH'}({q['x']:.2f},{q['y']:.2f}): "+", ".join(bad))
    print(f"{label}: {'frei' if not worst else str(len(worst))+' Konflikte'}"); [print(w) for w in worst]
u=19.05
ISOENT=(302.41875,95.25); HASH=(280.9875,104.775); RBR=(276.225,85.725); BKSP=(295.275,66.675)
LSH_ISO=(40.48125,123.825); LTGT=(61.9125,123.825); CAPS=(45.24375,104.775); LCTRL=(40.48125,142.875); A_KEY=(71.4375,104.775); Z=(80.9625,123.825); WIN=(64.29375,142.875)
ANSI_BS=(314.325-1.5*u/2,85.725); ANSI_ENT=(314.325-2.25*u/2,104.775); ANSI_LSH=(28.575+2.25*u/2,123.825)
def n(col,rowd,led): return {'1':col,'2':rowd,'3':led+'A','4':'BL_K'}
for bsv in ["MXOnly-1.5U","MXOnly-1.5U-FLIPPED"]:
  for isov in ["MXOnly-ISO","MXOnly-ISO-ReversedStabilizers","MXOnly-ISO-ROTATED","MXOnly-ISO-ROTATED-ReversedStabilizers"]:
    print(f"\n== Backslash {bsv} / ISO {isov}")
    iso=place(isov,*ISOENT,n('COL13','D71','L71'))
    check(place(bsv,*ANSI_BS,n('COL13','D106','L106')),iso,"  BS vs ISO-Enter")
for entv in ["MXOnly-2.25U","MXOnly-2.25U-ReversedStabilizers"]:
  for isov in ["MXOnly-ISO","MXOnly-ISO-ReversedStabilizers"]:
    print(f"\n== ANSI-Enter {entv} / ISO {isov}")
    e=place(entv,*ANSI_ENT,n('COL13','D107','L107'))
    check(e,place(isov,*ISOENT,n('COL13','D71','L71')),"  Enter vs ISO-Enter")
    check(e,place("MXOnly-1U",*HASH,n('COL12','D70','L70')),"  Enter vs #")
    check(e,place("MXOnly-1U",*RBR,n('COL12','D50','L50')),"  Enter vs ]")
    check(e,place("MXOnly-2U",*BKSP,n('COL13','D30','L30')),"  Enter vs Backspace")
for bsv in ["MXOnly-1.5U","MXOnly-1.5U-FLIPPED"]:
    print(f"\n== ANSI-Backslash {bsv} Nachbarn")
    b=place(bsv,*ANSI_BS,n('COL13','D106','L106'))
    check(b,place("MXOnly-1U",*RBR,n('COL12','D50','L50')),"  BS vs ]")
    check(b,place("MXOnly-2U",*BKSP,n('COL13','D30','L30')),"  BS vs Backspace")
    check(b,place("MXOnly-2.25U",*ANSI_ENT,n('COL13','D107','L107')),"  BS vs ANSI-Enter")
for lv in ["MXOnly-2.25U","MXOnly-2.25U-ReversedStabilizers"]:
    print(f"\n== ANSI-LShift {lv}")
    l=place(lv,*ANSI_LSH,n('COL0','D108','L108'))
    check(l,place("MXOnly-1.25U",*LSH_ISO,n('COL0','D75','L75')),"  vs ISO-LShift")
    check(l,place("MXOnly-1U",*LTGT,n('COL1','D76','L76')),"  vs <>")
    check(l,place("MXOnly-1.75U",*CAPS,n('COL0','D58','L58')),"  vs Caps")
    check(l,place("MXOnly-1U",*A_KEY,n('COL1','D59','L59')),"  vs A")
    check(l,place("MXOnly-1U",*Z,n('COL2','D77','L77')),"  vs Z")
    check(l,place("MXOnly-1.25U",*LCTRL,n('COL0','D93','L93')),"  vs LCtrl")
    check(l,place("MXOnly-1.25U",*WIN,n('COL1','D94','L94')),"  vs Win")
