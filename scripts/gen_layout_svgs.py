#!/usr/bin/env python3
"""Generate per-layer SVG diagrams from mf.keymap + keyrayout.md."""
import re
import os
import json

ROOT = "/Users/jewel/orca/workspaces/zmk-MoooseFree/mappings3"
KEYRAYOUT = os.path.join(ROOT, "keyrayout.md")
KEYMAP = os.path.join(ROOT, "mf.keymap")
OUT_DIR = os.path.join(ROOT, "images")
os.makedirs(OUT_DIR, exist_ok=True)

UNIT = 60  # px per 1u
PAD = 20

def parse_positions(path):
    """Parse keyrayout.md into a list of dicts with x,y,w,h,r in order."""
    positions = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Lines look like: { "col": 6,"row": 0, "x": 0, "y": 1.3 },
            # Convert JS-ish object to JSON: strip trailing comma
            s = line.rstrip(",").strip()
            try:
                # Already JSON-like
                obj = json.loads(s)
            except Exception:
                continue
            positions.append({
                "x": float(obj.get("x", 0)),
                "y": float(obj.get("y", 0)),
                "w": float(obj.get("w", 1)),
                "h": float(obj.get("h", 1)),
                "r": float(obj.get("r", 0)),
            })
    return positions

# Parse layers (default_layer, ARROW, NUM, AHK, FUNCTION) from mf.keymap
def parse_layers(path):
    with open(path) as f:
        text = f.read()
    # Match `keymap { ... }` block first
    keymap_m = re.search(r"keymap\s*\{[\s\S]*", text)
    if not keymap_m:
        raise SystemExit("keymap block not found")
    block = keymap_m.group(0)
    layer_re = re.compile(r"(\w+)\s*\{\s*bindings\s*=\s*<([\s\S]*?)>\s*;", re.M)
    layers = []
    for m in layer_re.finditer(block):
        name = m.group(1)
        inner = m.group(2)
        bindings = tokenize_bindings(inner)
        layers.append((name, bindings))
    return layers

def tokenize_bindings(inner):
    """Split bindings on whitespace but treat each &word ... starting `&` as a new binding."""
    # Normalize whitespace
    parts = inner.split()
    bindings = []
    cur = []
    paren_depth = 0
    for tok in parts:
        if tok.startswith("&") and paren_depth == 0:
            if cur:
                bindings.append(" ".join(cur))
            cur = [tok]
        else:
            cur.append(tok)
        # Track parens to be safe with LC(LS(...))
        paren_depth += tok.count("(") - tok.count(")")
    if cur:
        bindings.append(" ".join(cur))
    return bindings

# Map binding -> short label
def label_for(binding):
    b = binding.strip()
    if b == "&none":
        return ""
    if b == "&trans":
        return "▽"
    if b == "&bootloader":
        return "BOOT"
    m = re.match(r"&bt\s+BT_SEL\s+(\d+)", b)
    if m:
        return f"BT{m.group(1)}"
    if b == "&bt BT_CLR":
        return "BT CLR"
    if b == "&bt BT_CLR_ALL":
        return "BT CLR\nALL"
    m = re.match(r"&mkp\s+(\w+)", b)
    if m:
        return f"M:{m.group(1)}"
    m = re.match(r"&lt_to_layer_0\s+(\d+)\s+(\w+)", b)
    if m:
        return f"L{m.group(1)}/T0\n{m.group(2)}"
    m = re.match(r"&lt\s+(\d+)\s+(\w+)", b)
    if m:
        return f"L{m.group(1)}\n{m.group(2)}"
    m = re.match(r"&mo\s+(\d+)", b)
    if m:
        return f"MO{m.group(1)}"
    m = re.match(r"&to\s+(\d+)", b)
    if m:
        return f"TO{m.group(1)}"
    m = re.match(r"&kp\s+(.+)", b)
    if m:
        return short_keycode(m.group(1))
    # macro / unknown: strip leading &
    return b.lstrip("&")

def short_keycode(kc):
    """Shorten modifier-wrapped keycodes for display."""
    kc = kc.strip()
    # LC(LS(LA(LG(X)))) → Hyper X
    m = re.fullmatch(r"LC\(LS\(LA\(LG\((\w+)\)\)\)\)", kc)
    if m:
        return f"Hyp\n{base_kc(m.group(1))}"
    # LC(LS(LA(X))) → Meh X
    m = re.fullmatch(r"LC\(LS\(LA\((\w+)\)\)\)", kc)
    if m:
        return f"Meh\n{base_kc(m.group(1))}"
    # Single modifier wraps
    mods = []
    rest = kc
    while True:
        m = re.fullmatch(r"(LS|LC|LA|LG|RS|RC|RA|RG)\((.+)\)", rest)
        if not m:
            break
        mods.append(m.group(1))
        rest = m.group(2)
    if mods:
        return "+".join(mods) + "\n" + base_kc(rest)
    return base_kc(rest)

