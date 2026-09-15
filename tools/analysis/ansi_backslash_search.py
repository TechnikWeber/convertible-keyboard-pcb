"""Brute-force search: footprint variant, rotation and pin-net swap for ANSI backslash vs. ISO Enter.
Only the unlit 1.5u switch rotated 270° is free of collisions (NPTH-NPTH overlaps aside)."""
import re, math, itertools
import os
LIB=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib/MX_Alps_Hybrid/MX_Only.pretty/")
def pads(name):
    s=open(LIB+name+".kicad_mod").read(); out=[]
    for m in re.finditer(r'\(pad\s+"?([^"\s]*)"?\s+(\w+)\s+(\w+)\s+\(at ([-\d.]+) ([-\d.]+)[^)]*\)\s+\(size ([\d.]+) [\d.]+\)\s+\(drill ([\d.]+)\)', s):
        num,typ,shape,x,y,size,drill=m.groups()
        out.append(dict(num=num,typ=typ,x=float(x),y=float(y),r=float(size)/2,dr=float(drill)/2))
    return out
def place(name,cx,cy,rot,nets):
    t=math.radians(rot); c,s=round(math.cos(t)),round(math.sin(t)); res=[]
    for p in pads(name):
        x,y=p['x'],p['y']; X=cx+x*c+y*s; Y=cy-x*s+y*c   # KiCad board rotation (CCW on screen)
        res.append(dict(p,x=X,y=Y,net=nets.get(p['num'])))
    return res
def conflicts(A,B):
    bad=[]
    for p,q in itertools.product(A,B):
        d=math.hypot(p['x']-q['x'],p['y']-q['y'])
        if d-(p['dr']+q['dr'])<0.25: bad.append(('hole',p['num'],q['num'],round(d-(p['dr']+q['dr']),2)))
        if p['typ']=='thru_hole' and q['typ']=='thru_hole' and p['net']!=q['net'] and d-(p['r']+q['r'])<0.25: bad.append(('cu',p['num'],q['num'],round(d-(p['r']+q['r']),2)))
        if p['typ']!=q['typ'] and d-((p['r'] if p['typ']=='thru_hole' else p['dr'])+(q['r'] if q['typ']=='thru_hole' else q['dr']))<0.25: bad.append(('cu-npth',p['num'],q['num']))
    return bad
u=19.05
ISO=(302.41875,95.25); BS=(314.325-1.5*u/2,85.725)
res=[]
for bsv in ["MXOnly-1.5U","MXOnly-1.5U-FLIPPED","MXOnly-1.5U-NoLED"]:
 for isov in ["MXOnly-ISO","MXOnly-ISO-ReversedStabilizers","MXOnly-ISO-ROTATED","MXOnly-ISO-ROTATED-ReversedStabilizers"]:
  for br in (0,90,180,270):
   for ir in (0,180):
    for bswap in (False,True):
     for iswap in (False,True):
      bn={'1':'COL13','2':'D106'} if not bswap else {'1':'D106','2':'COL13'}; bn.update({'3':'L106','4':'BL_K'})
      inn={'1':'COL13','2':'D71'} if not iswap else {'1':'D71','2':'COL13'}; inn.update({'3':'L71','4':'BL_K'})
      c=conflicts(place(bsv,*BS,br,bn),place(isov,*ISO,ir,inn))
      hard=[x for x in c if x[0]!='hole' or not (x[1]=='' and x[2]=='')]   # NPTH-NPTH overlaps = soft
      res.append((len(hard),len(c),bsv,br,bswap,isov,ir,iswap,c))
res.sort(key=lambda r:(r[0],r[1]))
for r in res[:12]: print(r[0],r[1],r[2],"rot",r[3],"swap",r[4],"|",r[5],"rot",r[6],"swap",r[7],r[8])
