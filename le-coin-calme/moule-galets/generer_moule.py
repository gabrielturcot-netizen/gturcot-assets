#!/usr/bin/env python3
"""
Générateur paramétrique de moule pour le coussin tactile « galets » (Le Coin Calme).

Produit : plaque en silicone en forme de stade (pilule) avec des galets en relief
sur une face, dos plat.

Fichiers produits (dossier stl/) :
  1. piece_reference.stl        : la pièce en silicone attendue (pour vérification, PAS à imprimer)
  2. moule_base.stl             : moule ouvert, 1 pièce (coulée à ras bord + arasage)
  3. moule_couvercle_plat.stl   : couvercle à jupe, trou de coulée + évents (dos plat, épaisseur exacte)
  4. moule_couvercle_noyau.stl  : couvercle à noyau économique (dos évidé, ~25 % de silicone en moins)

Dépendances : pip install manifold3d trimesh numpy matplotlib
Usage       : python3 generer_moule.py
Toutes les cotes sont en millimètres.  Modifier la section PARAMÈTRES puis relancer.
"""
import math, os, random
import numpy as np
import manifold3d as m
import trimesh

# ============================ PARAMÈTRES ====================================
# --- Pièce en silicone (mesurer l'original au pied à coulisse et ajuster) ---
L            = 105.0   # longueur hors-tout de la pièce
W            = 42.0    # largeur hors-tout de la pièce
T_BASE       = 6.0     # épaisseur de la plaque (original estimé à ~8 mm -> 6 mm = -25 % de silicone)
H_GALET      = 4.0     # hauteur max des galets au-dessus de la plaque

# --- Nappe de galets ---
GRAINE       = 7       # graine aléatoire : changer pour obtenir une autre disposition
GAP          = 1.8     # espace minimum entre deux galets (= épaisseur des cloisons du moule)
MARGE_BORD   = 2.5     # espace minimum entre un galet et le bord de la pièce
# (nombre, demi-grand-axe min, max, ratio petit/grand axe min, max)
FAMILLES     = [(2, 9.0, 11.0, 0.40, 0.50),    # 2 grands galets allongés
                (2, 5.0, 6.0, 0.80, 1.00),     # 2 grands galets ronds
                (12, 3.8, 5.0, 0.55, 0.95),    # moyens
                (18, 2.8, 3.8, 0.60, 1.00),    # petits
                (14, 1.8, 2.6, 0.70, 1.00)]    # très petits

# --- Moule ---
T_FOND       = 3.0     # épaisseur du plancher sous le galet le plus profond
T_PAROI      = 4.0     # épaisseur des parois latérales du moule
DEPOUILLE    = 0.3     # évasement de la cavité (par côté) entre le fond et le haut : aide au démoulage

# --- Couvercle ---
T_COUV       = 4.0     # épaisseur de la plaque du couvercle
H_JUPE       = 6.0     # hauteur de la jupe qui enveloppe le moule (auto-centrage)
T_JUPE       = 2.4     # épaisseur de la jupe
JEU_JUPE     = 0.25    # jeu par côté entre la jupe et le moule (ajuster selon l'imprimante)
D_COULEE     = 7.0     # diamètre du trou de coulée
D_ENTONNOIR  = 14.0    # diamètre de l'entonnoir côté extérieur
D_EVENT      = 2.5     # diamètre des évents
P_NOYAU      = 2.5     # profondeur du noyau économique (évidement du dos)
MARGE_NOYAU  = 7.0     # retrait du noyau par rapport au bord de la pièce

# --- Marquage « Le Coin Calme » (en miroir sur le moule => lisible sur la pièce démoulée) ---
TEXTE               = "Le Coin Calme"
TAILLE_TEXTE        = 8.0    # taille de police (hauteur des capitales ≈ 0,75 x taille)
H_TEXTE             = 0.8    # relief des lettres sur le moule = profondeur gravée dans le silicone
TEXTE_SUR_COUVERCLE = True   # texte au dos de la pièce (couvercles plat et à noyau)
TEXTE_FACE_GALETS   = False  # texte sur la face galets (moule ouvert) : réserve une bande sans galet
MARGE_TEXTE         = 2.5    # espace entre le texte et les galets (face galets)

DENSITE_SILICONE = 1.10  # g/cm³ (silicone platine type Dragon Skin / Ecoflex ≈ 1.07–1.12)
# ============================================================================

