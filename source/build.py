"""Build the Agar theme for T3 Code: agar.json (+ svg previews)."""
import json, math, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
T = 30  # site SVG growth time, seconds
MONO = "ui-monospace,Menlo,monospace"
SERIF = '"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif'
TEAL = "#17695c"
INK = "#2a2316"


def f(x):
    s = f"{x:.1f}"
    return s[:-2] if s.endswith(".0") else s


def pct(x):
    return f"{x:.1f}".rstrip("0").rstrip(".") + "%"


COLS = {  # colony colours: (centre, edge)
    "cr": ("#fffaf0", "#e9dcb4"),   # cream
    "ye": ("#f7e27a", "#d9ae1c"),   # yellow
    "co": ("#ee6f7b", "#b32d46"),   # serratia red
    "vi": ("#a56fd1", "#5f2f8c"),   # violet
    "gr": ("#7fd8bf", "#1f8a74"),   # blue green
}


def defs(agar):
    g = "".join(f"<radialGradient id='{k}' cx='.38' cy='.34' r='.75'><stop offset='0' stop-color='{a}'/><stop offset='1' stop-color='{b}'/></radialGradient>" for k, (a, b) in COLS.items())
    return (f"<defs>{g}<radialGradient id='ag' cx='.45' cy='.4' r='.7'><stop offset='0' stop-color='{agar[0]}'/><stop offset='.8' stop-color='{agar[1]}'/><stop offset='1' stop-color='{agar[2]}'/></radialGradient>"
            "<linearGradient id='gl' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='%23ffffff' stop-opacity='.85'/><stop offset='1' stop-color='%23ffffff' stop-opacity='0'/></linearGradient></defs>")


def plate_base(agar, rim="#9bb5b1"):
    cx, cy = 180, 180
    return (
        f"<circle cx='188' cy='192' r='162' fill='#6b5420' fill-opacity='.14'/>"
        f"<circle cx='{cx}' cy='{cy}' r='162' fill='#ffffff' fill-opacity='.5' stroke='{rim}' stroke-width='2.5'/>"
        f"<circle cx='{cx}' cy='{cy}' r='153' fill='none' stroke='{rim}' stroke-width='1' stroke-opacity='.8'/>"
        f"<circle cx='{cx}' cy='{cy}' r='146' fill='url(#ag)'/>"
        f"<circle cx='{cx}' cy='{cy}' r='146' fill='none' stroke='#ffffff' stroke-opacity='.35' stroke-width='3'/>"
        f"<circle cx='{cx}' cy='{cy}' r='139' fill='none' stroke='#5b3d0a' stroke-opacity='.12' stroke-width='1.2'/>"
        "<path d='M62 118A126 126 0 0 1 150 62' fill='none' stroke='url(#gl)' stroke-width='9' stroke-linecap='round'/>"
        "<path d='M290 262A126 126 0 0 1 238 296' fill='none' stroke='#ffffff' stroke-opacity='.4' stroke-width='4' stroke-linecap='round'/>")


def label(txt1, txt2):
    return (f"<g transform='translate(52 362)'><path d='M0 0h256a6 6 0 0 1 6 6v34a6 6 0 0 1-6 6H0a6 6 0 0 1-6-6V6a6 6 0 0 1 6-6z' fill='#fffdf3' stroke='#cdb978' stroke-width='1.5' transform='translate(0 0)'/>"
            f"<rect x='-6' y='10' width='6' height='26' fill='#b8d5cf' fill-opacity='.8'/>"
            f"<text x='14' y='20' class='l'>{txt1}</text><text x='14' y='37' class='l s'>{txt2}</text></g>")


def label_css():
    return (f".l{{font:600 14px {MONO};letter-spacing:.12em;fill:#4a3c17}}.l.s{{font-weight:400;font-size:12px;fill:#7a6a3f;letter-spacing:.08em}}")


def spaced(rng, n, rmax, minsep, sizes):
    pts = []
    tries = 0
    while len(pts) < n and tries < 5000:
        tries += 1
        a, r = rng.uniform(0, 2 * math.pi), rmax * math.sqrt(rng.uniform(0, 1))
        s = rng.choice(sizes)
        x, y = 180 + r * math.cos(a), 180 + r * math.sin(a)
        if all(math.hypot(x - px, y - py) > s + ps + minsep for px, py, ps, _ in pts):
            pts.append((x, y, s, None))
    return pts


def colony(i, x, y, r, col, halo=None):
    h = f"<circle r='{f(r*1.9)}' fill='#fff3c4' fill-opacity='.38'/>" if halo else ""
    return (f"<g transform='translate({f(x)} {f(y)})'><g class='c c{i}'>{h}<circle r='{f(r)}' fill='url(#{col})'/>"
            f"<circle r='{f(r)}' fill='none' stroke='#3b2a05' stroke-opacity='.28' stroke-width='.8'/>"
            f"<circle cx='{f(-r*.3)}' cy='{f(-r*.35)}' r='{f(max(r*.22,1))}' fill='#ffffff' fill-opacity='.7'/></g></g>")



