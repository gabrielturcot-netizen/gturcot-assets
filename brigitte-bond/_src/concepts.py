import math, os
from textpath import F, shape, text, load
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

OUT = os.path.join(os.path.dirname(__file__), 'out'); os.makedirs(OUT, exist_ok=True)
# Encres process (approximations sRGB standard)
C, M, Y, K = '#00AEEF', '#EC008C', '#FFF200', '#231F20'
CM, MY, CY = '#2E3192', '#ED1C24', '#00A651'
GREY = '#6D6E71'

DMS  = F('dm-serif-display', 'dm-serif-display-latin-400-normal.woff')
FR6  = F('fraunces', 'fraunces-latin-600-normal.woff')
JO4  = F('jost', 'jost-latin-400-normal.woff')
JO5  = F('jost', 'jost-latin-500-normal.woff')
MO7  = F('montserrat', 'montserrat-latin-700-normal.woff')
MO5  = F('montserrat', 'montserrat-latin-500-normal.woff')

TAG = 'IMPRESSION GRAPHIQUE'

def glyph(path, ch, size, x=0, y=0):
    """Tracé d'un seul glyphe, origine ligne de base. Retourne d, bounds."""
    d, b, adv = shape(path, ch, size)
    return d, b

def svg(w, h, body, title='Brigitte Bond'):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}">'
            f'<title>{title}</title>{body}</svg>')

def save(name, s):
    p = os.path.join(OUT, name + '.svg'); open(p, 'w').write(s); return p


def icon(name, body, b, S_=420, fill=0.72, bg='#FFFFFF'):
    x0, y0, x1, y1 = b
    k = fill * S_ / max(x1 - x0, y1 - y0)
    tx = S_ / 2 - k * (x0 + x1) / 2; ty = S_ / 2 - k * (y0 + y1) / 2
    rect = f'<rect width="{S_}" height="{S_}" fill="{bg}"/>' if bg else ''
    save(name, svg(S_, S_, f'{rect}<g transform="translate({tx:.2f} {ty:.2f}) scale({k:.4f})">{body}</g>'))

# ---------------------------------------------------------------- A · Deux encres
def mark_A(x, y, size, solid=False):
    """Deux B superposés cyan/magenta, zone de surimpression en bleu."""
    d, (x0, y0, x1, y1) = glyph(DMS, 'B', size)
    w = x1 - x0
    dx = w * 0.46
    tx1, tx2 = x - x0, x - x0 + dx
    if solid:
        return (f'<path transform="translate({tx1:.2f} {y:.2f})" d="{d}" fill="{K}"/>'
                f'<path transform="translate({tx2:.2f} {y:.2f})" d="{d}" fill="{K}"/>'), (x, y + y0, x + w + dx, y + y1)
    cid = f'clipA{int(x)}{int(y)}'
    body = (f'<defs><clipPath id="{cid}"><path transform="translate({tx1:.2f} {y:.2f})" d="{d}"/></clipPath></defs>'
            f'<path transform="translate({tx1:.2f} {y:.2f})" d="{d}" fill="{C}"/>'
            f'<path transform="translate({tx2:.2f} {y:.2f})" d="{d}" fill="{M}"/>'
            f'<g clip-path="url(#{cid})"><path transform="translate({tx2:.2f} {y:.2f})" d="{d}" fill="{CM}"/></g>')
    return body, (x, y + y0, x + w + dx, y + y1)

def concept_A():
    body, (mx0, my0, mx1, my1) = mark_A(0, 0, 300)
    mh = my1 - my0
    gap = 46
    name, nb = text(DMS, 'Brigitte Bond', 100, x=mx1 + gap, y=0, fill=K)
    # aligne la ligne de base du nom sur ~58 % de la hauteur du monogramme
    base = my0 + mh * 0.60
    name, nb = text(DMS, 'Brigitte Bond', 100, x=mx1 + gap, y=base, fill=K)
    tag, tb = text(JO5, TAG, 25.5, x=nb[0] + 3, y=base + 52, tracking=0.34, fill=GREY)
    pad = 40
    x0, y0 = mx0 - pad, min(my0, nb[1]) - pad
    x1, y1 = max(nb[2], tb[2]) + pad, max(my1, tb[3]) + pad
    g = f'<g transform="translate({-x0:.2f} {-y0:.2f})">{body}{name}{tag}</g>'
    save('A_deux-encres_horizontal', svg(x1 - x0, y1 - y0, g))
    ib, bb = mark_A(0, 0, 300)
    icon('A_deux-encres_icone', ib, bb, fill=0.70)

