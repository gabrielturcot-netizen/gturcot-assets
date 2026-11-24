// Usage: node render.js out.png width bg file.svg   (bg: transparent | #hex)
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [out, width, bg, svgFile] = process.argv.slice(2);
  const svg = fs.readFileSync(svgFile, 'utf8');
  const m = svg.match(/viewBox="([\d.\s-]+)"/); const [, , vw, vh] = m[1].trim().split(/\s+/).map(Number);
  const w = Number(width), h = Math.round(w * vh / vw);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  const b64 = Buffer.from(svg).toString('base64');
  await page.setContent(`<html><body style="margin:0;background:${bg === 'transparent' ? 'transparent' : bg}"><img src="data:image/svg+xml;base64,${b64}" style="display:block;width:${w}px;height:${h}px"></body></html>`);
  await page.waitForTimeout(100);
  await page.screenshot({ path: out, omitBackground: bg === 'transparent', clip: { x: 0, y: 0, width: w, height: h } });
  await browser.close();
})();