def grow_css(n, start, end, span):
    """Per-colony keyframes for the landing-page SVGs: scale 0 -> 1 once, then hold."""
    out = []
    for i in range(n):
        a = start + (end - start) * i / max(n - 1, 1)
        b = a + span
        out.append(f".c{i}{{animation-name:k{i}}}@keyframes k{i}{{0%,{pct(a)}{{transform:scale(0)}}{pct(b)},to{{transform:scale(1)}}}}")
    return "".join(out)


def anim_css(n, start, end, span, static, delay=0):
    """Site-only SVG animation: grow once (negative delay = already populated at first paint) and hold."""
    base = f".c{{animation-duration:{T}s;animation-delay:-{delay}s;animation-timing-function:cubic-bezier(.2,.8,.25,1);animation-iteration-count:1;animation-fill-mode:both}}"
    return "" if static else base + grow_css(n, start, end, span)


# --- plate geometry shared by the SVG base art and the CSS colony layers (viewBox 360x420)
def plate_a_pts():
    rng = random.Random(7)
    cols = ["cr", "ye", "co", "vi", "gr", "cr", "co", "ye", "gr", "vi", "cr", "co", "gr", "ye", "cr", "vi", "co", "gr"]
    pts = spaced(rng, 18, 118, 6, [8, 10, 12, 14, 17, 6, 7])
    pts.sort(key=lambda p: math.hypot(p[0] - 180, p[1] - 180) * .5 + rng.uniform(0, 70))
    main = [(x, y, r, cols[i % len(cols)], i % 4 == 0) for i, (x, y, r, _) in enumerate(pts)]
    # late satellites: appear well into a long turn, so the plate never looks finished-and-frozen
    rng2 = random.Random(21)
    sat = []
    tries = 0
    while len(sat) < 5 and tries < 4000:
        tries += 1
        a, rr = rng2.uniform(0, 2 * math.pi), 128 * math.sqrt(rng2.uniform(0, 1))
        x, y, r = 180 + rr * math.cos(a), 180 + rr * math.sin(a), rng2.choice([4, 5, 6])
        if all(math.hypot(x - p[0], y - p[1]) > r + p[2] + 5 for p in main + sat):
            sat.append((x, y, r, rng2.choice(["cr", "ye", "gr"]), False))
    return main, sat


def plate_b_pts():
    rng = random.Random(11)
    lines = [
        [(70, 130), (100, 100), (135, 88), (180, 84), (225, 88), (260, 100), (290, 130)],
        [(80, 200), (110, 188), (140, 205), (170, 192), (200, 208)],
        [(230, 215), (255, 235), (232, 255), (255, 275)],
        [(120, 250), (140, 280), (170, 262), (180, 296)],
    ]
    counts = [10, 7, 5, 3]
    sizes = [(4, 6), (4.5, 7), (5, 8), (6, 9)]
    pts = []
    for ln, n, (s0, s1) in zip(lines, counts, sizes):
        for k in range(n):
            t = (k + .5) / n * (len(ln) - 1)
            i = min(int(t), len(ln) - 2)
            u = t - i
            x = ln[i][0] + (ln[i + 1][0] - ln[i][0]) * u + rng.uniform(-3, 3)
            y = ln[i][1] + (ln[i + 1][1] - ln[i][1]) * u + rng.uniform(-3, 3)
            pts.append((x, y, rng.uniform(s0, s1), "cr", k % 3 == 0))
    sat = [(150, 306, 4, "cr", False), (200, 300, 3.5, "cr", False), (262, 292, 3.5, "cr", False)]
    return lines, pts[:-0 or None], sat


AGAR_A = ("#f6df9c", "#e5b95a", "#cf9a3a")
AGAR_B = ("#e0866e", "#c4604a", "#a94837")


def label_dock(t1, t2):
    return (f"<g transform='translate(40 352)'><path d='M0 0h280a6 6 0 0 1 6 6v50a6 6 0 0 1-6 6H0a6 6 0 0 1-6-6V6a6 6 0 0 1 6-6z' fill='#fffdf3' stroke='#cdb978' stroke-width='2'/>"
            f"<rect x='-8' y='12' width='8' height='38' fill='#b8d5cf'/>"
            f"<text x='16' y='28' style='font:700 30px {MONO};letter-spacing:.08em;fill:#3a2f15'>{t1}</text>"
            f"<text x='16' y='52' style='font:500 20px {MONO};letter-spacing:.05em;fill:#6a5a30'>{t2}</text></g>")


def plate_art(agar, labeltxt, streak="", dock=False):
    """Plate with its label but no colonies (colonies are CSS gradient layers, see colony_layers)."""
    lab = "" if dock else label(*labeltxt[0])
    style = "" if dock else f"<style>{label_css()}</style>"
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 360 420'>{style}" + defs(agar) + plate_base(agar) + streak + lab + "</svg>")


def streak_svg_paths(lines):
    return "".join("<path d='M" + "L".join(f"{x} {y}" for x, y in ln) + "' fill='none' stroke='#fff0d6' stroke-opacity='.4' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/>" for ln in lines)


LAB_A = (("PLATE 07 · NUTRIENT", "37°C · 24 h · AEROBIC"), ("PLATE 07", "NUTRIENT · 37°C"))
LAB_B = (("PLATE 08 · BLOOD", "STREAK · 4 SECTORS · 48 h"), ("PLATE 08", "BLOOD · STREAK"))
HI = {k: v for k, v in COLS.items()}


