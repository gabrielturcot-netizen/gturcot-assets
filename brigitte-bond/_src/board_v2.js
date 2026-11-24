const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const V = path.join(__dirname, 'v2');
const r = f => fs.readFileSync(path.join(V, f + '.svg'), 'utf8');
const K = '#231F20';
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}body{margin:0;background:#F4F2EE;font-family:Inter,sans-serif;color:${K}}
.wrap{width:1500px;padding:56px 60px 48px}
h1{font-size:34px;margin:0 0 6px;font-weight:700;letter-spacing:-.01em}
h2{font-size:22px;margin:44px 0 6px;font-weight:700}
.sub{color:#6D6E71;font-size:17px;margin-bottom:22px;line-height:1.45}
.tag{display:inline-block;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:4px 10px;border-radius:99px;background:${K};color:#fff;margin-left:10px;vertical-align:middle}
.grid{display:grid;gap:18px}
.g1{grid-template-columns:1fr}.g2{grid-template-columns:1fr 1fr}.g3{grid-template-columns:1fr 1fr 1fr}.g4{grid-template-columns:repeat(4,1fr)}
.cell{background:#fff;border-radius:10px;padding:18px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;min-height:120px}
.cell.dark{background:${K}}
.cell svg{max-width:100%;height:auto;display:block}
.cap{font-size:13px;color:#6D6E71;align-self:flex-start}
.dark .cap{color:#B1B3B6}
.hero svg{width:900px}
.av{display:flex;gap:26px;align-items:end}
.av .c{width:120px;height:120px;border-radius:50%;overflow:hidden;box-shadow:0 0 0 1px #ddd}
.av .c svg{width:120px;height:120px}
.fav{display:flex;gap:10px;align-items:center}
.fav img{image-rendering:auto}
table{border-collapse:collapse;width:100%;font-size:15px;background:#fff;border-radius:10px;overflow:hidden}
td,th{padding:10px 14px;text-align:left;border-bottom:1px solid #eee}th{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#6D6E71}
.sw{display:inline-block;width:18px;height:18px;border-radius:4px;vertical-align:-4px;margin-right:8px;box-shadow:0 0 0 1px #ccc}
</style></head><body><div class="wrap">
<h1>Brigitte Bond — logo v2</h1>
<div class="sub">Corrections issues de la critique : slogan agrandi et justifié, versions une encre et fond foncé dédiées, version verticale, version compacte sans slogan.</div>

<h2>C · Papier Bond <span class="tag">Recommandé</span></h2>
<div class="sub">Le « bond » est le papier d’impression standard : une feuille cornée, un B et la barre de contrôle couleur (cyan, magenta, jaune, blanc papier).</div>
<div class="grid g1"><div class="cell hero">${r('C_papier-bond/horizontal_couleur')}<div class="cap">Horizontal · couleur (principal)</div></div></div>
<div class="grid g2" style="margin-top:18px">
<div class="cell">${r('C_papier-bond/horizontal_noir')}<div class="cap">Une encre (tampon, gravure, télécopie, facture N&amp;B)</div></div>
<div class="cell dark">${r('C_papier-bond/horizontal_inverse')}<div class="cap">Fond foncé</div></div></div>
<div class="grid g4" style="margin-top:18px">
<div class="cell">${r('C_papier-bond/vertical_couleur')}<div class="cap">Vertical · couleur</div></div>
<div class="cell">${r('C_papier-bond/vertical_noir')}<div class="cap">Vertical · une encre</div></div>
<div class="cell dark">${r('C_papier-bond/vertical_inverse')}<div class="cap">Vertical · fond foncé</div></div>
<div class="cell">${r('C_papier-bond/compact-sans-slogan_couleur')}<div class="cap">Compact sans slogan (petits formats)</div></div></div>
<div class="grid g2" style="margin-top:18px">
<div class="cell"><div class="av"><div class="c">${r('C_papier-bond/icone_couleur')}</div><div class="c">${r('C_papier-bond/icone_inverse')}</div><div class="c">${r('C_papier-bond/icone_noir')}</div></div><div class="cap">Icône · aperçu avatar rond (Facebook, Instagram)</div></div>
<div class="cell"><div class="fav">${['couleur','inverse'].map(m=>`<img width="64" height="64" src="data:image/svg+xml;base64,${Buffer.from(r('C_papier-bond/icone_'+m)).toString('base64')}"><img width="32" height="32" src="data:image/svg+xml;base64,${Buffer.from(r('C_papier-bond/icone_'+m)).toString('base64')}"><img width="16" height="16" src="data:image/svg+xml;base64,${Buffer.from(r('C_papier-bond/icone_'+m)).toString('base64')}">`).join('<span style="width:24px"></span>')}</div><div class="cap">Icône à 64, 32 et 16 px (favicon)</div></div></div>

<h2>A · Deux encres <span class="tag" style="background:#6D6E71">Alternative</span></h2>
<div class="grid g3">
<div class="cell">${r('A_deux-encres/horizontal_couleur')}<div class="cap">Couleur</div></div>
<div class="cell">${r('A_deux-encres/horizontal_noir')}<div class="cap">Une encre : un B en contour, un B plein</div></div>
<div class="cell dark">${r('A_deux-encres/horizontal_inverse')}<div class="cap">Fond foncé : superposition « lumière »</div></div></div>

<h2>Règles d’utilisation</h2>
<div class="grid g2">
<table><tr><th>Version</th><th>Taille minimale</th></tr>
<tr><td>Horizontale avec slogan</td><td>58 mm de large (slogan ≥ 6 pt)</td></tr>
<tr><td>Verticale avec slogan</td><td>44 mm de large</td></tr>
<tr><td>Compacte sans slogan</td><td>en dessous de ces tailles</td></tr>
<tr><td>Icône seule</td><td>8 mm · 32 px écran</td></tr>
<tr><td>Zone de protection</td><td>hauteur du « B » de la feuille, tout autour</td></tr></table>
<table><tr><th>Couleur</th><th>CMJN</th><th>Écran</th></tr>
<tr><td><span class="sw" style="background:#00AEEF"></span>Cyan</td><td>C100</td><td>#00AEEF</td></tr>
<tr><td><span class="sw" style="background:#EC008C"></span>Magenta</td><td>M100</td><td>#EC008C</td></tr>
<tr><td><span class="sw" style="background:#FFF200"></span>Jaune</td><td>J100</td><td>#FFF200</td></tr>
<tr><td><span class="sw" style="background:#231F20"></span>Noir</td><td>N100</td><td>#231F20</td></tr>
<tr><td><span class="sw" style="background:#6D6E71"></span>Gris slogan</td><td>N70</td><td>#6D6E71</td></tr>
<tr><td><span class="sw" style="background:#B1B3B6"></span>Gris slogan (fond foncé)</td><td>N35</td><td>#B1B3B6</td></tr></table></div>
<div class="sub" style="margin-top:16px;font-size:14px">Polices : Fraunces (nom), Jost (slogan), DM Serif Display (piste A) — licence SIL OFL, usage commercial gratuit. Texte vectorisé dans tous les fichiers.</div>
</div></body></html>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1500, height: 900 }, deviceScaleFactor: 2 });
  await p.setContent(html); await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(V, 'planche_v2.png'), fullPage: true });
  await b.close();
})();
