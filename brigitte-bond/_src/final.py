"""Brigitte Bond — piste A « Deux encres », trousse finale.
Géométrie booléenne (skia-pathops) : aucun clipPath ni contour, que des surfaces pleines
→ compatible Illustrator, Canva, découpe vinyle, broderie, gravure."""
import os, math
import pathops
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from textpath import F, shape, load

OUT = os.path.join(os.path.dirname(__file__), 'final'); os.makedirs(OUT, exist_ok=True)
C, M, K, W_ = '#00AEEF', '#EC008C', '#231F20', '#FFFFFF'
CM, CM_INV = '#2E3192', '#ECAEF8'
GREY, GREY_INV = '#6D6E71', '#B1B3B6'
DMS = F('dm-serif-display', 'dm-serif-display-latin-400-normal.woff')
JO5 = F('jost', 'jost-latin-500-normal.woff')
NAME, TAG = 'Brigitte Bond', 'IMPRESSION GRAPHIQUE'

# ------------------------------------------------------------------ géométrie
def text_path(font, txt, size, tracking=0.0):
    """Texte -> pathops.Path (origine ligne de base, y vers le bas)."""
    import uharfbuzz as hb
    tt, hbf = load(font); s = size / tt['head'].unitsPerEm
    buf = hb.Buffer(); buf.add_str(txt); buf.guess_segment_properties()
    hb.shape(hbf, buf, {"kern": True, "liga": True})
    gs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    p = pathops.Path(); pen = p.getPen(); x = 0
    n = len(buf.glyph_infos)
    for i, (inf, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        gs[order[inf.codepoint]].draw(TransformPen(pen, (s, 0, 0, -s, x + pos.x_offset * s, -pos.y_offset * s)))
        x += pos.x_advance * s + (tracking * size if i < n - 1 else 0)
    p.simplify()
    return p

def moved(p, dx=0, dy=0, k=1):
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), (k, 0, 0, k, dx, dy))); return q

def op(a, b, kind):
    return pathops.op(a, b, getattr(pathops.PathOp, kind))

def d_of(p):
    pen = SVGPathPen(None, ntos=lambda v: ('%.2f' % v).rstrip('0').rstrip('.')); p.draw(pen); return pen.getCommands()

def bnd(p): return p.bounds  # (xmin, ymin, xmax, ymax)

def fit_tracking(font, txt, size, width):
    b = bnd(text_path(font, txt, size)); return (width - (b[2] - b[0])) / ((len(txt) - 1) * size)

# ------------------------------------------------------------------ symbole BB
def mark(mode, size=300):
    """Liste de (pathops.Path, couleur) dans l'ordre de dessin. Origine : coin haut-gauche."""
    b = text_path(DMS, 'B', size); x0, y0, x1, y1 = bnd(b)
    b1 = moved(b, -x0, -y0); dx = (x1 - x0) * 0.46
    b2 = moved(b1, dx, 0)
    if mode == 'noir':
        # une encre : B1 en contour (anneau vectorisé), B2 plein ; l'anneau passe en défonce dans B2 (XOR)
        ring = pathops.Path(); b1.draw(ring.getPen())
        ring.stroke(size * 0.024, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
        ring.convertConicsToQuads(); ring.simplify()
        return [(op(b2, ring, 'XOR'), K)]
    if mode == 'noir-plein':
        # variante petits formats : deux B pleins, la zone commune en défonce
        return [(op(b1, b2, 'XOR'), K)]
    inter = op(b1, b2, 'INTERSECTION')
    return [(b1, C), (op(b2, inter, 'DIFFERENCE'), M), (inter, CM if mode == 'couleur' else CM_INV)]

def mark_bounds(parts):
    bs = [bnd(p) for p, _ in parts if p.area]
    return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))

# ------------------------------------------------------------------ assemblages
INK = {'couleur': (K, GREY), 'noir': (K, K), 'noir-plein': (K, K), 'inverse': (W_, GREY_INV)}
BG = {'couleur': None, 'noir': None, 'noir-plein': None, 'inverse': K}

