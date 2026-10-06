// Builds data.js from runes.json (runes, line by line) and texts.json (transcription, translations, notes).
// `node scripts/gen-data.mjs --fetch` first refreshes runes.json from the Wikisource edition.
import { readFileSync, writeFileSync } from 'node:fs';
const dir = new URL('..', import.meta.url).pathname;
if (process.argv.includes('--fetch')){
  const url = 'https://tr.wikisource.org/w/index.php?action=raw&title=' + encodeURIComponent('Orhun Yazıtları (Kül Tigin)');
  const wiki = await (await fetch(url, { headers: { 'User-Agent': 'kultigin-732 (github.com/CahidArda/obelisk-390)' } })).text();
  const out = [];
  for (const row of wiki.split(/\n\|-\s*\n/)){
    const cells = row.split('\n').filter(l => l.startsWith('|') && !l.startsWith('|+') && !l.startsWith('|}'))
      .map(l => l.replace(/^\|\s?/, '').replace(/^style="[^"]*"\s*\|\s*/, ''));
    const i = cells.findIndex(c => /^(G|D|K|KD|GD|GB|B)\d+\s*$/.test(c.trim()));
    if (i < 0) continue;
    const c = cells.slice(i);
    out.push({ id: c[0].trim(), code: c[1].trim(), runes: c[2].trim(), lit: c[3].trim(), tc: c[4].trim(), tr: (c[5] || '').trim() });
  }
  writeFileSync(dir + 'runes.json', JSON.stringify(out, null, 1));
  console.log('runes.json:', out.length, 'lines');
}
const runes = JSON.parse(readFileSync(dir + 'runes.json', 'utf8'));
const texts = JSON.parse(readFileSync(dir + 'texts.json', 'utf8'));
const lines = {};
for (const r of runes) lines[r.id] = { runes: r.runes, ...texts[r.id] };
const missing = Object.keys(lines).filter(k => !lines[k].en);
if (missing.length) throw new Error('No translation for ' + missing.join(', '));
writeFileSync(dir + 'data.js', 'window.KT = ' + JSON.stringify({ lines }, null, 1) + ';\n');
console.log('data.js:', Object.keys(lines).length, 'lines');
