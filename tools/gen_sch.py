#!/usr/bin/env python3
"""Builds the schematic on top of the base root sheet.

Stage 1: ANSI alternatives (SW106-108, D106-108), ISO Enter pin swap.
Stage 2: backlight - SW_MX_LED symbols, LED units, resistors, MOSFET drivers.
Stage 3: MCU sheet - RP2040, flash, crystal, LDO, USB-C, ESD, buttons, SWD pads.
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kicadlib import *
import uuid as _uuid, itertools

_UID_NS = _uuid.UUID("5b1f3c1e-6d2a-4c1b-9a8e-3f7d2c4b5a60")
_uid_counter = itertools.count()


def uid():
    """Deterministic UUIDs: re-running the generator keeps symbol paths and PCB links stable."""
    return str(_uuid.uuid5(_UID_NS, str(next(_uid_counter))))


PRJ = os.path.dirname(HERE)
OUT = os.path.join(HERE, "build")
NAME = "convertible-keyboard-pcb"
STAGE = int(sys.argv[1])
KBLIB = PRJ + "/lib/keyboard.kicad_sym"
U = 2.54
R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"

EXPECT = {}
COUNT = {"#PWR": 0, "#FLG": 0}
POWER = {"GND", "+5V", "+3V3", "+1V1", "VBUS"}
GLOBAL = {f"ROW{i}" for i in range(6)} | {f"COL{i}" for i in range(21)} | {"BL_PWM", "CAPS_LED", "NUM_LED"}
ANG = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}
JUST = {0: "left", 90: "left", 180: "right", 270: "right"}


def prop(sym, key):
    for p in findall(sym, "property"):
        if p[1] == key:
            return p
    return None


def effects(justify=None, size=1.27):
    e = S("effects", S("font", S("size", size, size)))
    if justify:
        e.append([Sym("justify")] + [Sym(j) for j in justify.split()])
    return e


class Sheet:
    def __init__(self, tree, path):
        self.tree, self.path = tree, path
        self.libs = find(tree, "lib_symbols")

    def lib(self, lib, name):
        full = f"{lib}:{name}"
        for s in findall(self.libs, "symbol"):
            if s[1] == full:
                return s
        s = lib_symbol(lib, name, KBLIB if lib == "keyboard" else None)
        self.libs.append(s)
        return s

    def add(self, node):
        tail = 0
        while isinstance(self.tree[-1 - tail], list) and self.tree[-1 - tail][0] in ("sheet_instances", "embedded_fonts"):
            tail += 1
        self.tree.insert(len(self.tree) - tail, node)


class Placed:
    def __init__(self, libsym, ref, x, y, rot, unit):
        self.ref = ref
        self.pins = {}
        for p in pins(libsym):
            if p["unit"] in (0, unit):
                self.pins[p["num"]] = (to_screen(x, y, rot, p["x"], p["y"]), pin_dir(rot, p["a"]))
        self.byname = {}
        for p in pins(libsym):
            if p["unit"] in (0, unit):
                self.byname.setdefault(p["name"].split("/")[0], []).append(p["num"])

    def pin(self, n):
        return self.pins[n]


def symbol(sh, lib, name, ref, x, y, rot=0, unit=1, value=None, footprint="", fpos=None, hide_value=False,
           in_bom=True):
    ls = sh.lib(lib, name)
    fpos = fpos or {}
    node = S("symbol", S("lib_id", f"{lib}:{name}"), S("at", x, y, rot), S("unit", unit), S("body_style", 1),
             S("exclude_from_sim", Sym("no")), S("in_bom", Sym("yes" if in_bom else "no")), S("on_board", Sym("yes")),
             S("in_pos_files", Sym("yes")), S("dnp", Sym("no")), S("uuid", uid()))
    for key in ("Reference", "Value", "Footprint", "Datasheet", "Description"):
        lp = prop(ls, key)
        v = {"Reference": ref, "Value": value if value is not None else (lp[2] if lp else name),
             "Footprint": footprint}.get(key, lp[2] if lp else "")
        if key in fpos:
            dx, dy, just = fpos[key]
            px, py = x + dx, y + dy
        else:
            at = find(lp, "at") if lp else None
            px, py = to_screen(x, y, rot, float(at[1]), float(at[2])) if at else (x, y)
            eff = find(lp, "effects") if lp else None
            j = find(eff, "justify") if eff else None
            just = " ".join(str(t) for t in j[1:]) if j else None
        lib_hidden = lp is not None and find(lp, "hide") is not None and find(lp, "hide")[1] == "yes"
        hidden = key in ("Footprint", "Datasheet", "Description") or lib_hidden or (key == "Value" and hide_value)
        # field angles are relative to the symbol: 90° on a rotated symbol reads horizontally
        p = S("property", key, v, S("at", px, py, 90 if rot in (90, 270) else 0))
        if hidden:
            p.append(S("hide", Sym("yes")))
        p.append(effects(just))
        node.append(p)
    placed = Placed(ls, ref, x, y, rot, unit)
    for n in placed.pins:
        node.append(S("pin", n, S("uuid", uid())))
    node.append(S("instances", S("project", NAME, S("path", sh.path, S("reference", ref), S("unit", unit)))))
    sh.add(node)
    return placed


def wire(sh, a, b):
    if a != b:
        sh.add(S("wire", S("pts", S("xy", *a), S("xy", *b)), S("stroke", S("width", 0), S("type", Sym("default"))),
                 S("uuid", uid())))


def junction(sh, p):
    sh.add(S("junction", S("at", *p), S("diameter", 0), S("color", 0, 0, 0, 0), S("uuid", uid())))


def no_connect(sh, p):
    sh.add(S("no_connect", S("at", *p), S("uuid", uid())))


def label(sh, name, p, ang, glob=None, shape="bidirectional"):
    glob = name in GLOBAL if glob is None else glob
    if glob:
        sh.add(S("global_label", name, S("shape", Sym(shape)), S("at", *p, ang), S("fields_autoplaced", Sym("yes")),
                 effects(JUST[ang]), S("uuid", uid()),
                 S("property", "Intersheetrefs", "${INTERSHEET_REFS}", S("at", *p, 0), S("hide", Sym("yes")),
                   effects(JUST[ang]))))
    else:
        sh.add(S("label", name, S("at", *p, ang), S("fields_autoplaced", Sym("yes")),
                 effects(JUST[ang] + " bottom"), S("uuid", uid())))


def text(sh, s, x, y, size=1.27):
    sh.add(S("text", s, S("exclude_from_sim", Sym("no")), S("at", x, y, 0), effects("left top", size), S("uuid", uid())))


def power(sh, net, p, out):
    if net == "GND":
        rot = {(0, 1): 0, (0, -1): 180, (1, 0): 90, (-1, 0): 270}[out]
    else:
        rot = {(0, -1): 0, (0, 1): 180, (1, 0): 270, (-1, 0): 90}[out]
    COUNT["#PWR"] += 1
    symbol(sh, "power", net, f"#PWR{COUNT['#PWR']:04d}", p[0], p[1], rot)


def pwr_flag(sh, p, out=(0, -1)):
    COUNT["#FLG"] += 1
    rot = {(0, -1): 0, (0, 1): 180, (1, 0): 270, (-1, 0): 90}[out]
    symbol(sh, "power", "PWR_FLAG", f"#FLG{COUNT['#FLG']:02d}", p[0], p[1], rot)


def connect(sh, pl, mapping, stub=U):
    """mapping {pin: net | None}. Pins stacked on one point are drawn once."""
    bypos = {}
    for n, net in mapping.items():
        EXPECT[(pl.ref, n)] = net
        p, out = pl.pin(n)
        bypos.setdefault(p, (out, set()))[1].add(net)
    for p, (out, nets) in bypos.items():
        assert len(nets) == 1, (pl.ref, p, nets)
        net = next(iter(nets))
        if net is None:
            no_connect(sh, p)
        elif net in POWER and out[1] == 0:
            q = (round(p[0] + out[0] * 2 * stub, 4), p[1])   # side pin: short stub, symbol upright
            wire(sh, p, q)
            power(sh, net, q, (0, 1) if net == "GND" else (0, -1))
        elif net in POWER:
            power(sh, net, p, out)
        else:
            q = (round(p[0] + out[0] * stub, 4), round(p[1] + out[1] * stub, 4))
            wire(sh, p, q)
            label(sh, net, q, ANG[out])


def two_pin(sh, lib, name, ref, value, fp, x, y, n1, n2):
    pl = symbol(sh, lib, name, ref, x, y, 0, value=value, footprint=fp,
                fpos={"Reference": (2.032, -0.635, "left"), "Value": (2.032, 1.905, "left")})
    connect(sh, pl, {"1": n1, "2": n2})
    return pl


def rail(sh, pl, pinnums, net, y_rail, end="left"):
    pts = sorted({pl.pin(n)[0] for n in pinnums})
    for n in pinnums:
        EXPECT[(pl.ref, n)] = net
    xs = [p[0] for p in pts]
    for x, y in pts:
        wire(sh, (x, y), (x, y_rail))
    for a, b in zip(xs, xs[1:]):
        wire(sh, (a, y_rail), (b, y_rail))
    for x in xs[1:-1]:
        junction(sh, (x, y_rail))
    power(sh, net, (xs[0] if end == "left" else xs[-1], y_rail), (0, -1))


def new_sheet(title):
    return S("kicad_sch", S("version", 20260306), S("generator", "eeschema"), S("generator_version", "10.0"),
             S("uuid", uid()), S("paper", "A3"), S("title_block", S("title", title), S("company", NAME)),
             [Sym("lib_symbols")], S("embedded_fonts", Sym("no")))


def sheet_symbol(sh, root_uuid, name, fname, x, y, w, h, page):
    u = uid()
    sh.add(S("sheet", S("at", x, y), S("size", w, h), S("exclude_from_sim", Sym("no")), S("in_bom", Sym("yes")),
             S("on_board", Sym("yes")), S("dnp", Sym("no")), S("fields_autoplaced", Sym("yes")),
             S("stroke", S("width", 0.1524), S("type", Sym("solid"))), S("fill", S("color", 0, 0, 0, 0)),
             S("uuid", u),
             S("property", "Sheetname", name, S("at", x, y - 0.7116, 0), effects("left bottom")),
             S("property", "Sheetfile", fname, S("at", x, y + h + 0.5846, 0), effects("left top")),
             S("instances", S("project", NAME, S("path", "/" + root_uuid, S("page", str(page)))))))
    return u


# ------------------------------------------------------------ keyboard symbol lib
def write_kblib():
    sw = lib_symbol("Switch", "SW_Push_45deg")
    led = lib_symbol("Device", "LED_Small")
    sym = [Sym("symbol"), "SW_MX_LED",
           S("pin_numbers", S("hide", Sym("yes"))),
           S("pin_names", S("offset", 1.016), S("hide", Sym("yes")))]
    for item in sw[2:]:
        if not isinstance(item, list) or item[0] in ("symbol", "pin_numbers", "pin_names", "embedded_fonts"):
            continue
        if item[0] == "property":
            item = [x for x in item]
            item[2] = {"Value": "SW_MX_LED",
                       "Description": "MX key switch with in-switch LED. Unit A: switch, unit B: LED "
                                      "(pin 3 anode, pin 4 cathode - matches the ai03 MX_Only LED footprints)",
                       "ki_keywords": "switch mx key led backlight"}.get(item[1], item[2])
        sym.append(item)
    u1 = [Sym("symbol"), "SW_MX_LED_1_1"]
    for sub in findall(sw, "symbol"):
        u1 += [x for x in sub[2:]]
    u2 = [Sym("symbol"), "SW_MX_LED_2_1"]
    for sub in findall(led, "symbol"):
        for x in sub[2:]:
            if isinstance(x, list) and x[0] == "pin":
                find(x, "number")[1] = "3" if find(x, "name")[1] == "A" else "4"
            u2.append(x)
    sym += [u1, u2, S("embedded_fonts", Sym("no"))]
    tree = S("kicad_symbol_lib", S("version", 20251024), S("generator", "kicad_symbol_editor"),
             S("generator_version", "10.0"), sym)
    open(KBLIB, "w").write(dumps(tree) + "\n")
    open(PRJ + "/sym-lib-table", "w").write(
        '(sym_lib_table\n\t(version 7)\n\t(lib (name "keyboard") (type "KiCad") '
        '(uri "${KIPRJMOD}/lib/keyboard.kicad_sym") (options "") (descr "Project symbols"))\n)\n')


# ============================================================ root sheet
root = parse(git_base(PRJ, f"{NAME}.kicad_sch"))
ROOT_UUID = find(root, "uuid")[1]
R = Sheet(root, "/" + ROOT_UUID)
refsym = {prop(s, "Reference")[2]: s for s in findall(root, "symbol")}
tb = find(root, "title_block")
tb[1:] = [S("title", NAME), S("comment", 1, "Key matrix generated with kicad-kbplacer (github.com/adamws/kicad-kbplacer)")]


def matrix_key(sh, n, x, y, rot, col, row, fp):
    sw = symbol(sh, "Switch", "SW_Push_45deg", f"SW{n}", x, y, rot, value="SW_Push", footprint=fp, hide_value=True,
                fpos={"Reference": (0, -5.08, None)})
    d = symbol(sh, "Device", "D_Small", f"D{n}", x + U, y + 3.5 * U, 90, value="D",
               footprint="Diode_SMD:D_SOD-123", hide_value=True)
    ul, dr = ("1", "2") if rot == 0 else ("2", "1")
    (pu, _), (pd, _) = sw.pin(ul), sw.pin(dr)
    q = (pu[0] - U, pu[1])
    wire(sh, pu, q)
    label(sh, col, q, 180, True, "input")
    (pa, _), (pk, _) = d.pin("2"), d.pin("1")
    wire(sh, pd, pa)
    q = (pk[0], pk[1] + U)
    wire(sh, pk, q)
    label(sh, row, q, 270, True, "input")
    EXPECT.update({(f"SW{n}", ul): col, (f"SW{n}", dr): f"~D{n}A", (f"D{n}", "2"): f"~D{n}A", (f"D{n}", "1"): row})


if STAGE >= 1:
    find(refsym["SW71"], "at")[3] = num(180)
    EXPECT.update({("SW71", "1"): "~D71A", ("D71", "2"): "~D71A", ("SW71", "2"): "COL13"})
    text(R, "ANSI alternatives - populate instead of the matching ISO keys\\n"
            "SW106  Backslash 1.5u: no LED, switch rotated 270° on the PCB (clears the ISO Enter stabilizer)\\n"
            "SW107  Enter 2.25u: same matrix position as ISO Enter SW71 (ROW3 / COL13)\\n"
            "SW108  Left Shift 2.25u: same matrix position as ISO Left Shift SW75 (ROW4 / COL0)\\n"
            "SW71 is drawn rotated 180°: pin 2 = COL13, pin 1 = diode (keeps its pads clear of SW106)", 302.26, 12.7)
    matrix_key(R, 106, 322.58, 38.1, 180, "COL13", "ROW2", "MX_Only:MXOnly-1.5U-NoLED")
    matrix_key(R, 107, 342.9, 38.1, 0, "COL13", "ROW3", "MX_Only:MXOnly-2.25U-NoLED")
    matrix_key(R, 108, 363.22, 38.1, 0, "COL0", "ROW4", "MX_Only:MXOnly-2.25U-NoLED")

sheets = {}

# ============================================================ backlight
if STAGE >= 2:
    # LED cathode (square pad) moved away from the stabilizer holes of the alternative layout keys
    LED_FP = {"SW71": "keyboard:MXOnly-ISO-FLIPPED", "SW76": "MX_Only:MXOnly-1U-FLIPPED",
              "SW107": "MX_Only:MXOnly-2.25U-FLIPPED"}
    write_kblib()
    lit = []
    for s in findall(root, "symbol"):
        ref = prop(s, "Reference")[2]
        if not ref.startswith("SW") or ref == "SW106":
            continue
        find(s, "lib_id")[1] = "keyboard:SW_MX_LED"
        prop(s, "Footprint")[2] = LED_FP.get(ref, prop(s, "Footprint")[2].replace("-NoLED", ""))
        prop(s, "Value")[2] = "SW_MX_LED"
        if not any(pn[1] in ("3", "4") for pn in findall(s, "pin")):   # KiCad lists all unit pins per instance
            last = max(i for i, x in enumerate(s) if isinstance(x, list) and x[0] == "pin")
            s[last + 1:last + 1] = [S("pin", n, S("uuid", str(_uuid.uuid5(_UID_NS, f"{ref}-pin{n}"))))
                                    for n in ("3", "4")]
        lit.append((int(ref[2:]), prop(s, "Footprint")[2]))
    R.lib("keyboard", "SW_MX_LED")
    for s in findall(R.libs, "symbol"):
        pass
    bl_uuid = sheet_symbol(R, ROOT_UUID, "Backlight", "backlight.kicad_sch", 302.26, 71.12, 38.1, 10.16, 2)
    bl = new_sheet("Backlight")
    B = Sheet(bl, f"/{ROOT_UUID}/{bl_uuid}")
    sheets["backlight.kicad_sch"] = bl
    LOCK = {58: "CAPS_K", 34: "NUM_K"}
    lit.sort()
    x0, y0, dx, dy, cols = 22.86, 38.1, 30.48, 22.86, 12
    text(B, "Backlight - every lit key has its own LED (unit B of the switch symbol) and series resistor.\\n"
            "The through-hole LEDs are optional; resistors and drivers are always populated.\\n"
            "LED pin 3 = anode, pin 4 = cathode. 1k gives about 2 mA per white LED at 5 V.\\n"
            "Caps Lock (SW58) and Num Lock (SW34) LEDs are lock indicators with their own drivers.\\n"
            "SW106 (ANSI backslash) has no LED.", 22.86, 12.7)
    for i, (n, fp) in enumerate(lit):
        cx, cy = x0 + (i % cols) * dx, y0 + (i // cols) * dy
        r = symbol(B, "Device", "R_Small", f"R{n}", cx, cy + 2 * U, 0, value="1k", footprint=R0603,
                   fpos={"Reference": (2.032, -0.635, "left"), "Value": (2.032, 1.905, "left")})
        led = symbol(B, "keyboard", "SW_MX_LED", f"SW{n}", cx, cy + 5 * U, 90, unit=2, value="SW_MX_LED",
                     footprint=fp, hide_value=True, fpos={"Reference": (6.35, 0, None)})
        connect(B, r, {"1": "+5V"})
        wire(B, r.pin("2")[0], led.pin("3")[0])
        EXPECT.update({(f"R{n}", "2"): f"~R{n}", (f"SW{n}", "3"): f"~R{n}"})
        pk = led.pin("4")[0]
        q = (pk[0], round(pk[1] + U, 4))
        wire(B, pk, q)
        net = LOCK.get(n, "BL_K")
        label(B, net, q, 0)
        EXPECT[(f"SW{n}", "4")] = net

    def driver(x, y, qref, part, g_net, d_net, rg, rpd):
        q = symbol(B, "Transistor_FET", part, qref, x, y, 0, value=part, footprint="Package_TO_SOT_SMD:SOT-23")
        pg, pd = q.pin("1")[0], q.pin("3")[0]
        connect(B, q, {"2": "GND"})
        t = (pd[0], round(pd[1] - U, 4))
        wire(B, pd, t)
        label(B, d_net, t, 90)
        EXPECT.update({(qref, "3"): d_net, (qref, "1"): f"~G{qref}"})
        r1 = symbol(B, "Device", "R_Small", rg, pg[0] - U, pg[1], 90, value="100", footprint=R0603,
                    fpos={"Reference": (0, -2.54, "left"), "Value": (0, 2.54, "left")})
        connect(B, r1, {"1": g_net})
        EXPECT[(rg, "2")] = f"~G{qref}"
        r2 = symbol(B, "Device", "R_Small", rpd, pg[0], pg[1] + 2 * U, 0, value="100k", footprint=R0603,
                    fpos={"Reference": (-2.032, -0.635, "right"), "Value": (-2.032, 1.905, "right")})
        wire(B, pg, r2.pin("1")[0])
        junction(B, pg)
        connect(B, r2, {"2": "GND"})
        EXPECT[(rpd, "1")] = f"~G{qref}"

    text(B, "Drivers - low-side N-MOSFETs switched by the RP2040 (QMK: BACKLIGHT_DRIVER = pwm)", 22.86, 248.92)
    driver(50.8, 266.7, "Q1", "AO3400A", "BL_PWM", "BL_K", "R121", "R122")
    driver(127.0, 266.7, "Q2", "2N7002", "CAPS_LED", "CAPS_K", "R123", "R124")
    driver(203.2, 266.7, "Q3", "2N7002", "NUM_LED", "NUM_K", "R125", "R126")

# ============================================================ MCU
if STAGE >= 3:
    mcu_uuid = sheet_symbol(R, ROOT_UUID, "MCU", "mcu.kicad_sch", 302.26, 91.44, 38.1, 10.16, 3)
    mt = new_sheet("MCU, USB and power")
    M = Sheet(mt, f"/{ROOT_UUID}/{mcu_uuid}")
    sheets["mcu.kicad_sch"] = mt

    # --- USB-C
    text(M, "USB-C (USB 2.0, 5 V default power)", 22.86, 30.48, 2)
    J1 = symbol(M, "Connector", "USB_C_Receptacle_USB2.0_16P", "J1", 40.64, 60.96, value="USB_C",
                footprint="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12")
    connect(M, J1, {"A4": "VBUS", "A9": "VBUS", "B4": "VBUS", "B9": "VBUS", "A5": "CC1", "B5": "CC2",
                    "A6": "USB_CONN_DP", "B6": "USB_CONN_DP", "A7": "USB_CONN_DM", "B7": "USB_CONN_DM",
                    "A8": None, "B8": None, "A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND", "SH": "SHIELD"})
    two_pin(M, "Device", "R_Small", "R201", "5k1", R0603, 81.28, 60.96, "CC1", "GND")
    two_pin(M, "Device", "R_Small", "R202", "5k1", R0603, 91.44, 60.96, "CC2", "GND")
    two_pin(M, "Device", "R_Small", "R203", "1M", R0603, 101.6, 60.96, "SHIELD", "GND")
    two_pin(M, "Device", "C_Small", "C201", "4n7", C0603, 111.76, 60.96, "SHIELD", "GND")
    U4 = symbol(M, "Power_Protection", "USBLC6-2SC6", "U4", 86.36, 104.14, value="USBLC6-2SC6",
                footprint="Package_TO_SOT_SMD:SOT-23-6")
    connect(M, U4, {"1": "USB_CONN_DP", "6": "USB_CONN_DP", "3": "USB_CONN_DM", "4": "USB_CONN_DM",
                    "5": "VBUS", "2": "GND"})
    two_pin(M, "Device", "Polyfuse_Small", "F1", "500mA", "Fuse:Fuse_1206_3216Metric", 121.92, 104.14, "VBUS", "+5V")
    two_pin(M, "Device", "R_Small", "R204", "27", R0603, 137.16, 104.14, "USB_CONN_DP", "USB_DP")
    two_pin(M, "Device", "R_Small", "R205", "27", R0603, 149.86, 104.14, "USB_CONN_DM", "USB_DM")
    for i, net in enumerate(("VBUS", "+5V", "GND")):
        p = (124.46 + i * 10.16, 124.46)
        power(M, net, p, (0, 1) if net == "GND" else (0, -1))
        pwr_flag(M, p, (0, -1) if net == "GND" else (0, 1))

    # --- 3.3 V
    text(M, "3.3 V regulator", 22.86, 121.92, 2)
    U3 = symbol(M, "Regulator_Linear", "AP2112K-3.3", "U3", 58.42, 139.7, value="AP2112K-3.3",
                footprint="Package_TO_SOT_SMD:SOT-23-5",
                fpos={"Reference": (-5.08, -7.62, "left"), "Value": (3.81, 7.62, "left")})
    wire(M, U3.pin("3")[0], U3.pin("1")[0])
    connect(M, U3, {"1": "+5V", "2": "GND", "4": None, "5": "+3V3"})
    EXPECT[("U3", "3")] = "+5V"
    two_pin(M, "Device", "C_Small", "C202", "10u", C0805, 38.1, 144.78, "+5V", "GND")
    two_pin(M, "Device", "C_Small", "C203", "10u", C0805, 78.74, 144.78, "+3V3", "GND")

    # --- RP2040
    text(M, "RP2040 - one 100n per IOVDD pin, placed next to the pins", 165.1, 55.88, 2)
    U1 = symbol(M, "MCU_RaspberryPi", "RP2040", "U1", 228.6, 149.86, value="RP2040",
                footprint="Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm")
    bn = U1.byname
    gpio = {}
    for i in range(30):
        gpio[bn[f"GPIO{i}"][0]] = (f"COL{i}" if i <= 20 else f"ROW{i - 21}" if i <= 26 else
                                   {27: "BL_PWM", 28: "CAPS_LED", 29: "NUM_LED"}[i])
    m = dict(gpio)
    for nm, net in (("SWDIO", "SWDIO"), ("SWCLK", "SWCLK"), ("XOUT", "XOUT"), ("XIN", "XIN"),
                    ("QSPI_SD0", "QSPI_SD0"), ("QSPI_SD1", "QSPI_SD1"), ("QSPI_SD2", "QSPI_SD2"),
                    ("QSPI_SD3", "QSPI_SD3"), ("QSPI_SCLK", "QSPI_SCLK"), ("~{QSPI_SS}", "QSPI_SS"),
                    ("USB_DP", "USB_DP"), ("USB_DM", "USB_DM"), ("RUN", "RUN"), ("TESTEN", "GND"), ("GND", "GND")):
        for n in bn[nm]:
            m[n] = net
    connect(M, U1, m)
    rail(M, U1, bn["USB_VDD"] + bn["ADC_AVDD"] + bn["IOVDD"] + bn["VREG_VIN"], "+3V3", 99.06, "left")
    rail(M, U1, bn["VREG_VOUT"] + bn["DVDD"], "+1V1", 99.06, "right")
    caps = [("100n", "+3V3")] * 6 + [("100n", "+3V3"), ("100n", "+3V3"), ("1u", "+3V3"),
                                     ("1u", "+1V1"), ("100n", "+1V1"), ("100n", "+1V1")]
    for i, (val, net) in enumerate(caps):
        two_pin(M, "Device", "C_Small", f"C{210 + i}", val, C0603, 165.1 + i * 10.16, 76.2, net, "GND")
    text(M, "C210-C215: IOVDD (6x)   C216: USB_VDD   C217: ADC_AVDD   C218: VREG_VIN\\n"
            "C219: VREG_VOUT   C220, C221: DVDD", 165.1, 83.82)
    text(M, "GPIO assignment\\nGPIO0-GPIO20: COL0-COL20\\nGPIO21-GPIO26: ROW0-ROW5\\n"
            "GPIO27: BL_PWM (backlight, PWM)\\nGPIO28: CAPS_LED\\nGPIO29: NUM_LED\\n"
            "No Scroll Lock indicator - its pin drives the backlight", 279.4, 106.68)

    # --- crystal
    text(M, "Crystal 12 MHz", 116.84, 162.56, 2)
    Y1 = symbol(M, "Device", "Crystal_GND24", "Y1", 134.62, 172.72, value="12MHz",
                footprint="Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")
    connect(M, Y1, {"1": "XIN", "3": "XOUT_R", "2": "GND", "4": "GND"})
    two_pin(M, "Device", "C_Small", "C204", "15p", C0603, 119.38, 187.96, "XIN", "GND")
    two_pin(M, "Device", "C_Small", "C205", "15p", C0603, 149.86, 187.96, "XOUT_R", "GND")
    two_pin(M, "Device", "R_Small", "R206", "1k", R0603, 162.56, 172.72, "XOUT", "XOUT_R")

    # --- flash, BOOTSEL, RESET, SWD
    text(M, "QSPI flash", 116.84, 218.44, 2)
    U2 = symbol(M, "Memory_Flash", "W25Q16JVSS", "U2", 144.78, 238.76, value="W25Q16JVSS",
                footprint="Package_SO:SOIC-8_5.3x5.3mm_P1.27mm")
    connect(M, U2, {"1": "QSPI_SS", "6": "QSPI_SCLK", "5": "QSPI_SD0", "2": "QSPI_SD1", "3": "QSPI_SD2",
                    "7": "QSPI_SD3", "8": "+3V3", "4": "GND"})
    two_pin(M, "Device", "C_Small", "C206", "100n", C0603, 160.02, 238.76, "+3V3", "GND")

    text(M, "Reset, BOOTSEL, SWD", 22.86, 203.2, 2)
    for i, (ref, net) in enumerate((("TP1", "SWCLK"), ("TP2", "SWDIO"), ("TP3", "RUN"), ("TP4", "GND"))):
        tp = symbol(M, "Connector", "TestPoint", ref, 27.94 + i * 10.16, 215.9, value=net,
                    footprint="TestPoint:TestPoint_Pad_D1.0mm", in_bom=False)
        connect(M, tp, {"1": net})

    def button(x, sw_ref, r_ref, r_val, r_top, net):
        r = symbol(M, "Device", "R_Small", r_ref, x, 236.22, 0, value=r_val, footprint=R0603,
                   fpos={"Reference": (2.032, -0.635, "left"), "Value": (2.032, 1.905, "left")})
        connect(M, r, {"1": r_top})
        sw = symbol(M, "Switch", "SW_Push", sw_ref, x, 254.0, 90, value="SW_Push", hide_value=True,
                    footprint="Button_Switch_SMD:SW_SPST_TL3342", fpos={"Reference": (6.35, 0, None)})
        a, b = r.pin("2")[0], sw.pin("2")[0]
        mid = (a[0], round((a[1] + b[1]) / 2, 4))
        wire(M, a, mid)
        wire(M, mid, b)
        label(M, net, mid, 0)
        connect(M, sw, {"1": "GND"})
        EXPECT.update({(r_ref, "2"): net, (sw_ref, "2"): net})

    button(81.28, "SW201", "R208", "10k", "+3V3", "RUN")
    text(M, "SW201 RESET", 68.58, 264.16)
    button(101.6, "SW202", "R207", "1k", "QSPI_SS", "BOOT_SW")
    text(M, "SW202 BOOTSEL", 96.52, 264.16)

# ------------------------------------------------------------ write
open(f"{PRJ}/{NAME}.kicad_sch", "w").write(dumps(root) + "\n")
for fn in ("backlight.kicad_sch", "mcu.kicad_sch"):
    path = f"{PRJ}/{fn}"
    if fn in sheets:
        open(path, "w").write(dumps(sheets[fn]) + "\n")
    elif os.path.exists(path):
        os.remove(path)
os.makedirs(OUT, exist_ok=True)
json.dump({f"{r}|{p}": n for (r, p), n in EXPECT.items()}, open(f"{OUT}/expect.json", "w"), indent=0)
print(f"stage {STAGE}: {len(EXPECT)} expected pin connections, sheets: {['root'] + list(sheets)}")