ICI = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(ICI, "stl")
APERCU = os.path.join(ICI, "apercu")
os.makedirs(STL, exist_ok=True); os.makedirs(APERCU, exist_ok=True)
m.set_circular_segments(96)
H_MOULE = T_FOND + H_GALET + T_BASE          # hauteur totale du moule base
EPS = 0.02                                    # recouvrement anti-faces coplanaires


# ------------------------------- utilitaires --------------------------------
def stade(longueur, largeur):
    """Section en forme de stade (rectangle terminé par 2 demi-cercles), centrée."""
    r = largeur / 2.0
    d = longueur / 2.0 - r
    return m.CrossSection.batch_hull([m.CrossSection.circle(r).translate((-d, 0)),
                                      m.CrossSection.circle(r).translate((d, 0))])


def prisme_stade(longueur, largeur, hauteur, z0=0.0, evasement=0.0):
    """Extrusion d'un stade ; evasement = agrandissement par côté au sommet (dépouille)."""
    s = ((longueur + 2 * evasement) / longueur, (largeur + 2 * evasement) / largeur)
    return m.Manifold.extrude(stade(longueur, largeur), hauteur, scale_top=s).translate((0, 0, z0))


def galet(a, b, h, x, y, ang_deg):
    """Galet = ellipsoïde tronqué : empreinte au sol de demi-axes (a, b), hauteur h.
    Centre de l'ellipsoïde sous le plan de base => flancs rentrants (dépouille naturelle)
    et sommet arrondi aplati, comme un galet de rivière."""
    c = 1.45 * h
    z0 = h - c                         # < 0 : centre sous la base
    k = math.sqrt(1 - (z0 / c) ** 2)   # facteur de l'empreinte au niveau z=0
    g = m.Manifold.sphere(1.0, 72).scale((a / k, b / k, c)).translate((0, 0, z0))
    g = g.trim_by_plane((0, 0, 1), 0.0)         # garde z >= 0
    return g.rotate((0, 0, ang_deg)).translate((x, y, 0))


def dans_stade(px, py, longueur, largeur):
    """Distance signée (positive = à l'intérieur) d'un point au bord d'un stade."""
    r = largeur / 2.0
    d = longueur / 2.0 - r
    cx = np.clip(px, -d, d)
    return r - np.hypot(px - cx, py)


def contour_ellipse(a, b, x, y, ang, n=48):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ex, ey = a * np.cos(t), b * np.sin(t)
    ca, sa = math.cos(ang), math.sin(ang)
    return np.c_[x + ex * ca - ey * sa, y + ex * sa + ey * ca]


def section_texte(miroir=True):
    """Contours du texte (police DejaVu Sans Bold, fournie avec matplotlib), centrés sur l'origine.
    miroir=True : texte inversé gauche/droite, tel qu'il doit être sur le moule pour être lisible
    sur la pièce démoulée (principe du tampon)."""
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    tp = TextPath((0, 0), TEXTE, size=TAILLE_TEXTE,
                  prop=FontProperties(family="DejaVu Sans", weight="bold"))
    bb = tp.get_extents()
    cx, cy = (bb.x0 + bb.x1) / 2, (bb.y0 + bb.y1) / 2
    contours = []
    for poly in tp.to_polygons():
        p = np.asarray(poly, dtype=np.float64) - [cx, cy]
        if miroir:
            p[:, 0] *= -1
        if len(p) >= 3:
            contours.append(p)
    return m.CrossSection(contours, m.FillRule.EvenOdd)


def solide_texte(z0, h, miroir=True):
    return m.Manifold.extrude(section_texte(miroir), h).translate((0, 0, z0))


def zone_texte():
    """Rectangle (xmin, ymin, xmax, ymax) réservé au texte sur la face galets."""
    b = section_texte().bounds()
    return (b[0] - MARGE_TEXTE, b[1] - MARGE_TEXTE, b[2] + MARGE_TEXTE, b[3] + MARGE_TEXTE)


def centre_dans_ellipse(qx, qy, a, b, x, y, ang):
    """Vrai si le point (qx, qy) est à l'intérieur de l'ellipse (a, b) centrée en (x, y)."""
    dx, dy = qx - x, qy - y
    ca, sa = math.cos(ang), math.sin(ang)
    u, v = dx * ca + dy * sa, -dx * sa + dy * ca
    return (u / a) ** 2 + (v / b) ** 2 < 1.0


