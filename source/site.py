"""Generate index.html (landing page) from agar.json so the palette table always matches the theme file."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
C = json.load(open(os.path.join(ROOT, "agar.json")))["colors"]
SITE = "https://joshsaintjacque.github.io/t3code-theme-agar/"
REPO = "https://github.com/joshsaintjacque/t3code-theme-agar"

LEFT = [("Canvas", "canvas", "The notebook page"), ("Sidebar", "sidebar", "The agar slab"), ("Message", "messageSurface", "Your prompts"),
        ("Code", "codeBackground", "Code blocks"), ("Border", "border", "Rules and frames"), ("Surface", "surface", "Composer and popovers")]
RIGHT = [("Text", "text", "Sepia-black ink"), ("Muted", "textMuted", "Notes and labels"), ("Accent", "accent", "Send, links, focus"),
         ("Accent text", "accentForeground", "On the accent"), ("Error", "error", "Failures"), ("Warning", "warning", "Cautions")]


def rows(items):
    out = []
    for name, key, use in items:
        h = C[key]
        out.append(f'<tr data-hex="{h}"><td class="sw"><i style="background:{h}"></i></td><td class="role">{name}</td>'
                   f'<td class="hex">{h.upper()}<span>COPIED</span></td><td class="use">{use}</td></tr>')
    return "".join(out)


TABLE = '<table class="schedule"><thead><tr><th class="sw"></th><th>Role</th><th>Hex</th><th class="use">Used for</th></tr></thead><tbody>{}</tbody></table>'

html = open(os.path.join(HERE, "site.template.html")).read()
html = html.replace("__PAL_L__", TABLE.format(rows(LEFT))).replace("__PAL_R__", TABLE.format(rows(RIGHT)))
html = html.replace("__SITE__", SITE).replace("__REPO__", REPO)
open(os.path.join(ROOT, "index.html"), "w").write(html)
print("index.html", len(html))
