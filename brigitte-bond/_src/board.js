const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const out = path.join(__dirname, 'out');
const read = f => fs.readFileSync(path.join(out, f), 'utf8');
const rows = [
  ['A', 'Deux encres', 'deux-encres', 'Deux « B » (Brigitte Bond) imprimés en cyan et magenta ; leur chevauchement crée une 3ᵉ couleur, comme une surimpression sur presse.'],
  ['B', 'Repère', 'repere', 'Le « o » de Bond devient une croix de repérage — le symbole que tout imprimeur reconnaît.'],
  ['C', 'Papier Bond', 'papier-bond', 'Clin d’œil au papier « bond », le papier d’impression standard : une feuille cornée et la barre de contrôle couleur.'],
  ['D', 'Trame', 'trame', 'Un « B » formé de points de trame (demi-teinte), la technique qui reproduit les dégradés à l’impression.'],
];
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;background:#F4F2EE;font-family:Inter,sans-serif;color:#231F20}
.wrap{width:1500px;padding:56px 60px 40px}
h1{font-size:34px;margin:0 0 6px;font-weight:700;letter-spacing:-.01em}
.sub{color:#6D6E71;font-size:17px;margin-bottom:34px}
.row{display:grid;grid-template-columns:1fr 250px;gap:22px;margin-bottom:22px}
.card{background:#fff;border-radius:10px;padding:22px 28px;display:flex;flex-direction:column}
.lbl{font-size:14px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#6D6E71}
.lbl b{color:#231F20;margin-right:8px}
.desc{font-size:15px;color:#555;margin-top:4px;line-height:1.4}
.logo{flex:1;display:flex;align-items:center;justify-content:center;padding-top:6px}
.logo svg{width:760px;height:auto}
.ic{display:flex;align-items:center;justify-content:center;background:#fff;border-radius:10px}
.ic svg{width:210px;height:210px;border-radius:16px;box-shadow:0 0 0 1px #e4e1dc}
.foot{color:#8a8a8a;font-size:13px;margin-top:10px}
</style></head><body><div class="wrap">
<h1>Brigitte Bond — pistes de logo</h1>
<div class="sub">4 concepts · version horizontale + icône (réseaux sociaux, favicon, tampon)</div>
${rows.map(([k, t, f, d]) => `<div class="row"><div class="card"><div class="lbl"><b>${k}</b>${t}</div><div class="desc">${d}</div>
<div class="logo">${read(`${k}_${f}_horizontal.svg`)}</div></div>
<div class="ic">${read(`${k}_${f}_icone.svg`)}</div></div>`).join('')}
<div class="foot">Couleurs : encres process CMJN (cyan, magenta, jaune) + noir riche. Fichiers vectoriels SVG, texte vectorisé.</div>
</div></body></html>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1500, height: 800 }, deviceScaleFactor: 2 });
  await p.setContent(html); await p.waitForTimeout(200);
  await p.screenshot({ path: path.join(out, 'planche_concepts.png'), fullPage: true });
  await b.close();
})();