def colony_layers(prefix, main, sat):
    """CSS radial-gradient layers, one per colony (+ halos), radius driven by registered numbers --<prefix>N (0..1)."""
    cols, halos = [], []
    for i, (x, y, r, col, halo) in enumerate(main + sat):
        v = f"var(--{prefix}{i+1})"
        rx, ry = r / 360 * 100, r / 420 * 100
        px, py = x / 360 * 100, y / 420 * 100
        a, b = HI[col]
        cols.append(f"radial-gradient(ellipse calc({v}*{rx:.2f}% + .002%) calc({v}*{ry:.2f}% + .002%) at {px:.2f}% {py:.2f}%,{a} 0,{a} 14%,{b} 82%,rgba(59,42,5,.4) 93%,rgba(59,42,5,0) 100%)")
        if halo:
            halos.append(f"radial-gradient(ellipse calc({v}*{rx*1.9:.2f}% + .002%) calc({v}*{ry*1.9:.2f}% + .002%) at {px:.2f}% {py:.2f}%,rgba(255,243,196,.38) 0,rgba(255,243,196,.38) 95%,rgba(255,243,196,0) 100%)")
    return cols + halos


def grow_keyframes(name, prefix, n_main, n_sat):
    """One-shot, 60s: colonies re-inoculate (shrink in ~1s), grow in a stagger over ~30s, late satellites appear
    between 33s and 51s, then everything holds. Values between stops hold, so a long turn never resets."""
    stops = {}

    def put(p, i, v):
        stops.setdefault(round(p, 2), {})[i] = v
    n = n_main + n_sat
    for i in range(n):
        put(1.2, i, 0)
        if i < n_main:
            a = 3 + 31 * i / max(n_main - 1, 1)
            b = a + 9
        else:
            j = i - n_main
            a = 55 + 30 * j / max(n_sat - 1, 1)
            b = a + 8
        put(a, i, 0)
        put(b, i, 1)
    rows = "".join(f"{pct(p)}{{" + ";".join(f"--{prefix}{i+1}:{v}" for i, v in sorted(d.items())) + "}" for p, d in sorted(stops.items()))
    return f"@keyframes {name}{{{rows}}}", n


def ruler_svg():
    ticks = "".join(f"<path d='M{10+i*10} 0v{14 if i%5==0 else 8}' />" for i in range(0, 25))
    nums = "".join(f"<text x='{10+i*10}' y='28' text-anchor='middle'>{i//5}</text>" for i in range(0, 25, 5))
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 260 36'><style>path{{stroke:#6a5a30;stroke-width:1;fill:none}}text{{font:10px {MONO};fill:#6a5a30;letter-spacing:.06em}}</style>"
            f"<rect x='0' y='0' width='260' height='34' rx='3' fill='#f3e3b0' fill-opacity='.7' stroke='#cdb978'/>{ticks}{nums}<text x='256' y='28' text-anchor='end'>cm</text></svg>")


def entry_svg():
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 260 92'><style>path{{fill:none;stroke:#c7b57a;stroke-width:1}}"
            f"text{{font:9.5px {MONO};fill:#7a6a3f;letter-spacing:.12em}}.b{{font:600 13px {MONO};fill:#3a2f15;letter-spacing:.04em}}.t{{fill:{TEAL}}}</style>"
            "<rect x='.5' y='.5' width='259' height='91' rx='4' fill='#fffdf3' fill-opacity='.85' stroke='#c7b57a'/>"
            "<path d='M.5 33.5h259M130.5 33.5v58'/>"
            "<text x='10' y='12'>NOTEBOOK ENTRY</text><text class='b' x='10' y='27'>EXP. T3-0042</text>"
            "<text x='10' y='47'>INOCULATED BY</text><text class='b' x='10' y='62'>AGENT</text>"
            "<text x='140' y='47'>READ BY</text><text class='b' x='140' y='62'>YOU</text>"
            "<text x='10' y='81'>GROWTH</text><rect x='62' y='72' width='11' height='11' rx='2' fill='none' stroke='#6a5a30'/>"
            "<text x='140' y='81'>WITNESSED</text><path d='M210 84c6-9 9 7 14-2s9 3 15-3' style='stroke:#3a2f15'/></svg>")


def zig_svg():
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='28' height='8' viewBox='0 0 28 8'><path d='M0 6 7 2 14 6 21 2 28 6' fill='none' stroke='{TEAL}' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round' stroke-opacity='.5'/></svg>"


def data_uri(svg):
    svg = svg.replace("%23", "\0")
    out = svg.replace("%", "%25").replace("#", "%23").replace('"', "'").replace("<", "%3C").replace("\0", "%23")
    return "url(\"data:image/svg+xml," + out + "\")"