# ---------------------------- nappe de galets --------------------------------
def generer_nappe():
    rng = random.Random(GRAINE)
    places = []     # (a, b, x, y, ang, contour, rayon_englobant)
    specs = []
    for n, amin, amax, rmin, rmax in FAMILLES:
        for _ in range(n):
            a = rng.uniform(amin, amax)
            specs.append((a, a * rng.uniform(rmin, rmax)))
    specs.sort(key=lambda s: -s[0] * s[1])     # les gros d'abord
    zt = zone_texte() if TEXTE_FACE_GALETS else None
    for a, b in specs:
        ok = False
        for _ in range(20000):
            x = rng.uniform(-L / 2, L / 2); y = rng.uniform(-W / 2, W / 2)
            ang = rng.uniform(0, math.pi)
            ct = contour_ellipse(a, b, x, y, ang)
            if dans_stade(ct[:, 0], ct[:, 1], L, W).min() < MARGE_BORD:
                continue
            if zt and np.any((ct[:, 0] > zt[0]) & (ct[:, 0] < zt[2]) & (ct[:, 1] > zt[1]) & (ct[:, 1] < zt[3])):
                continue
            renv = a + GAP
            clash = False
            for (pa, pb, px, py, pang, pct, pr) in places:
                if math.hypot(px - x, py - y) > renv + pr:
                    continue
                dmin = np.min(np.hypot(ct[:, None, 0] - pct[None, :, 0],
                                       ct[:, None, 1] - pct[None, :, 1]))
                if dmin < GAP or centre_dans_ellipse(x, y, pa, pb, px, py, pang) \
                        or centre_dans_ellipse(px, py, a, b, x, y, ang):
                    clash = True; break
            if not clash:
                places.append((a, b, x, y, ang, ct, a)); ok = True; break
        if not ok:
            print(f"  ! galet {a:.1f}x{b:.1f} non placé (nappe trop dense)")
    # contrôle : espacement réel minimum entre galets placés
    gmin = min(np.min(np.hypot(p[5][:, None, 0] - q[5][None, :, 0], p[5][:, None, 1] - q[5][None, :, 1]))
               for i, p in enumerate(places) for q in places[i + 1:])
    print(f"  espacement réel minimum entre galets : {gmin:.2f} mm")
    return [(a, b, x, y, math.degrees(ang)) for (a, b, x, y, ang, _, _) in places]


def hauteur_galet(a, b):
    return min(H_GALET, 1.4 * b)


# ------------------------------- géométrie -----------------------------------
def piece(nappe):
    plaque = prisme_stade(L, W, T_BASE)
    galets = [galet(a, b, hauteur_galet(a, b), x, y, ang).translate((0, 0, T_BASE - EPS))
              for (a, b, x, y, ang) in nappe]
    p = m.Manifold.batch_boolean([plaque] + galets, m.OpType.Add)
    if TEXTE_FACE_GALETS:   # gravé (lisible) dans la face galets
        p = p - solide_texte(T_BASE - H_TEXTE, H_TEXTE + 1.0, miroir=False)
    return p


def moule_base(nappe):
    bloc = prisme_stade(L + 2 * T_PAROI, W + 2 * T_PAROI, H_MOULE)
    # cavité de la plaque : du dessus des galets jusqu'au bord supérieur (ouvert), avec dépouille
    z_plaque = T_FOND + H_GALET
    cav_plaque = prisme_stade(L, W, T_BASE + 1.0, z0=z_plaque - EPS, evasement=DEPOUILLE)
    # cavités des galets : galets retournés, pointe vers le bas, sommet à z = T_FOND + H_GALET
    cav_galets = []
    for (a, b, x, y, ang) in nappe:
        h = hauteur_galet(a, b)
        g = galet(a, b, h, x, y, ang).mirror((0, 0, 1))          # occupe z in [-h, 0]
        # la pièce est retournée dans le moule : miroir en y pour conserver la nappe vue du dessus
        cav_galets.append(g.translate((0, 0, z_plaque + EPS)))
    return m.Manifold.batch_boolean([bloc.__class__.batch_boolean([bloc], m.OpType.Add),
                                     cav_plaque] + cav_galets, m.OpType.Subtract) \
        if False else bloc - m.Manifold.batch_boolean([cav_plaque] + cav_galets, m.OpType.Add)