def wordmark(mode, name_size=100, tag_size=35, tagline=True, center=False):
    ink, tagc = INK[mode]
    n = text_path(DMS, NAME, name_size); nb = bnd(n)
    parts = [(moved(n, -nb[0], 0), ink)]
    w = nb[2] - nb[0]
    if tagline:
        trk = fit_tracking(JO5, TAG, tag_size, w)
        t = text_path(JO5, TAG, tag_size, trk); tb = bnd(t)
        parts.append((moved(t, -tb[0], name_size * 0.50 + tag_size * 0.70), tagc))
    return parts

def place(parts, dx, dy): return [(moved(p, dx, dy), c) for p, c in parts]

def lockup_h(mode, tagline=True, gap=46):
    mk = mark(mode); mb = mark_bounds(mk)
    wm = wordmark(mode, tagline=tagline); wb = mark_bounds(wm)
    cap_top = bnd(wm[0][0])[1]
    bottom = wb[3] if tagline else 0          # ligne de base du nom quand pas de slogan
    dy = (mb[1] + mb[3]) / 2 - (cap_top + bottom) / 2
    return mk + place(wm, mb[2] + gap, dy)

def lockup_v(mode, gap=56):
    mk = mark(mode); mb = mark_bounds(mk)
    wm = wordmark(mode); wb = mark_bounds(wm)
    W = max(mb[2] - mb[0], wb[2] - wb[0])
    cap_top = bnd(wm[0][0])[1]
    return place(mk, (W - (mb[2] - mb[0])) / 2, 0) + place(wm, (W - (wb[2] - wb[0])) / 2, mb[3] + gap - cap_top)

def to_svg(parts, pad=40, bg=None, square=None, fill=None, circle_safe=False):
    x0, y0, x1, y1 = mark_bounds(parts)
    if square:
        S_ = square; w, h = x1 - x0, y1 - y0
        k = fill * S_ / max(w, h)
        if circle_safe:                        # la diagonale doit tenir dans le cercle inscrit
            k = min(k, 0.86 * S_ / math.hypot(w, h))
        tx, ty = S_ / 2 - k * (x0 + x1) / 2, S_ / 2 - k * (y0 + y1) / 2
        g = f'<g transform="translate({tx:.2f} {ty:.2f}) scale({k:.5f})">'
        W, H = S_, S_
    else:
        W, H = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
        g = f'<g transform="translate({pad - x0:.2f} {pad - y0:.2f})">'
    body = ''.join(f'<path d="{d_of(p)}" fill="{c}"/>' for p, c in parts if p.area)
    rect = f'<rect width="{W:.0f}" height="{H:.0f}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}">'
            f'<title>Brigitte Bond — Impression graphique</title>{rect}{g}{body}</g></svg>')

def save(name, s):
    p = os.path.join(OUT, 'svg', name + '.svg'); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(s)

if __name__ == '__main__':
    import glob
    for f in glob.glob(os.path.join(OUT, 'svg', '*.svg')): os.remove(f)
    for m in ('couleur', 'noir', 'inverse'):
        save(f'bb_horizontal_{m}', to_svg(lockup_h(m)))
        save(f'bb_horizontal-compact_{m}', to_svg(lockup_h(m, tagline=False)))
        save(f'bb_vertical_{m}', to_svg(lockup_v(m), pad=50))
        save(f'bb_symbole_{m}', to_svg(mark(m), pad=20))
    for m in ('couleur', 'noir-plein', 'inverse'):
        save(f'bb_icone_{m}', to_svg(mark(m), square=512, fill=0.70, bg=BG[m] or W_))
        save(f'bb_avatar-rond_{m}', to_svg(mark(m), square=512, fill=0.70, circle_safe=True, bg=BG[m] or W_))
        save(f'bb_favicon_{m}', to_svg(mark(m), square=64, fill=0.92, bg=BG[m] or W_))
    save('bb_symbole_noir-plein', to_svg(mark('noir-plein'), pad=20))
    print(len(os.listdir(os.path.join(OUT, 'svg'))), 'SVG')