# ---------------------------------------------------------------- B · Repère
def reg_mark(cx, cy, r, sw, color, ext=0.42, csw=None):
    csw = csw or sw * 0.5
    L = r * (1 + ext)
    return (f'<g fill="none" stroke="{color}">'
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r - sw/2:.2f}" stroke-width="{sw:.2f}"/>'
            f'<path d="M{cx-L:.2f} {cy:.2f}H{cx+L:.2f}M{cx:.2f} {cy-L:.2f}V{cy+L:.2f}" stroke-width="{csw:.2f}"/>'
            f'</g>')

def fit_tracking(path, txt, size, width):
    _, b, _ = shape(path, txt, size)
    return (width - (b[2] - b[0])) / ((len(txt) - 1) * size)

def concept_B():
    size = 120
    left, lb, ladv = shape(JO5, 'Brigitte B', size)
    _, ob, oadv = shape(JO5, 'o', size)
    right, rb, radv = shape(JO5, 'nd', size)
    sp = 0.11 * size   # air supplémentaire de chaque côté du repère
    xr = ladv + oadv + 2 * sp
    ocx = ladv + sp + (ob[0] + ob[2]) / 2; ocy = (ob[1] + ob[3]) / 2   # coordonnées SVG (y vers le bas)
    r = (ob[2] - ob[0]) / 2
    stem = 0.085 * size
    mark = reg_mark(ocx, ocy, r, stem, M, ext=0.30, csw=stem * 0.40)
    body = (f'<path d="{left}" fill="{K}"/>'
            f'<path transform="translate({xr:.2f} 0)" d="{right}" fill="{K}"/>' + mark)
    x_start, x_end = lb[0], xr + rb[2]
    tag, tb = text(JO4, TAG, 28, x=x_start + 3, y=76, tracking=0.36, fill=GREY)
    pad = 44
    top = min(lb[1], rb[1], ocy - r * 1.30)
    x0, y0, x1, y1 = x_start - pad, top - pad, max(x_end, tb[2]) + pad, tb[3] + pad
    g = f'<g transform="translate({-x0:.2f} {-y0:.2f})">{body}{tag}</g>'
    save('B_repere_horizontal', svg(x1 - x0, y1 - y0, g))
    # icône : B dans l'anneau de repérage, réticule à l'extérieur
    R = 150; sw = 15; L = 44
    d, (b0, b1_, b2, b3) = glyph(JO5, 'B', 190)
    bx = -(b0 + b2) / 2; by = -(b1_ + b3) / 2
    ib = (f'<circle cx="0" cy="0" r="{R - sw/2}" fill="none" stroke="{M}" stroke-width="{sw}"/>'
          f'<path d="M0 {-R-L}V{-R+2}M0 {R-2}V{R+L}M{-R-L} 0H{-R+2}M{R-2} 0H{R+L}" stroke="{M}" stroke-width="{sw*0.55}"/>'
          f'<path transform="translate({bx:.2f} {by:.2f})" d="{d}" fill="{K}"/>')
    icon('B_repere_icone', ib, (-R - L, -R - L, R + L, R + L), fill=0.80)

# ---------------------------------------------------------------- C · Papier Bond
def sheet(x, y, w, h, fold, fill, letter_d=None, lb=None, letter_fill='#FFFFFF', bar=True):
    """Feuille à coin corné + barre de contrôle CMJN."""
    p = f'M{x} {y}H{x+w-fold}L{x+w} {y+fold}V{y+h}H{x}Z'
    s = f'<path d="{p}" fill="{fill}"/>'
    s += f'<path d="M{x+w-fold} {y}V{y+fold}H{x+w}Z" fill="#FFFFFF" opacity="0.55"/>'
    if letter_d:
        s += letter_d
    if bar:
        n = 4; m = w * 0.12; bw = (w - 2 * m) / n; bh = h * 0.07; by = y + h - m * 0.75 - bh
        for i, col in enumerate([C, M, Y, '#FFFFFF']):
            s += f'<rect x="{x + m + i*bw:.2f}" y="{by:.2f}" width="{bw:.2f}" height="{bh:.2f}" fill="{col}"/>'
    return s