def moule_base_marque(nappe):
    base = moule_base(nappe)
    if TEXTE_FACE_GALETS:   # lettres en relief sur le plancher, en miroir => gravées et lisibles sur la pièce
        base = base + solide_texte(T_FOND + H_GALET - EPS, H_TEXTE + EPS, miroir=True)
    return base


def trou(d, x, y, h):
    return m.Manifold.cylinder(h, d / 2.0).translate((x, y, -1.0))


def couvercle(noyau=False):
    Lo, Wo = L + 2 * T_PAROI, W + 2 * T_PAROI                # extérieur du moule
    Li, Wi = Lo + 2 * JEU_JUPE, Wo + 2 * JEU_JUPE            # intérieur de la jupe
    Le, We = Li + 2 * T_JUPE, Wi + 2 * T_JUPE                # extérieur du couvercle
    # z = 0 : face extérieure (posée sur le plateau d'impression) ; z = T_COUV : face côté silicone
    plaque = prisme_stade(Le, We, T_COUV)
    jupe = prisme_stade(Le, We, H_JUPE, z0=T_COUV - EPS) - prisme_stade(Li, Wi, H_JUPE + 2, z0=T_COUV - 1)
    corps = plaque + jupe
    if noyau:
        Ln, Wn = L - 2 * MARGE_NOYAU, W - 2 * MARGE_NOYAU
        boss = prisme_stade(Ln, Wn, P_NOYAU, z0=T_COUV - EPS, evasement=-0.8)   # flancs en dépouille
        corps = corps + boss
    if TEXTE_SUR_COUVERCLE:
        z_face = T_COUV + (P_NOYAU if noyau else 0.0)
        corps = corps + solide_texte(z_face - EPS, H_TEXTE + EPS, miroir=True)
    htot = T_COUV + H_JUPE + 4
    x_coulee = -(L / 2 - 14.0)
    x_event = (L / 2 - 4.5)
    coulee = trou(D_COULEE, x_coulee, 0, htot)
    entonnoir = m.Manifold.cylinder(T_COUV - 0.5, D_ENTONNOIR / 2.0, D_COULEE / 2.0).translate((x_coulee, 0, -EPS))
    events = [trou(D_EVENT, x_event, 0, htot),
              trou(D_EVENT, L / 4, W / 2 - 4.5, htot),
              trou(D_EVENT, L / 4, -(W / 2 - 4.5), htot)]
    return corps - m.Manifold.batch_boolean([coulee, entonnoir] + events, m.OpType.Add)


# -------------------------------- export -------------------------------------
def exporter(man, nom):
    mesh = man.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3].astype(np.float64)
    f = np.asarray(mesh.tri_verts).astype(np.int64)
    tm = trimesh.Trimesh(vertices=v, faces=f, process=False)
    assert tm.is_watertight, f"{nom} : maillage non étanche"
    chemin = os.path.join(STL, nom)
    tm.export(chemin)
    bb = tm.bounds
    print(f"  {nom:28s} {len(f):7d} tri  volume {tm.volume/1000:6.1f} cm³  "
          f"encombrement {bb[1][0]-bb[0][0]:.1f} x {bb[1][1]-bb[0][1]:.1f} x {bb[1][2]-bb[0][2]:.1f} mm")
    return tm


def plan_nappe(nappe, piece_tm):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Ellipse
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ct = contour_ellipse(1, 1, 0, 0, 0, 1)  # dummy
    # contour du stade
    t = np.linspace(0, 2 * np.pi, 200)
    r, d = W / 2, L / 2 - W / 2
    xs = np.where(np.cos(t) >= 0, d, -d) + r * np.cos(t); ys = r * np.sin(t)
    ax.fill(xs, ys, color="#f6b8b0", zorder=1); ax.plot(xs, ys, color="#8c3b3b", lw=1.5)
    for (a, b, x, y, ang) in nappe:
        ax.add_patch(Ellipse((x, y), 2 * a, 2 * b, angle=ang, facecolor="#fde3df",
                             edgecolor="#8c3b3b", lw=0.8, zorder=2))
    ax.set_aspect("equal"); ax.set_xlim(-L / 2 - 8, L / 2 + 8); ax.set_ylim(-W / 2 - 10, W / 2 + 10)
    ax.set_xlabel("mm"); ax.set_ylabel("mm")
    ax.set_title(f"Plan de la nappe – {len(nappe)} galets – pièce {L:.0f} x {W:.0f} mm, "
                 f"plaque {T_BASE:.0f} mm + galets {H_GALET:.0f} mm – graine {GRAINE}")
    ax.annotate("", (-L / 2, -W / 2 - 6), (L / 2, -W / 2 - 6), arrowprops=dict(arrowstyle="<->"))
    ax.text(0, -W / 2 - 8.5, f"{L:.0f} mm", ha="center", va="top")
    ax.annotate("", (L / 2 + 5, -W / 2), (L / 2 + 5, W / 2), arrowprops=dict(arrowstyle="<->"))
    ax.text(L / 2 + 6.5, 0, f"{W:.0f} mm", ha="left", va="center", rotation=90)
    ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(os.path.join(APERCU, "plan_nappe.png"), dpi=150); plt.close(fig)


