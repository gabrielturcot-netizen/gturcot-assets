"""Brigitte Bond — v2 : corrections issues de la critique de design."""
import os
from textpath import F, shape, text

OUT = os.path.join(os.path.dirname(__file__), 'v2'); os.makedirs(OUT, exist_ok=True)
C, M, Y, K = '#00AEEF', '#EC008C', '#FFF200', '#231F20'
CM = '#2E3192'            # surimpression cyan + magenta (fond clair)
CM_INV = '#ECAEF8'        # superposition « lumière » cyan + magenta (fond foncé)
W_ = '#FFFFFF'
GREY, GREY_INV = '#6D6E71', '#B1B3B6'

DMS = F('dm-serif-display', 'dm-serif-display-latin-400-normal.woff')
FR6 = F('fraunces', 'fraunces-latin-600-normal.woff')
JO5 = F('jost', 'jost-latin-500-normal.woff')
TAG = 'IMPRESSION GRAPHIQUE'

# palettes par mode
P = {
  'couleur': dict(ink=K, tag=GREY, bg=None),
  'noir':    dict(ink=K, tag=K, bg=None),
  'inverse': dict(ink=W_, tag=GREY_INV, bg=K),
}

def svg(w, h, body, bg=None):
    rect = f'<rect width="{w:.0f}" height="{h:.0f}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}">'
            f'<title>Brigitte Bond — Impression graphique</title>{rect}{body}</svg>')

def save(name, s):
    os.makedirs(os.path.dirname(os.path.join(OUT, name)), exist_ok=True)
    open(os.path.join(OUT, name + '.svg'), 'w').write(s)

def fit_tracking(path, txt, size, width):
    _, b, _ = shape(path, txt, size)
    return (width - (b[2] - b[0])) / ((len(txt) - 1) * size)

def wordmark(font, name_size, tag_size, mode, x=0, align='start', tagline=True, gap_k=0.50):
    """Nom + slogan justifié à la largeur du nom. Retourne (svg, bbox, name_bbox)."""
    p = P[mode]
    nm, nb = text(font, 'Brigitte Bond', name_size, x=x, y=0, anchor=align, fill=p['ink'])
    if not tagline:
        return nm, nb, nb
    nw = nb[2] - nb[0]
    trk = fit_tracking(JO5, TAG, tag_size, nw)
    ty = name_size * gap_k + tag_size * 0.70
    tg, tb = text(JO5, TAG, tag_size, x=nb[0], y=ty, tracking=trk, fill=p['tag'])
    return nm + tg, (min(nb[0], tb[0]), nb[1], max(nb[2], tb[2]), tb[3]), nb

# ============================================================ C · Papier Bond
SW, SH, FOLD = 220, 284, 58

def sheet(mode):
    x, y, w, h, f = 0, 0, SW, SH, FOLD
    body_p = f'M{x} {y}H{w-f}L{w} {f}V{h}H{x}Z'
    fold_p = f'M{w-f} {y}V{f}H{w}Z'
    dd, gb, _ = shape(FR6, 'B', 190)
    lx = (w - (gb[2] - gb[0])) / 2 - gb[0] - 4; ly = h * 0.47 + (gb[3] - gb[1]) / 2
    m = w * 0.12; bw = (w - 2 * m) / 4; bh = h * 0.07; by = h - m * 0.75 - bh
    if mode == 'couleur':
        sheet_c, letter_c, fold_c = K, W_, '#939598'
        bar = ''.join(f'<rect x="{m+i*bw:.2f}" y="{by:.2f}" width="{bw:.2f}" height="{bh:.2f}" fill="{c}"/>' for i, c in enumerate([C, M, Y, W_]))
        fold = f'<path d="{fold_p}" fill="{fold_c}"/>'
    elif mode == 'inverse':
        sheet_c, letter_c = W_, K
        bar = ''.join(f'<rect x="{m+i*bw:.2f}" y="{by:.2f}" width="{bw:.2f}" height="{bh:.2f}" fill="{c}"/>' for i, c in enumerate([C, M, Y, K]))
        fold = f'<path d="{fold_p}" fill="#BCBEC0"/>'
    else:  # noir : une seule encre, tout en défonce
        sheet_c, letter_c = K, W_
        s = 4.5
        bar = ''.join(f'<rect x="{m+i*bw+s/2+ (1.5 if i else 0):.2f}" y="{by+s/2:.2f}" width="{bw-s-(1.5 if i else 0):.2f}" height="{bh-s:.2f}" fill="{W_ if i==0 else "none"}" stroke="{W_}" stroke-width="{s}"/>' for i in range(4))
        fold = f'<defs><clipPath id="sheetbox"><rect width="{w}" height="{h}"/></clipPath></defs><path d="{fold_p}" fill="{W_}"/><path clip-path="url(#sheetbox)" d="M{w-f} {y}L{w} {f}" stroke="{K}" stroke-width="7" stroke-linecap="round"/>'
    return (f'<path d="{body_p}" fill="{sheet_c}"/>{fold}'
            f'<path transform="translate({lx:.2f} {ly:.2f})" d="{dd}" fill="{letter_c}"/>{bar}')