def concept_C():
    W, H = 220, 284; fold = 58
    d, (g0, g1, g2, g3) = glyph(FR6, 'B', 190)
    gw, gh = g2 - g0, g3 - g1
    lx = (W - gw) / 2 - g0 - 4; ly = H * 0.47 + gh / 2
    letter = f'<path transform="translate({lx:.2f} {ly:.2f})" d="{d}" fill="#FFFFFF"/>'
    ic = sheet(0, 0, W, H, fold, K, letter)
    gap = 48
    base = H * 0.56
    name, nb = text(FR6, 'Brigitte Bond', 104, x=W + gap, y=base, fill=K)
    tag, tb = text(JO5, TAG, 26, x=nb[0] + 3, y=base + 58, tracking=0.335, fill=GREY)
    pad = 40
    x0, y0, x1, y1 = -pad, -pad, max(nb[2], tb[2]) + pad, H + pad
    g = f'<g transform="translate({-x0:.2f} {-y0:.2f})">{ic}{name}{tag}</g>'
    save('C_papier-bond_horizontal', svg(x1 - x0, y1 - y0, g))
    icon('C_papier-bond_icone', ic, (0, 0, W, H), fill=0.74)

# ---------------------------------------------------------------- D · Trame
def halftone(x, y, size, step=13, angle=45, col=K, minr=None, maxr=None, idc='ht'):
    d, (g0, g1, g2, g3) = glyph(MO7, 'B', size)
    tx, ty = x - g0, y
    maxr = maxr or step * 0.64
    minr = minr or step * 0.24
    w, h = g2 - g0, g3 - g1
    cx0, cy0 = x, y + g1
    dots = []
    a = math.radians(angle)
    R = math.hypot(w, h)
    n = int(R / step) + 2
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            u, v = i * step, j * step
            px = cx0 + w / 2 + u * math.cos(a) - v * math.sin(a)
            py = cy0 + h / 2 + u * math.sin(a) + v * math.cos(a)
            if not (cx0 - step <= px <= cx0 + w + step and cy0 - step <= py <= cy0 + h + step):
                continue
            # dégradé diagonal : haut-gauche plein -> bas-droite clair
            t = ((px - cx0) / w * 0.55 + (py - cy0) / h * 0.45)
            t = min(max(t, 0), 1)
            r = maxr * (1 - t) + minr * t
            dots.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.2f}"/>')
    body = (f'<defs><clipPath id="{idc}"><path transform="translate({tx:.2f} {ty:.2f})" d="{d}"/></clipPath></defs>'
            f'<g clip-path="url(#{idc})" fill="{col}">{"".join(dots)}</g>')
    return body, (x, y + g1, x + w, y + g3)

def concept_D():
    body, (mx0, my0, mx1, my1) = halftone(0, 0, 330, step=12.5, col=M, idc='htA')
    mh = my1 - my0
    gap = 44
    base = my0 + mh * 0.57
    name, nb = text(MO7, 'Brigitte Bond', 92, x=mx1 + gap, y=base, fill=K, tracking=-0.01)
    tag, tb = text(MO5, TAG, 24, x=nb[0] + 3, y=base + 52, tracking=0.37, fill=GREY)
    pad = 40
    x0, y0, x1, y1 = mx0 - pad, my0 - pad, max(nb[2], tb[2]) + pad, my1 + pad
    g = f'<g transform="translate({-x0:.2f} {-y0:.2f})">{body}{name}{tag}</g>'
    save('D_trame_horizontal', svg(x1 - x0, y1 - y0, g))
    ib, bb = halftone(0, 0, 330, step=12.5, col=M, idc='htB')
    icon('D_trame_icone', ib, bb, fill=0.70)

if __name__ == '__main__':
    concept_A(); concept_B(); concept_C(); concept_D()
    print('\n'.join(sorted(os.listdir(OUT))))