# ---------------------------------------------------------------- colours
colors = {
    "canvas": "#f8f4e6", "chrome": "#efe9d6", "toolbar": "#f3eedd", "toolbarForeground": "#2a2316",
    "toolbarBorder": "#d9cfae", "toolbarControl": "#e8e0c6", "toolbarControlForeground": "#2a2316",
    "toolbarControlHover": "#ddd3b0", "surface": "#fffdf5", "surfaceRaised": "#ffffff", "surfaceOverlay": "#fffcf0",
    "text": "#2a2316", "textMuted": "#62553a", "border": "#d8cca6", "input": "#c9bb8f", "focus": "#17695c",
    "accent": "#17695c", "accentForeground": "#f8f4e6", "secondary": "#ebe3c8", "secondaryForeground": "#2a2316",
    "muted": "#efe8d2", "mutedForeground": "#6a5c3d", "placeholder": "#75663f", "secondaryLabel": "#6a5c3d",
    "iconMuted": "#7a6a45", "error": "#b3263a", "errorForeground": "#8c1d2e", "errorSurface": "#f8dcd8",
    "warning": "#a65f00", "warningForeground": "#7a4400", "warningSurface": "#f8e6bd",
    "update": "#2a6f8f", "updateForeground": "#1a4d66", "updateSurface": "#d9ecef",
    "accentSurface": "#d6ebe4", "accentSurfaceForeground": "#0f4a40", "messageSurface": "#dcebe3",
    "messageForeground": "#1f2a24", "messageAction": "#17695c", "messageActionForeground": "#f8f4e6",
    "messageActionHover": "#0f574b", "codeBackground": "#efe9d2", "codeForeground": "#2a2316",
    "searchMatchBackground": "#f3d77a", "searchMatchForeground": "#2a2316",
    "searchMatchActiveBackground": "#17695c", "searchMatchActiveForeground": "#ffffff",
    "sidebar": "#efd9a0", "sidebarForeground": "#2e2310", "sidebarMutedForeground": "#5b4719",
    "sidebarControlSurface": "#f6e6b8", "sidebarRowHover": "#e8cf8c", "sidebarRowActive": "#e2c57a",
    "sidebarRowSelected": "#f8ecc6", "sidebarBorder": "#cfb06a", "terminalBackground": "#f4efdd",
    "terminalForeground": "#2a2316", "terminalCursor": "#17695c", "terminalSelection": "#cfe3d6",
    "terminalScrollbar": "#d3c79f", "terminalScrollbarHover": "#b5a678",
}

CW = "var(--chat-content-max-width,46rem)"
G = f"(100% - {CW})/2"
PAPER = "248,244,230"
SB = "239,217,160"  # sidebar colour as rgb

BUSY = ('body:has([data-timeline-row-kind="working"])', 'body:has([data-thread-item] [aria-busy="true"][aria-current]:not([aria-current="false"]))')


def busy(sel):
    return ",".join(f"{b} {sel}" for b in BUSY)


LINE = "rgba(31,120,108,"
GRID = (f"linear-gradient({LINE}.13) 1px,transparent 1px) 0 0/120px 120px,linear-gradient(90deg,{LINE}.13) 1px,transparent 1px) 0 0/120px 120px,"
        f"linear-gradient({LINE}.1) 1px,transparent 1px) 0 0/24px 24px,linear-gradient(90deg,{LINE}.1) 1px,transparent 1px) 0 0/24px 24px")
SMALLGRID = f"linear-gradient({LINE}.09) 1px,transparent 1px) 0 0/24px 24px,linear-gradient(90deg,{LINE}.09) 1px,transparent 1px) 0 0/24px 24px"


def dots(n_list, color, cy="calc(100% - 5px)"):
    """Colony dots along the bottom edge, sized by registered numbers --g1..--gN."""
    return ",".join(f"radial-gradient(circle calc(max(var(--g{i+1})*{r}px,2px)) at {x}px {cy},#e4f6ee 0,#2a9b83 45%,#0f574b 88%,transparent 100%)" for i, (x, r) in enumerate(n_list))


ROW_DOTS = [(16, 4), (33, 3.2), (50, 4.2), (68, 3.4)]
WORK_DOTS = [(5, 4), (24, 3.2), (42, 4.2), (62, 3.4), (82, 4), (104, 3.2)]
rowd = dots(ROW_DOTS, "#1f8a74")
workd = dots(WORK_DOTS, "#1f8a74")
hoverd = ("radial-gradient(circle at calc(100% - 18px) calc(100% - 6px),#f4cfc2 0,#c8404f calc(var(--h)*3.5px*.55),#8c1d2e calc(var(--h)*3.5px - .01px),transparent calc(var(--h)*3.5px)),"
          "radial-gradient(circle at calc(100% - 18px) calc(100% - 6px),transparent calc(var(--h)*5.2px),rgba(23,105,92,.65) calc(var(--h)*5.2px + .01px),rgba(23,105,92,.65) calc(var(--h)*6.4px),transparent calc(var(--h)*6.4px + .01px))")


def pop_keyframes(name, n):
    pts = sorted({0, 100} | {round(i * (62 / n) + d, 1) for i in range(n) for d in (0, 14)} | {82})
    rows = []
    for p in pts:
        vals = []
        for i in range(n):
            a = i * (62 / n)
            if p <= a: v = 0
            elif p >= a + 14: v = 1
            else: v = round((p - a) / 14, 2)
            if p >= 100: v = 0
            if 82 <= p < 100: v = 1 if p == 82 else v
            vals.append(f"--g{i+1}:{v}")
        rows.append(f"{pct(p)}{{{';'.join(vals)}}}")
    return f"@keyframes {name}{{" + "".join(rows) + "}"