def base_kc(kc):
    """Shorten common base keycodes for display."""
    table = {
        "LSHIFT": "LShift", "RSHIFT": "RShift",
        "LCTRL": "LCtrl", "RCTRL": "RCtrl",
        "LALT": "LAlt", "RALT": "RAlt",
        "LWIN": "LWin", "RWIN": "RWin", "LGUI": "LGui",
        "BSPC": "BSpc", "SPACE": "Space", "ENTER": "Enter",
        "RIGHT": "→", "LEFT": "←", "UP": "↑", "DOWN": "↓",
        "TAB": "Tab", "ESC": "Esc", "DEL": "Del", "PSCRN": "PrtSc",
        "TILDE": "~", "GRAVE": "`", "MINUS": "-", "EQUAL": "=",
        "SLASH": "/", "BSLH": "\\", "COMMA": ",", "DOT": ".",
        "SEMI": ";", "SQT": "'", "LBKT": "[", "RBKT": "]",
        "LBRC": "{", "RBRC": "}", "PLUS": "+", "ASTRK": "*",
        "CARET": "^", "K_APP": "App",
        "C_MUTE": "Mute", "C_VOL_UP": "Vol+", "C_VOL_DN": "Vol-",
        "KP_SLASH": "KP/", "KP_DOT": "KP.",
        "JP_YEN": "¥", "JP_COLON": ":", "JP_SEMI": ";",
        "JP_COMMA": ",", "JP_DOT": ".", "JP_SLASH": "/",
        "JP_LBKT": "[", "JP_RBKT": "]", "JP_AT": "@",
        "JP_MHEN": "無変換", "JP_HENK": "変換",
        "JP_EISU": "英数", "JP_MINUS": "-",
        "JP_UNDER": "_", "JP_LT": "<", "JP_RT": ">",
        "LANG1": "かな", "LANG2": "英数",
        "SCRL_UP": "Scr↑", "SCRL_DOWN": "Scr↓",
    }
    if kc.startswith("N") and kc[1:].isdigit():
        return kc[1:]
    if kc.startswith("F") and kc[1:].isdigit():
        return kc
    if len(kc) == 1:
        return kc
    return table.get(kc, kc)

def render_svg(layer_name, bindings, positions):
    # Compute extents
    min_x = min(p["x"] for p in positions)
    min_y = min(p["y"] for p in positions)
    max_x = max(p["x"] + p["w"] for p in positions)
    max_y = max(p["y"] + p["h"] for p in positions)
    width = (max_x - min_x) * UNIT + 2 * PAD
    height = (max_y - min_y) * UNIT + 2 * PAD

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}" font-family="sans-serif">')
    svg.append('<style>'
               '.key{fill:#3a3a48;stroke:#5a5a68;stroke-width:1}'
               '.kt{fill:#e8e8ec;font-size:10px;text-anchor:middle}'
               '.ks{fill:#8a8a95;font-size:9px;text-anchor:middle}'
               '.bg{fill:#1a1a1f}'
               '</style>')
    svg.append(f'<rect class="bg" width="{width:.0f}" height="{height:.0f}"/>')

    for i, pos in enumerate(positions):
        if i >= len(bindings):
            break
        binding = bindings[i]
        label = label_for(binding)
        kw = pos["w"] * UNIT
        kh = pos["h"] * UNIT
        kx = (pos["x"] - min_x) * UNIT + PAD
        ky = (pos["y"] - min_y) * UNIT + PAD
        r = pos["r"]
        # Rotation around the key's own top-left center
        cx = kx + kw / 2
        cy = ky + kh / 2
        transform = f' transform="rotate({r:.0f} {cx:.1f} {cy:.1f})"' if r else ""
        # Faded if &none
        fill = "#2a2a30" if label == "" else "#3a3a48"
        svg.append(f'<g{transform}>')
        svg.append(f'<rect class="key" x="{kx:.1f}" y="{ky:.1f}" width="{kw:.1f}" height="{kh:.1f}" rx="4" fill="{fill}"/>')
        # Position number (tiny)
        svg.append(f'<text class="ks" x="{kx + 5:.1f}" y="{ky + 9:.1f}" text-anchor="start">{i}</text>')
        # Label (possibly multi-line)
        lines = label.split("\n")
        n = len(lines)
        for li, ln in enumerate(lines):
            ty = cy + (li - (n - 1) / 2) * 11 + 3
            svg.append(f'<text class="kt" x="{cx:.1f}" y="{ty:.1f}">{escape_xml(ln)}</text>')
        svg.append('</g>')
    svg.append('</svg>')
    return "\n".join(svg)

def escape_xml(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def main():
    positions = parse_positions(KEYRAYOUT)
    layers = parse_layers(KEYMAP)
    print(f"positions: {len(positions)}")
    for name, bs in layers:
        print(f"layer {name}: {len(bs)} bindings")
    for i, (name, bindings) in enumerate(layers):
        svg = render_svg(name, bindings, positions)
        path = os.path.join(OUT_DIR, f"layer{i}_{name}.svg")
        with open(path, "w") as f:
            f.write(svg)
        print(f"wrote {path}")

if __name__ == "__main__":
    main()
