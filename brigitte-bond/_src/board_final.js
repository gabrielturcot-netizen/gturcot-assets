const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const V = path.join(__dirname, 'final', 'svg');
const r = f => fs.readFileSync(path.join(V, 'bb_' + f + '.svg'), 'utf8');
const img = (f, s) => `<img width="${s}" height="${s}" src="data:image/svg+xml;base64,${Buffer.from(r(f)).toString('base64')}">`;
const K = '#231F20';
const sw = (c, n, cmyk, hex) => `<tr><td><span class="sw" style="background:${c}"></span>${n}</td><td>${cmyk}</td><td>${hex}</td></tr>`;
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}body{margin:0;background:#F4F2EE;font-family:Inter,sans-serif;color:${K}}
.wrap{width:1500px;padding:56px 60px 48px}
h1{font-size:34px;margin:0 0 6px;font-weight:700;letter-spacing:-.01em}
h2{font-size:22px;margin:40px 0 14px;font-weight:700}
.sub{color:#6D6E71;font-size:17px;line-height:1.45}
.grid{display:grid;gap:18px}.g2{grid-template-columns:1fr 1fr}.g3{grid-template-columns:repeat(3,1fr)}.g4{grid-template-columns:repeat(4,1fr)}
.cell{background:#fff;border-radius:10px;padding:20px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px}
.cell.dark{background:${K}}.cell svg{max-width:100%;height:auto;display:block}
.cap{font-size:13px;color:#6D6E71;align-self:flex-start}.dark .cap{color:#B1B3B6}
.hero{padding:56px}.hero svg{width:860px}
.row{display:flex;gap:26px;align-items:center}
.c{width:120px;height:120px;border-radius:50%;overflow:hidden;box-shadow:0 0 0 1px #ddd}.c img{display:block}
.card{width:350px;height:200px;border-radius:6px;box-shadow:0 6px 18px rgba(0,0,0,.12),0 0 0 1px #e5e2dd;display:flex;align-items:center;justify-content:center;position:relative}
.card.back{background:${K}}
.card .info{position:absolute;left:22px;bottom:16px;font-size:8.5px;line-height:1.5;color:#6D6E71}
table{border-collapse:collapse;width:100%;font-size:15px;background:#fff;border-radius:10px;overflow:hidden}
td,th{padding:10px 14px;text-align:left;border-bottom:1px solid #eee}th{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#6D6E71}
.sw{display:inline-block;width:18px;height:18px;border-radius:4px;vertical-align:-4px;margin-right:8px;box-shadow:0 0 0 1px #ccc}
</style></head><body><div class="wrap">
<h1>Brigitte Bond — identité visuelle</h1>
<div class="sub">Direction « Deux encres » : deux B, cyan et magenta, dont la superposition crée une troisième couleur, comme sur une presse.</div>
<div class="grid" style="margin-top:26px"><div class="cell hero">${r('horizontal_couleur')}<div class="cap">Logo principal · horizontal couleur</div></div></div>
<div class="grid g2" style="margin-top:18px">
<div class="cell">${r('horizontal_noir')}<div class="cap">Une encre (tampon, gravure, facture noir et blanc)</div></div>
<div class="cell dark">${r('horizontal_inverse')}<div class="cap">Fond foncé</div></div></div>
<div class="grid g4" style="margin-top:18px">
<div class="cell">${r('vertical_couleur')}<div class="cap">Vertical · couleur</div></div>
<div class="cell">${r('vertical_noir')}<div class="cap">Vertical · une encre</div></div>
<div class="cell dark">${r('vertical_inverse')}<div class="cap">Vertical · fond foncé</div></div>
<div class="cell">${r('horizontal-compact_couleur')}<div class="cap">Compact sans slogan (petits formats)</div></div></div>

<h2>Icône, réseaux sociaux et site web</h2>
<div class="grid g2">
<div class="cell"><div class="row"><div class="c">${img('avatar-rond_couleur',120)}</div><div class="c">${img('avatar-rond_inverse',120)}</div><div class="c">${img('avatar-rond_noir-plein',120)}</div></div><div class="cap">Photo de profil (Facebook, Instagram, Google) · recadrage rond sans coupure</div></div>
<div class="cell"><div class="row">${img('favicon_couleur',64)}${img('favicon_couleur',32)}${img('favicon_couleur',16)}<span style="width:20px"></span>${img('favicon_inverse',64)}${img('favicon_inverse',32)}${img('favicon_inverse',16)}</div><div class="cap">Favicon (onglet du navigateur) à 64, 32 et 16 px</div></div></div>

<h2>Exemple : carte d’affaires (3,5 × 2 po, recto et verso)</h2>
<div class="grid g2"><div class="cell" style="padding:34px"><div class="row" style="gap:34px">
<div class="card"><div style="width:250px">${r('vertical_couleur')}</div></div>
<div class="card back"><div style="width:130px">${r('symbole_inverse')}</div></div></div></div>
<div class="cell" style="align-items:flex-start;justify-content:flex-start"><div class="sub" style="font-size:15px">
<b style="color:${K}">Deux versions une encre</b><br>Le logo une encre principal montre un B en contour et un B plein. Sous 25 mm (petit tampon, stylo, broderie), on utilise la variante « pleine », où la zone commune devient blanche :</div>
<div class="row" style="margin-top:12px"><div style="width:150px">${r('symbole_noir')}</div><div style="width:150px">${r('symbole_noir-plein')}</div></div></div></div>

<h2>Règles d’utilisation</h2>
<div class="grid g2">
<table><tr><th>Version</th><th>Taille minimale</th></tr>
<tr><td>Horizontal avec slogan</td><td>58 mm de large (slogan ≥ 6 pt)</td></tr>
<tr><td>Vertical avec slogan</td><td>41 mm de large</td></tr>
<tr><td>Compact sans slogan</td><td>en dessous de ces tailles</td></tr>
<tr><td>Symbole seul · une encre « contour »</td><td>25 mm · sinon variante pleine</td></tr>
<tr><td>Icône</td><td>16 px (favicon) · 8 mm imprimé</td></tr>
<tr><td>Zone de protection</td><td>½ largeur d’un B, tout autour</td></tr></table>
<table><tr><th>Couleur</th><th>CMJN</th><th>Écran</th></tr>
${sw('#00AEEF','Cyan','C100','#00AEEF')}${sw('#EC008C','Magenta','M100','#EC008C')}${sw('#2E3192','Superposition','C100 M100','#2E3192')}
${sw('#231F20','Noir','N100','#231F20')}${sw('#6D6E71','Gris slogan','N70','#6D6E71')}${sw('#B1B3B6','Gris slogan (fond foncé)','N35','#B1B3B6')}${sw('#ECAEF8','Lavande (fond foncé)','C8 M32','#ECAEF8')}</table></div>
<div class="sub" style="margin-top:16px;font-size:14px">Polices : DM Serif Display (nom) et Jost (slogan), licence SIL OFL, usage commercial gratuit. Le texte est vectorisé dans tous les fichiers : aucune police à installer.</div>
</div></body></html>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1500, height: 900 }, deviceScaleFactor: 2 });
  await p.setContent(html); await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(__dirname, 'final', 'planche_identite.png'), fullPage: true });
  await b.close();
})();