def bubbles_svg(w, h, n, seed, op):
    rng = random.Random(seed)
    c = "".join(f"<circle cx='{rng.randint(8,w-8)}' cy='{rng.randint(8,h-8)}' r='{rng.choice([1.5,2,2.5,3.5,5,7])}' fill='#fff7da' fill-opacity='{op}' stroke='#b58a2c' stroke-opacity='{op*.8:.2f}'/>" for _ in range(n))
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>{c}</svg>"


# ------------------------------------------------------------ plates as CSS (colony gradients on a small box)
mainA, satA = plate_a_pts()
lines, mainB, satB = plate_b_pts()
layersA = colony_layers("a", mainA, satA)
layersB = colony_layers("b", mainB, satB)
nA, nB = len(mainA) + len(satA), len(mainB) + len(satB)
kfA, _ = grow_keyframes("ag-growA", "a", len(mainA), len(satA))
kfB, _ = grow_keyframes("ag-growB", "b", len(mainB), len(satB))
plateA = data_uri(plate_art(AGAR_A, LAB_A))
plateB = data_uri(plate_art(AGAR_B, LAB_B, streak_svg_paths(lines)))
plateA_dock = data_uri(plate_art(AGAR_A, LAB_A, dock=True))
props = ("".join(f"@property --g{i}{{syntax:'<number>';inherits:false;initial-value:0}}" for i in range(1, 7))
         + "@property --k{syntax:'<number>';inherits:false;initial-value:0}@property --h{syntax:'<number>';inherits:false;initial-value:0}"
         + "".join(f"@property --a{i}{{syntax:'<number>';inherits:false;initial-value:1}}" for i in range(1, nA + 1))
         + "".join(f"@property --b{i}{{syntax:'<number>';inherits:false;initial-value:1}}" for i in range(1, nB + 1)))
trA = ",".join(f"--a{i} 1.6s cubic-bezier(.2,.8,.25,1)" for i in range(1, nA + 1))
trB = ",".join(f"--b{i} 1.6s cubic-bezier(.2,.8,.25,1)" for i in range(1, nB + 1))

GW = f"min(300px,clamp(0px,({G} - 216px)*1000,{G} - 40px))"
CONV = '[data-workspace-area="conversation"]'
SBI = '[data-slot="sidebar-inner"]'

DOCK_W, DOCK_H = 96, 112
dock_layers = layersA + [plateA_dock]
dock_scrim = (f"linear-gradient(180deg,transparent calc(100% - {DOCK_H + 56}px),rgba({SB},.88) calc(100% - {DOCK_H + 46}px),rgba({SB},.88) 100%)")
dock_images = ",".join([dock_scrim] + dock_layers)
nd = len(dock_layers)
dock_size = ",".join(["100% 100%"] + [f"{DOCK_W}px {DOCK_H}px"] * nd)
dock_pos = ",".join(["0 0"] + ["right 16px bottom 8px"] * nd)
BUB1 = data_uri(bubbles_svg(240, 410, 26, 3, .2))
BUB2 = data_uri(bubbles_svg(170, 300, 12, 9, .14))
SLAB = "linear-gradient(180deg,#f3dfae,#ebd292)"

