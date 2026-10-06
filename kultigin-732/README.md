# kultigin-732

An interactive, print-style reading of the **Kül Tigin stele** (Orkhon inscriptions, A.D. 732), built on the obelisk-390 app. A rotatable 3D stele sits next to a reading page that gives every line in Old Turkic runes, transcription, English and Turkish.

- **Model**: an eight-sided stele (four faces, four narrow corner edges) on its tortoise base, under a dragon crown. Each line of runes is a vertical column, read top to bottom and right to left. Hover or tap a column to read it; drag to turn, zoom to read the stone.
- **Read**: one section per face (South, East, North), the corner edges, the West face, and the crown and tortoise. On wide screens the model follows what you read; **See it** takes the model to a line.
- **Languages**: English and Türkçe.

## Running it

No build step. Serve this folder with any static server, e.g. `node ../server.js` from here or `python3 -m http.server`.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole app: layout, 3D model, reading page, interaction |
| `runes.json` | The 70 lines from the Wikisource edition: runes, transliteration, transcription, Turkish |
| `texts.json` | Normalized transcription, English and Turkish translations and notes, keyed by line (G1…G13, D1…D40, K1…K13, KD1, GD1, GB1, B1) |
| `data.js` | Generated from the two files above by `scripts/gen-data.mjs` |
| `i18n.js` | Interface strings (en, tr) |
| `scripts/gen-data.mjs` | Rebuilds `data.js`; `--fetch` first refreshes `runes.json` from Wikisource |

## Sources and caveats

- Runes and line division from the Wikisource edition [Orhun Yazıtları (Kül Tigin)](https://tr.wikisource.org/wiki/Orhun_Yaz%C4%B1tlar%C4%B1_(K%C3%BCl_Tigin)), CC BY-SA 4.0, re-typeset in Noto Sans Old Turkic. Transcription normalized after T. Tekin, *Orhon Yazıtları* (1988, 1995).
- The English and Turkish translations are new, line by line; readings of damaged passages follow Tekin. They have not been reviewed yet.
- The Chinese inscription of Emperor Xuanzong on the west face is not reproduced; the model shows its panel as ruled columns only.
- Measurements after the published figures (3.75 m tall; inscribed 2.75 m; faces 1.32 m wide at the base, 1.22 m at the top). The crown, the tortoise and the place of the single Old Turkic line on the west face are drawn schematically.
