"""SVG -> PDF vectoriel en CMJN réel (pour l'imprimeur)."""
import sys, os, glob
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Group, Shape
from reportlab.lib.colors import CMYKColor, Color

CMYK = {  # hex écran -> CMJN (0-1)
    '00aeef': (1, 0, 0, 0), 'ec008c': (0, 1, 0, 0), '2e3192': (1, 1, 0, 0),
    '231f20': (0, 0, 0, 1), '6d6e71': (0, 0, 0, .70), 'b1b3b6': (0, 0, 0, .35),
    'ffffff': (0, 0, 0, 0), 'ecaef8': (.08, .32, 0, 0),
}
def hx(c):
    return '%02x%02x%02x' % tuple(round(v * 255) for v in (c.red, c.green, c.blue))
unknown = set()
def walk(node):
    if isinstance(node, Group):
        for ch in node.contents: walk(ch)
    for attr in ('fillColor', 'strokeColor'):
        c = getattr(node, attr, None)
        if isinstance(c, Color) and not isinstance(c, CMYKColor):
            h = hx(c)
            if h in CMYK: setattr(node, attr, CMYKColor(*CMYK[h]))
            else: unknown.add(h)
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
for f in sorted(glob.glob(os.path.join(src, '*.svg'))):
    n = os.path.basename(f)[:-4]
    if 'favicon' in n or 'avatar' in n or 'icone' in n: continue
    d = svg2rlg(f); walk(d)
    renderPDF.drawToFile(d, os.path.join(dst, n + '.pdf'), title=f'Brigitte Bond — {n}', author='Brigitte Bond')
print('couleurs non converties :', unknown or 'aucune')