css = (
    props
    + ":root{--ag-rule:" + data_uri(ruler_svg()) + ";--ag-entry:" + data_uri(entry_svg()) + ";--ag-zig:" + data_uri(zig_svg())
    + ";--ag-b1:" + BUB1 + ";--ag-b2:" + BUB2 + "}"
    # notebook sheet: grid only (plates live on their own small boxes below)
    + CONV + "{position:relative;background:" + GRID + ",#f8f4e6!important}"
    # the two plates: small pseudo boxes in the gutters; colony radii are registered numbers, one-shot growth while a turn runs
    + f"{CONV}::before,{CONV}::after{{content:\"\";position:absolute;z-index:0;pointer-events:none;width:{GW};aspect-ratio:360/420;contain:layout paint;background-size:100% 100%;background-repeat:no-repeat}}"
    + f"{CONV}::before{{left:14px;top:56px;background-image:{','.join(layersA + [plateA])};transition:{trA}}}"
    + f"{CONV}::after{{right:14px;top:90px;background-image:{','.join(layersB + [plateB])};transition:{trB}}}"
    + kfA + kfB
    + busy(CONV + "::before") + "{animation:ag-growA 60s steps(14,end) 1 forwards}"
    + busy(CONV + "::after") + "{animation:ag-growB 60s steps(14,end) 1 forwards}"
    # reading-column scrim, ruler and notebook-entry label
    + CONV + " .messages-timeline-scroll{background:"
    f"var(--ag-entry) right 14px bottom 14px/min(260px,clamp(0px,({G} - 200px)*1000,{G} - 32px)) auto no-repeat,"
    f"var(--ag-rule) left 14px bottom 18px/min(260px,clamp(0px,({G} - 200px)*1000,{G} - 32px)) auto no-repeat,"
    f"linear-gradient(90deg,transparent calc(50% - {CW}/2 - 96px),rgba({PAPER},.95) calc(50% - {CW}/2 - 18px),rgba({PAPER},.95) calc(50% + {CW}/2 + 18px),transparent calc(50% + {CW}/2 + 96px))!important}}"
    + "@media (max-width:1699px){" + CONV + " .messages-timeline-scroll{background:"
    f"var(--ag-entry) right 14px bottom 14px/min(260px,clamp(0px,({G} - 200px)*1000,{G} - 32px)) auto no-repeat,"
    f"linear-gradient(90deg,transparent calc(50% - {CW}/2 - 96px),rgba({PAPER},.95) calc(50% - {CW}/2 - 18px),rgba({PAPER},.95) calc(50% + {CW}/2 + 18px),transparent calc(50% + {CW}/2 + 96px))!important}}"
    + "}"
    # header: serif title, and a slow inoculation streak along the rail while a turn runs
    f"[data-chat-header]{{font-family:{SERIF};font-size:15px!important;background-color:rgba(243,238,221,.96)!important;background-image:var(--ag-zig)!important;background-repeat:repeat-x!important;background-size:0 8px!important;background-position:0 100%!important;border-bottom:1px solid #d9cfae!important;transition:background-size .5s ease}}"
    + busy("[data-chat-header]") + "{background-size:28px 8px!important;animation:ag-streak 7s steps(28) infinite}"
    "@keyframes ag-streak{to{background-position:28px 100%}}"
    # turn-complete beat: a lab tab on the composer. INCUBATING while busy, then GROWTH CHECKED stamps down (transition, not animation)
    "[data-slot=\"composer-host\"]{position:relative}"
    f"[data-slot=\"composer-host\"]::before,[data-slot=\"composer-host\"]::after{{position:absolute;top:-10px;right:22px;z-index:1;pointer-events:none;padding:3px 9px;border-radius:3px;background:#fffdf3;font:700 10.5px/1.3 {MONO};letter-spacing:.14em;white-space:nowrap}}"
    "[data-slot=\"composer-host\"]::before{content:\"● INCUBATING\";color:#6a5a30;border:1.5px solid #cdb978;opacity:0;transition:opacity .25s}"
    "[data-slot=\"composer-host\"]::after{content:\"✓ GROWTH CHECKED\";color:#17695c;border:1px solid #17695c;--k:0;opacity:calc(.4 + .6*var(--k));transform:rotate(-2deg) scale(1);transition:--k 4s ease-out .5s,transform .45s cubic-bezier(.2,1.5,.4,1) .35s}"
    + busy("[data-slot=\"composer-host\"]::before") + "{opacity:1}"
    + busy("[data-slot=\"composer-host\"]::after") + "{--k:1;opacity:0;transform:rotate(-9deg) scale(1.9);transition:none}"
    # sidebar: a slab of agar with two offset bubble layers
    + SBI + "{background:var(--ag-b1) 0 0/240px 410px,var(--ag-b2) 60px 90px/170px 300px," + SLAB + "!important}"
    # thread rows: label-tape selection, room under the text for colonies
    "[data-thread-item] :is([role=\"button\"],[aria-busy],[aria-current]){border-radius:6px!important;padding-top:6px!important;padding-bottom:12px!important}"
    "[data-thread-item] [aria-current]:not([aria-current=\"false\"]){box-shadow:inset 0 0 0 1px rgba(23,105,92,.3),inset 6px 0 0 #b8d5cf}"
    # busy thread rows and the live Working row grow colonies along their lower edge (background longhands keep selected/hover fills)
    + pop_keyframes("ag-pop4", 4) + pop_keyframes("ag-pop6", 6)
    + f"[data-thread-item] [aria-busy=\"true\"]{{background-image:{rowd}!important;background-repeat:no-repeat!important;background-size:100% 100%!important;animation:ag-pop4 5s ease-in-out infinite}}"
    + f"[data-timeline-row-kind=\"working\"]{{padding-bottom:12px!important;background-image:{workd}!important;background-repeat:no-repeat!important;background-size:100% 100%!important;animation:ag-pop6 6s ease-in-out infinite}}"
    # work rows: field-note mono with a dotted margin tick
    f"[data-timeline-row-kind=\"work\"]{{font-family:{MONO};font-size:11px!important;letter-spacing:0;border-left:2px dotted rgba(23,105,92,.5);padding-left:10px!important}}"
    # hover: a single colony seeds under the pointer, ringed like a picked colony
    f"[data-thread-item]{{background-image:{hoverd};background-repeat:no-repeat;transition:--h .4s cubic-bezier(.2,.8,.3,1)}}"
    "[data-thread-item]:hover{--h:1}[data-thread-item]:has([aria-busy=\"true\"]){background-image:none}"
    # monogram: specimen-label chip
    f"[data-slot=\"project-monogram\"]{{font-family:{MONO}!important;text-transform:uppercase;letter-spacing:.04em;background:#fffdf3!important;color:#3a2f15!important;border:1px solid #cdb978!important;border-radius:3px!important}}"
    # narrow windows (<1460px): no gutter art; plate 07 docks small at the foot of the sidebar, under a sidebar-coloured scrim
    "@media (max-width:1459px){"
    + f"{CONV}::before,{CONV}::after{{display:none}}"
    + SBI + "{background-image:" + ",".join([dock_images, "var(--ag-b1)", "var(--ag-b2)", SLAB]) + "!important;"
    + "background-size:" + ",".join([dock_size, "240px 410px", "170px 300px", "100% 100%"]) + "!important;"
    + "background-position:" + ",".join([dock_pos, "0 0", "60px 90px", "0 0"]) + "!important;"
    + "background-repeat:" + ",".join(["no-repeat"] * (nd + 1) + ["repeat", "repeat", "no-repeat"]) + "!important;"
    + "}}"
    # messages
    "[data-user-message-bubble]{background:#dcebe3!important;border:1px solid #6aa89c!important;border-radius:12px!important;box-shadow:inset 0 0 0 3px #dcebe3,inset 0 0 0 4px rgba(23,105,92,.28)}"
    "[data-slot=\"composer-host\"]{background:#fffdf5!important;border:1px solid #cdbf93!important;border-radius:18px!important;box-shadow:inset 0 0 0 3px #fffdf5,inset 0 0 0 4px #ecdfb6;transition:border-color .25s,box-shadow .35s}"
    "[data-slot=\"composer-host\"]:focus-within{border-color:#17695c!important;box-shadow:inset 0 0 0 3px #fffdf5,inset 0 0 0 4px rgba(23,105,92,.45),0 0 0 4px rgba(23,105,92,.13)}"
    ".chat-markdown-codeblock{background:#efe9d2!important;border:1px dashed #b9a56a!important;border-radius:10px!important}"
    ".chat-markdown :not(pre)>code{color:#5a2d7a;background:rgba(111,59,145,.09);padding:.05em .32em;border-radius:5px}"
    f".chat-markdown :is(h1,h2,h3){{font-family:{SERIF};font-style:italic;letter-spacing:.005em}}.chat-markdown :is(h1,h2,h3) code{{font-style:normal}}"
    ".chat-markdown :is(h1,h2){border-bottom:2px dotted rgba(23,105,92,.4);padding-bottom:.2em}"
    f".chat-markdown a{{color:{TEAL}!important;text-decoration-style:dotted;text-decoration-thickness:2px;text-underline-offset:3px}}"
    # markdown: margin note, specimen table, dotted rule, colony bullets
    f".chat-markdown blockquote{{border-left:3px dotted {TEAL};background:rgba(23,105,92,.06);padding:.4em .9em;margin:.8em 0;border-radius:0 8px 8px 0;font-family:{SERIF};font-style:italic}}"
    ".chat-markdown table{border-collapse:collapse}"
    f".chat-markdown th{{font-family:{MONO};font-size:.78em;text-transform:uppercase;letter-spacing:.1em;border-bottom:2px dotted {TEAL}!important;text-align:left}}"
    ".chat-markdown td{border-bottom:1px dotted #b9a56a!important}"
    ".chat-markdown hr{border:0!important;border-top:2px dotted rgba(23,105,92,.45)!important;background:none!important;height:0}"
    f".chat-markdown ul>li::marker{{content:\"● \";color:{TEAL};font-size:.75em}}.chat-markdown ol>li::marker{{color:{TEAL};font-family:{MONO};font-weight:700}}"
    "::selection{background:rgba(95,175,155,.38)}"
    # popups: double petri rim; tooltip as lab tape
    "[data-slot=\"dialog-popup\"],[data-slot=\"popover-popup\"],[data-slot=\"menu-popup\"]{border-radius:14px!important;border:1px solid #cdbf93!important;box-shadow:0 0 0 3px #fffdf5,0 0 0 4px #cdbf93,0 14px 34px rgba(70,50,10,.2)!important}"
    f"[data-slot=\"tooltip-popup\"]{{background:#fffdf3!important;color:#3a2f15!important;border:1px solid #cdb978!important;border-radius:3px!important;font-family:{MONO}!important;font-size:11px!important;letter-spacing:.06em;box-shadow:inset 4px 0 0 #b8d5cf,0 6px 16px rgba(70,50,10,.18)!important}}"
    # controls
    "[data-slot=\"button\"]{border-radius:10px!important;box-shadow:inset 0 0 0 2px rgba(248,244,230,.28);transition:box-shadow .2s,transform .15s}"
    "[data-slot=\"button\"]:hover{box-shadow:inset 0 0 0 2px rgba(248,244,230,.55)}[data-slot=\"button\"]:active{transform:scale(.96)}"
    "[data-slot=\"input\"],[data-slot=\"select-trigger\"]{border-radius:10px!important;background:#fffdf5!important;border:1px solid #c9bb8f!important;box-shadow:inset 0 0 0 2px #fffdf5,inset 0 0 0 3px #ecdfb6;transition:border-color .2s}"
    "[data-slot=\"input\"]:hover,[data-slot=\"select-trigger\"]:hover{border-color:#a99a68!important}"
    f"[data-slot=\"input\"]:focus-visible,[data-slot=\"select-trigger\"]:focus-visible{{border-color:{TEAL}!important;box-shadow:inset 0 0 0 2px #fffdf5,inset 0 0 0 3px rgba(23,105,92,.45)}}"
    "[data-slot=\"switch\"]{border:1px solid #b9a56a!important;background:#ebe3c8!important}[data-slot=\"switch\"][aria-checked=\"true\"]{background:#17695c!important;border-color:#0f574b!important}"
    "[data-slot=\"switch\"]>*{background:radial-gradient(circle at 38% 34%,#fffaf0,#e9dcb4)!important;box-shadow:inset 0 0 0 1px rgba(59,42,5,.3)!important}"
    f":focus-visible{{outline:2px solid {TEAL};outline-offset:2px}}"
    "[data-slot=\"composer-host\"] :focus-visible,.composer-tiptap:focus-visible{outline:none!important}"
    "svg.lucide{stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round}"
    # panels
    "[data-thread-details-card]{background-color:#fffdf3!important;border:1px solid #c7b57a!important;border-radius:6px!important;background-image:repeating-linear-gradient(180deg,transparent 0 23px,rgba(31,120,108,.1) 23px 24px)!important;box-shadow:inset 6px 0 0 #b8d5cf}"
    "[data-thread-terminal-drawer]{border-top:2px dashed #b9a56a!important;background-color:#f4efdd!important}"
    f"[data-settings-page-scroll]{{background:{SMALLGRID},#f8f4e6!important}}"
    # scrollbars
    "::-webkit-scrollbar{width:11px;height:11px}::-webkit-scrollbar-track{background:rgba(216,202,166,.25)}"
    "::-webkit-scrollbar-thumb,[data-slot=\"scroll-area-thumb\"]{background:rgba(122,106,69,.38)!important;border-radius:999px!important;border:2px solid transparent;background-clip:padding-box}"
    "::-webkit-scrollbar-thumb:hover{background:rgba(23,105,92,.6)!important;background-clip:padding-box}"
    "[data-slot=\"scroll-area-scrollbar\"]{background:transparent}"
    # reduced motion: nothing animates; plates show every colony (registered defaults are 1), dots are grown, stamp is in place
    "@media (prefers-reduced-motion:reduce){"
    + busy(CONV + "::before") + "," + busy(CONV + "::after") + "{animation:none!important}"
    + busy("[data-chat-header]") + "{animation:none!important;background-size:28px 8px!important}"
    + "[data-slot=\"composer-host\"]::after{transition:none!important;--k:0;opacity:.4;transform:rotate(-2deg) scale(1)}"
    + "[data-thread-item] [aria-busy=\"true\"],[data-timeline-row-kind=\"working\"]{animation:none!important;--g1:1;--g2:1;--g3:1;--g4:1;--g5:1;--g6:1}"
    + f"{CONV}::before,{CONV}::after,[data-slot=\"composer-host\"]::before,[data-slot=\"composer-host\"]::after,[data-thread-item],[data-slot=\"button\"],[data-chat-header]{{transition:none!important}}}}"
)

