// Deterministic 10 s take of the Dikilitas app: virtual clock, one screenshot per 1/60 s.
import puppeteer from 'puppeteer-core'; import fs from 'fs';
const FPS = 60, DUR = 10, DSF = +(process.env.DSF || 2), OUT = process.env.OUT || 'frames';
fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT);
const b = await puppeteer.launch({ executablePath: process.env.CHROMIUM || '/usr/bin/chromium', headless: 'new', args: ['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-smooth-scrolling','--hide-scrollbars'] });
const p = await b.newPage(); await p.setViewport({ width: 1280, height: 800, deviceScaleFactor: DSF });
await p.evaluateOnNewDocument(fs.readFileSync('vclock.js', 'utf8'));
p.on('console', m => { if (m.type() === 'error') console.log('page error:', m.text()); });
await p.goto('http://localhost:8080/?lang=en', { waitUntil: 'networkidle0' });
const step = n => p.evaluate(n => { for (let i = 0; i < n; i++) window.__step(1000 / 60); }, n);
for (let i = 0; i < 40; i++) { await step(6); if (!(await p.$('#loader'))) break; await new Promise(r => setTimeout(r, 100)); }
await new Promise(r => setTimeout(r, 1500));   // fonts and textures
await step(30);
// park the real mouse away from everything
await p.mouse.move(1000, 760);
const SHAFT = [345, 300], READ = [985, 470], BASE = [1047, 49];
const ev = {}; let SEE = null;
const F = t => Math.round(t * FPS);
const at = {
  [F(1.9)]: async () => { await p.mouse.move(...SHAFT, { steps: 4 }); },
  [F(2.5)]: async () => { ev.click_shaft = 2.5; await p.mouse.down(); await p.mouse.up(); },
  [F(3.45)]: async () => { SEE = await p.evaluate(() => { const b = document.querySelector('#readBody .p.on .see').getBoundingClientRect(); return [Math.round(b.x + 14), Math.round(b.y + b.height / 2)]; }); },
  [F(4.1)]: async () => { await p.mouse.move(...SEE, { steps: 4 }); },
  [F(4.25)]: async () => { ev.click_see = 4.25; await p.mouse.down(); await p.mouse.up(); },
  [F(5.5)]: async () => { await p.mouse.move(...READ, { steps: 4 }); },
  [F(5.55)]: async () => { await p.mouse.wheel({ deltaY: 2 }); },
  [F(8.2)]: async () => { await p.mouse.move(...BASE, { steps: 4 }); },
  [F(8.35)]: async () => { ev.click_base = 8.35; await p.mouse.down(); await p.mouse.up(); },
};
const S0 = 5.7, S1 = 7.6, DIST = 700; let sFrom = null;
const t0 = Date.now();
for (let i = 0; i < FPS * DUR; i++) {
  const t = i / FPS;
  if (at[i]) await at[i]();
  if (t >= S0 && t <= S1 + 1e-6) {
    if (sFrom === null) sFrom = await p.evaluate(() => document.getElementById('rs').scrollTop);
    const u = (t - S0) / (S1 - S0), e = u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
    await p.evaluate(y => { document.getElementById('rs').scrollTop = y; }, sFrom + DIST * e);
  }
  await step(1);
  await p.screenshot({ path: `${OUT}/f${String(i).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 93 });
  if (i % 30 === 0) console.log(`frame ${i} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
fs.writeFileSync('take.json', JSON.stringify({ ev, SHAFT, READ, BASE, SEE }, null, 1));
await b.close(); console.log('done');