def rendu_3d(tm, nom, titre, elev=35, azim=-50, px=1100):
    """Rendu orthographique avec tampon de profondeur (sans OpenGL) pour visualiser sans logiciel 3D."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    V = np.asarray(tm.vertices, dtype=np.float64); F = np.asarray(tm.faces)
    ea, az = math.radians(elev), math.radians(azim)
    Rz = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, math.cos(ea), -math.sin(ea)], [0, math.sin(ea), math.cos(ea)]])
    P = (V - V.mean(axis=0)) @ Rz.T @ Rx.T          # x,y écran ; z = profondeur (vers l'observateur)
    tri = P[F]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    light = np.array([-0.3, 0.5, 0.8]); light /= np.linalg.norm(light)
    shade = 0.30 + 0.70 * np.clip(n @ light, 0, 1)
    xmin, ymin = P[:, :2].min(axis=0); xmax, ymax = P[:, :2].max(axis=0)
    s = (px - 40) / max(xmax - xmin, ymax - ymin)
    Wd = int((xmax - xmin) * s) + 40; Hd = int((ymax - ymin) * s) + 40
    sx = (tri[:, :, 0] - xmin) * s + 20; sy = (ymax - tri[:, :, 1]) * s + 20; sz = tri[:, :, 2]
    zbuf = np.full((Hd, Wd), -np.inf); img = np.ones((Hd, Wd, 3))
    base = np.array([0.97, 0.66, 0.62])
    for i in range(len(F)):
        x0, x1 = int(np.floor(sx[i].min())), int(np.ceil(sx[i].max()))
        y0, y1 = int(np.floor(sy[i].min())), int(np.ceil(sy[i].max()))
        if x1 < x0 or y1 < y0:
            continue
        xs = np.arange(x0, x1 + 1) + 0.5; ys = np.arange(y0, y1 + 1) + 0.5
        gx, gy = np.meshgrid(xs, ys)
        ax_, bx_, cx_ = sx[i]; ay_, by_, cy_ = sy[i]
        det = (bx_ - ax_) * (cy_ - ay_) - (cx_ - ax_) * (by_ - ay_)
        if abs(det) < 1e-9:
            continue
        l1 = ((bx_ - gx) * (cy_ - gy) - (cx_ - gx) * (by_ - gy)) / det
        l2 = ((cx_ - gx) * (ay_ - gy) - (ax_ - gx) * (cy_ - gy)) / det
        l3 = 1 - l1 - l2
        inside = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        if not inside.any():
            continue
        z = l1 * sz[i][0] + l2 * sz[i][1] + l3 * sz[i][2]
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        upd = inside & (z > sub)
        sub[upd] = z[upd]
        img[y0:y1 + 1, x0:x1 + 1][upd] = base * shade[i]
    fig, ax = plt.subplots(figsize=(Wd / 110, Hd / 110 + 0.5))
    ax.imshow(img); ax.set_axis_off(); ax.set_title(titre)
    fig.tight_layout(); fig.savefig(os.path.join(APERCU, nom), dpi=110); plt.close(fig)


def coupes(nappe, base_man, couv_man, piece_man):
    """Coupes longitudinale (y=0) et transversale (x=0) du moule assemblé avec le silicone."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    # assemblage dans le repère du moule : couvercle retourné posé sur le bord supérieur
    couv_ass = couv_man.mirror((0, 0, 1)).translate((0, 0, H_MOULE + T_COUV))
    sil_ass = piece_man.mirror((0, 0, 1)).translate((0, 0, H_MOULE)) - couv_ass   # silicone réel (moins le noyau)
    fig, axes = plt.subplots(2, 1, figsize=(12, 7.5), gridspec_kw={"height_ratios": [1, 1]})
    for ax, (axe, titre) in zip(axes, [("y", "Coupe longitudinale (plan y = 0)"),
                                        ("x", "Coupe transversale (plan x = 0)")]):
        for man, col, lab in [(base_man, "#c9a27e", "moule base (imprimé)"),
                              (couv_ass, "#8fb3c9", "couvercle (imprimé)"),
                              (sil_ass, "#f29a8e", "silicone")]:
            # amener le plan de coupe sur z = 0 (rotation de 90° autour de x) puis trancher.
            # Après rotation, le polygone obtenu est exprimé en (x, -z) : on remet z vers le haut.
            r = man if axe == "y" else man.rotate((0, 0, 90))      # x = 0 -> y' = 0
            cs = r.rotate((90, 0, 0)).slice(0.0)
            for poly in cs.to_polygons():
                pts = np.asarray(poly) * np.array([1.0 if axe == "y" else -1.0, -1.0])
                ax.add_patch(Polygon(pts, closed=True, facecolor=col, edgecolor="k", lw=0.5, alpha=0.9))
        ax.set_aspect("equal"); ax.autoscale_view()
        ax.set_xlim(-(L / 2 + 12), L / 2 + 12) if axe == "y" else ax.set_xlim(-(W / 2 + 12), W / 2 + 12)
        ax.set_ylim(-2, H_MOULE + T_COUV + 3)
        ax.set_title(titre); ax.grid(alpha=0.25); ax.set_xlabel("mm"); ax.set_ylabel("mm")
    from matplotlib.patches import Patch
    axes[0].legend(handles=[Patch(color="#c9a27e", label="moule base (imprimé)"),
                            Patch(color="#8fb3c9", label="couvercle à noyau (imprimé)"),
                            Patch(color="#f29a8e", label="silicone")], loc="upper right", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(APERCU, "coupes_assemblage.png"), dpi=140); plt.close(fig)