def C_horizontal(mode, tagline=True):
    wm, wb, nb = wordmark(FR6, 104, 37, mode, x=0, tagline=tagline)
    gap = 50
    # centre optique : du haut des capitales au bas du slogan (ou ligne de base du nom)
    cap_top = nb[1]; bottom = wb[3] if tagline else nb[3] - 22
    dy = SH / 2 - (cap_top + bottom) / 2
    dx = SW + gap - wb[0]
    pad = 40
    x1 = SW + gap + (wb[2] - wb[0])
    body = f'{sheet(mode)}<g transform="translate({dx:.2f} {dy:.2f})">{wm}</g>'
    W, H = x1 + 2 * pad, SH + 2 * pad
    return svg(W, H, f'<g transform="translate({pad} {pad})">{body}</g>', P[mode]['bg'])

def C_vertical(mode):
    wm, wb, nb = wordmark(FR6, 104, 37, mode, x=0)
    ww = wb[2] - wb[0]
    gap = 54
    W = max(ww, SW) ; sx = (W - SW) / 2
    dx = (W - ww) / 2 - wb[0]; dy = SH + gap - nb[1]
    pad = 50
    H = SH + gap + (wb[3] - nb[1])
    body = f'<g transform="translate({sx:.2f} 0)">{sheet(mode)}</g><g transform="translate({dx:.2f} {dy:.2f})">{wm}</g>'
    return svg(W + 2 * pad, H + 2 * pad, f'<g transform="translate({pad} {pad})">{body}</g>', P[mode]['bg'])

def C_icon(mode):
    S_ = 420; k = 0.74 * S_ / SH
    tx = S_ / 2 - k * SW / 2; ty = S_ / 2 - k * SH / 2
    bg = {'couleur': W_, 'noir': W_, 'inverse': K}[mode]
    return svg(S_, S_, f'<g transform="translate({tx:.2f} {ty:.2f}) scale({k:.4f})">{sheet(mode)}</g>', bg)

# ============================================================ A · Deux encres
def mark_A(mode, size=300):
    d, (x0, y0, x1, y1), _ = shape(DMS, 'B', size)
    w = x1 - x0; dx = w * 0.46
    t1, t2 = -x0, -x0 + dx
    P1 = f'<path transform="translate({t1:.2f} 0)" d="{d}"'
    P2 = f'<path transform="translate({t2:.2f} 0)" d="{d}"'
    clip1 = f'<clipPath id="a1{mode}">{P1}/></clipPath>'
    clip2 = f'<clipPath id="a2{mode}">{P2}/></clipPath>'
    if mode == 'noir':
        # B1 en contour, B2 plein ; dans la zone commune le contour passe en défonce blanche
        s = 7
        body = (f'<defs>{clip2}</defs>{P2} fill="{K}"/>'
                f'{P1} fill="none" stroke="{K}" stroke-width="{s}"/>'
                f'<g clip-path="url(#a2{mode})">{P1} fill="none" stroke="{W_}" stroke-width="{s}"/></g>')
    else:
        ov = CM if mode == 'couleur' else CM_INV
        body = (f'<defs>{clip1}</defs>{P1} fill="{C}"/>{P2} fill="{M}"/>'
                f'<g clip-path="url(#a1{mode})">{P2} fill="{ov}"/></g>')
    return body, (0, y0, w + dx, y1)

def A_horizontal(mode, tagline=True):
    mk, (mx0, my0, mx1, my1) = mark_A(mode)
    wm, wb, nb = wordmark(DMS, 100, 35, mode, x=0, tagline=tagline)
    gap = 46
    bottom = wb[3] if tagline else nb[3] - 22
    dy = (my0 + my1) / 2 - (nb[1] + bottom) / 2
    dx = mx1 + gap - wb[0]
    pad = 40
    x1 = mx1 + gap + (wb[2] - wb[0])
    body = f'{mk}<g transform="translate({dx:.2f} {dy:.2f})">{wm}</g>'
    W, H = x1 + 2 * pad, (my1 - my0) + 2 * pad
    return svg(W, H, f'<g transform="translate({pad} {pad - my0:.2f})">{body}</g>', P[mode]['bg'])

def A_icon(mode):
    mk, (x0, y0, x1, y1) = mark_A(mode)
    S_ = 420; k = 0.70 * S_ / max(x1 - x0, y1 - y0)
    tx = S_ / 2 - k * (x0 + x1) / 2; ty = S_ / 2 - k * (y0 + y1) / 2
    bg = {'couleur': W_, 'noir': W_, 'inverse': K}[mode]
    return svg(S_, S_, f'<g transform="translate({tx:.2f} {ty:.2f}) scale({k:.4f})">{mk}</g>', bg)

if __name__ == '__main__':
    for m in ('couleur', 'noir', 'inverse'):
        save(f'C_papier-bond/horizontal_{m}', C_horizontal(m))
        save(f'C_papier-bond/vertical_{m}', C_vertical(m))
        save(f'C_papier-bond/compact-sans-slogan_{m}', C_horizontal(m, tagline=False))
        save(f'C_papier-bond/icone_{m}', C_icon(m))
        save(f'A_deux-encres/horizontal_{m}', A_horizontal(m))
        save(f'A_deux-encres/icone_{m}', A_icon(m))
    for root, _, fs in os.walk(OUT):
        for f in sorted(fs): print(os.path.join(os.path.relpath(root, OUT), f))
