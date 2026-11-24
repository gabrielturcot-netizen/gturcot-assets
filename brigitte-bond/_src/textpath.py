"""Convertit du texte en tracés SVG (vectoriel, sans dépendance de police)."""
import io, os
from functools import lru_cache
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import uharfbuzz as hb

FONTS = os.path.join(os.path.dirname(__file__), '..', 'fonts')
def F(pkg, file):
    import glob
    return glob.glob(os.path.join(FONTS, f'fontsource-{pkg}-*', 'package', 'files', file))[0]

@lru_cache(None)
def load(path):
    tt = TTFont(path)
    tt.flavor = None
    buf = io.BytesIO(); tt.save(buf)
    face = hb.Face(hb.Blob(buf.getvalue()))
    hbfont = hb.Font(face)
    return tt, hbfont

def shape(path, text, size, tracking=0.0, features=None):
    """Retourne (d, bbox, advance). tracking en em. Origine = ligne de base, x=0."""
    tt, hbfont = load(path)
    upem = tt['head'].unitsPerEm
    s = size / upem
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hbfont, buf, features or {"kern": True, "liga": True})
    gs = tt.getGlyphSet(); order = tt.getGlyphOrder()
    pen = SVGPathPen(gs, ntos=lambda v: ('%.2f' % v).rstrip('0').rstrip('.'))
    bpen = BoundsPen(gs)
    x = 0.0
    n = len(buf.glyph_infos)
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        name = order[info.codepoint]
        t = (s, 0, 0, -s, x + pos.x_offset * s, -pos.y_offset * s)
        gs[name].draw(TransformPen(pen, t))
        gs[name].draw(TransformPen(bpen, t))
        x += pos.x_advance * s
        if i < n - 1:
            x += tracking * size
    return pen.getCommands(), bpen.bounds, x

def text(path, txt, size, x=0, y=0, tracking=0.0, anchor='start', **attrs):
    """Élément <path> positionné; anchor = start|middle|end (sur la boîte d'encre)."""
    d, (x0, y0, x1, y1), adv = shape(path, txt, size, tracking)
    if anchor == 'middle': dx = x - (x0 + x1) / 2
    elif anchor == 'end': dx = x - x1
    else: dx = x - x0
    a = ' '.join(f'{k.replace("_","-")}="{v}"' for k, v in attrs.items())
    el = f'<path transform="translate({dx:.2f} {y:.2f})" d="{d}" {a}/>'
    return el, (x0 + dx, y0 + y, x1 + dx, y1 + y)