_d = 0
for _c in css:
    _d += (_c == "{") - (_c == "}")
    assert _d >= 0, "unbalanced css"
assert _d == 0, "css braces unbalanced"
assert css.index("[data-user-message-bubble]") < css.index("@media (prefers-reduced-motion"), "order"
_dd = 0
for _c in css[:css.index("[data-user-message-bubble]")]:
    _dd += (_c == "{") - (_c == "}")
assert _dd == 0, "bubble rule not at depth 0"

theme = {"version": 1, "id": "agar", "name": "Agar", "appearance": "light", "accent": TEAL, "canvas": "#f8f4e6", "colors": colors, "css": css}
out = os.path.join(HERE, "..")
with open(os.path.join(out, "agar.json"), "w") as fh:
    json.dump(theme, fh, ensure_ascii=False)
print("css chars:", len(css))


# ------------------------------------------------------------ landing-page SVGs (img files): animated + static twins
def site_plate_a(static=False):
    main, sat = plate_a_pts()
    pts = main + sat
    body = "".join(colony(i, x, y, r, col, halo=h) for i, (x, y, r, col, h) in enumerate(pts))
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 360 420'><style>{label_css()}{anim_css(len(pts), 3, 75, 15, static, 14)}</style>"
            + defs(AGAR_A) + plate_base(AGAR_A) + f"<g class='cols'>{body}</g>" + label(*LAB_A[0]) + "</svg>")


def site_plate_b(static=False):
    lines_, main, sat = plate_b_pts()
    pts = main + sat
    body = "".join(colony(i, x, y, r, col, halo=True) for i, (x, y, r, col, h) in enumerate(pts))
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 360 420'><style>{label_css()}{anim_css(len(pts), 3, 80, 9, static, 14)}</style>"
            + defs(AGAR_B) + plate_base(AGAR_B) + streak_svg_paths(lines_) + f"<g class='cols'>{body}</g>" + label(*LAB_B[0]) + "</svg>")


os.makedirs(os.path.join(out, "assets", "svg"), exist_ok=True)
for n, s in (("plate-growth", site_plate_a()), ("plate-streak", site_plate_b()), ("plate-growth-static", site_plate_a(True)),
             ("plate-streak-static", site_plate_b(True)), ("entry", entry_svg()), ("ruler", ruler_svg())):
    with open(os.path.join(out, "assets", "svg", f"{n}.svg"), "w") as fh:
        fh.write(s.replace("%23", "#"))
