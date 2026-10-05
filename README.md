# obelisk-390

An interactive plate of the **Obelisk of Theodosius** (Dikilitaş) in Istanbul's Hippodrome: the red granite obelisk of Thutmose III, carved for Karnak c. 1450 B.C. and raised here by Theodosius I in A.D. 390.

The obelisk and its pedestal are a rotatable 3D model drawn in the flat, ink-outlined style of a printed technical plate. Next to it, a reading page sets each face's hieroglyphic column beside its transliteration, translation and notes.

- **Model**: drag to turn; pinch, Ctrl-scroll or the +/− buttons to zoom; scroll or drag to move along the shaft once zoomed. Hover or tap a line of hieroglyphs to read it.
- **Read**: one scrolling page per face, plus the pedestal with its Latin and Greek inscriptions. On wide screens the model follows what you read.
- **Languages**: English, Türkçe, Français, 日本語.

## Running it

No build step. Serve the folder with any static file server:

```sh
node server.js        # http://localhost:8080
```

Three.js, EB Garamond, Noto Serif JP and Noto Sans Egyptian Hieroglyphs load from CDNs.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole app: layout, 3D model, reading page, interaction |
| `data.js` | Hieroglyph sequences, transliterations and English text for each face, plus the pedestal inscriptions |
| `reliefs.js` | Line drawings of the pedestal reliefs and inscribed faces, every figure placed from measurements on the photographs |
| `photos/` | Photographs of the pedestal shown in the reading page (see below) |
| `i18n.js` | Interface strings and translations (tr, fr, ja), keyed by the English text |
| `scripts/gen-data.py` | Regenerates `data.js` from Gardiner sign codes (needs Python 3 with Unicode 14+ data) |
| `server.js` | Minimal static server for local use |

## Sources and caveats

- The royal names follow Thutmose III's standard titulary. The narrative passages are paraphrased after published translations: J. H. Breasted, *Ancient Records of Egypt* II (1906); L. Habachi, *The Obelisks of Egypt* (1985). Signs are re-typeset in Noto Sans Egyptian Hieroglyphs, so this is an illustrated reading, not a facsimile; the order of passages on each face is approximate.
- Pedestal inscriptions after B. Kiilerich, *American Journal of Archaeology* 105 (2001).
- The pedestal reliefs are line drawings made from photographs by Francesco Bini on Wikimedia Commons: each figure's position, head size and turn, hair, dress and gesture are measured on the photograph; the drawing style is simplified.
- The photographs in `photos/` are by Francesco Bini, from Wikimedia Commons, licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); they are resized here and otherwise unchanged. The app links each one to its Commons page. They remain under CC BY-SA 4.0; the rest of the repository is not affected by that license.
- Model proportions are approximate.

Companion to [bosphore-1819](https://github.com/CahidArda/bosphore-1819).