if __name__ == "__main__":
    print("Nappe de galets…")
    nappe = generer_nappe()
    print(f"  {len(nappe)} galets placés, gap mini {GAP} mm, marge bord {MARGE_BORD} mm")
    print("Géométrie et export STL…")
    man_piece, man_base, man_cp, man_cn = piece(nappe), moule_base_marque(nappe), couvercle(False), couvercle(True)
    p = exporter(man_piece, "piece_reference.stl")
    base = exporter(man_base, "moule_base.stl")
    cp = exporter(man_cp, "moule_couvercle_plat.stl")
    cn = exporter(man_cn, "moule_couvercle_noyau.stl")

    v_piece = p.volume / 1000.0
    v_orig = v_piece + (8.0 - T_BASE) * stade(L, W).area() / 1000.0
    Ln, Wn = L - 2 * MARGE_NOYAU, W - 2 * MARGE_NOYAU
    v_noyau = v_piece - P_NOYAU * stade(Ln, Wn).area() / 1000.0
    print("\nBilan silicone (densité %.2f g/cm³) :" % DENSITE_SILICONE)
    for nom, v in [("original estimé (plaque 8 mm)", v_orig),
                   (f"nouveau moule (plaque {T_BASE:.0f} mm)", v_piece),
                   ("avec couvercle à noyau", v_noyau)]:
        print(f"  {nom:36s} {v:5.1f} cm³  ≈ {v*DENSITE_SILICONE:5.1f} g")

    print("Aperçus…")
    plan_nappe(nappe, p)
    rendu_3d(p, "piece_reference.png", "Pièce en silicone attendue (face galets)")
    rendu_3d(base, "moule_base.png", "Moule base – cavité vue du dessus", elev=55, azim=-35)
    rendu_3d(cn, "couvercle_noyau.png", "Couvercle à noyau – face côté silicone (jupe, noyau, coulée, évents)", elev=55, azim=-35)
    rendu_3d(cp, "couvercle_plat_dessus.png", "Couvercle plat vu du dessus (côté silicone) : texte en miroir sur le moule", elev=20, azim=0)
    coupes(nappe, man_base, man_cn, man_piece)
    print("Terminé.")
