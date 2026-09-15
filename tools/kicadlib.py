"""Minimal KiCad S-expression parser/serializer plus symbol-library helpers."""
import re, math, subprocess, uuid as _uuid
from copy import deepcopy


class Sym(str):
    """Bare (unquoted) atom. Plain str = quoted string (raw, escapes untouched)."""
    __slots__ = ()


_TOK = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))', re.S)


def parse(text):
    stack = [[]]
    pos = 0
    while True:
        m = _TOK.match(text, pos)
        if not m:
            if text[pos:].strip():
                raise ValueError(f"parse error at {pos}: {text[pos:pos+60]!r}")
            break
        pos = m.end()
        if m.group(1):
            stack.append([])
        elif m.group(2):
            lst = stack.pop()
            stack[-1].append(lst)
        elif m.group(3) is not None:
            stack[-1].append(m.group(3))
        else:
            stack[-1].append(Sym(m.group(4)))
    assert len(stack) == 1, "unbalanced parentheses"
    return stack[0][0]


def num(v):
    if isinstance(v, (int, float)):
        s = f"{v:.4f}".rstrip("0").rstrip(".")
        return Sym("0" if s in ("-0", "") else s)
    return v


def dumps(node, indent=0):
    if isinstance(node, Sym):
        return str(node)
    if isinstance(node, str):
        return '"' + node + '"'
    if isinstance(node, (int, float)):
        return str(num(node))
    parts = [dumps(x, indent + 1) for x in node]
    if not any(isinstance(x, list) for x in node):
        return "(" + " ".join(parts) + ")"
    head = []
    i = 0
    while i < len(node) and not isinstance(node[i], list):
        head.append(parts[i])
        i += 1
    s = "(" + " ".join(head)
    for p in parts[i:]:
        s += "\n" + "\t" * (indent + 1) + p
    return s + "\n" + "\t" * indent + ")"


def S(*items):
    """Build a list node: first item becomes a Sym, numbers become Syms."""
    out = [Sym(items[0])]
    for it in items[1:]:
        out.append(num(it) if isinstance(it, (int, float)) else it)
    return out


def find(node, key):
    for x in node:
        if isinstance(x, list) and x and x[0] == key:
            return x
    return None


def findall(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def uid():
    return str(_uuid.uuid4())


# kbplacer matrix + switch footprints, schematic upgraded to KiCad 10: starting point of the generator
BASE_COMMIT = "95ce8fa"


def git_base(prj, path):
    """Content of a project file as of BASE_COMMIT."""
    return subprocess.run(["git", "-C", prj, "show", f"{BASE_COMMIT}:{path}"],
                          capture_output=True, text=True, check=True).stdout


# ---------------------------------------------------------------- symbol libs
SYMDIR = "/usr/share/kicad/symbols/"
_libcache = {}


def _lib(libname, path=None):
    key = path or libname
    if key not in _libcache:
        tree = parse(open(path or SYMDIR + libname + ".kicad_sym").read())
        _libcache[key] = {s[1]: s for s in findall(tree, "symbol")}
    return _libcache[key]


def lib_symbol(libname, symname, path=None):
    """Flattened symbol (extends resolved), named 'lib:sym' for lib_symbols."""
    syms = _lib(libname, path)
    s = deepcopy(syms[symname])
    ext = find(s, "extends")
    if ext:
        parent = lib_symbol(libname, ext[1], path)
        pname = ext[1]
        overrides = {}
        for item in s[2:]:
            if isinstance(item, list) and item[0] != "extends":
                k = (item[0], item[1]) if item[0] == "property" else (item[0],)
                overrides[k] = item
        new = [Sym("symbol"), symname]
        for item in parent[2:]:
            if isinstance(item, list):
                k = (item[0], item[1]) if item[0] == "property" else (item[0],)
                if item[0] == "symbol":
                    item = deepcopy(item)
                    item[1] = symname + item[1][len(pname):]
                    new.append(item)
                    continue
                if k in overrides:
                    new.append(overrides.pop(k))
                    continue
            new.append(item)
        new.extend(overrides.values())
        s = new
    s[1] = f"{libname}:{symname}"
    return s


def pins(symbol):
    """[{unit, num, name, type, x, y, a}] from a (flattened) symbol; lib coordinates."""
    out = []
    base = symbol[1].split(":")[-1]
    for sub in findall(symbol, "symbol"):
        m = re.match(re.escape(base) + r"_(\d+)_(\d+)$", sub[1])
        unit = int(m.group(1)) if m else 0
        for p in findall(sub, "pin"):
            at = find(p, "at")
            out.append(dict(unit=unit, num=find(p, "number")[1], name=find(p, "name")[1],
                            type=str(p[1]), x=float(at[1]), y=float(at[2]), a=float(at[3])))
    return out


def to_screen(sx, sy, rot, px, py):
    """Lib point (px,py) of a symbol at (sx,sy) rotated rot° -> schematic point."""
    vx, vy = px, -py
    t = math.radians(rot)
    c, s_ = round(math.cos(t)), round(math.sin(t))
    return (round(sx + vx * c + vy * s_, 4), round(sy - vx * s_ + vy * c, 4))


def pin_dir(rot, a):
    """Unit vector (schematic) pointing from the pin end AWAY from the body."""
    t = math.radians(a)
    vx, vy = math.cos(t), -math.sin(t)
    r = math.radians(rot)
    c, s_ = math.cos(r), math.sin(r)
    dx, dy = vx * c + vy * s_, -vx * s_ + vy * c
    return (-round(dx), -round(dy))
