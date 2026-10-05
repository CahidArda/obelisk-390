# obelisk-390

An interactive, print-style reading of the **Obelisk of Theodosius** (Dikilitaş) in Istanbul's Hippodrome: the red granite obelisk of Thutmose III, carved for Karnak c. 1450 B.C. and raised here by Theodosius I in A.D. 390.

**Live:** [obelisk-390.vercel.app](https://obelisk-390.vercel.app) · **Demo:** [10-second video](docs/demo-10s-en.mp4) · **How it was made:** [blog post](https://cahidarda.github.io/articles/dikilitas)

The obelisk and its pedestal are a rotatable 3D model drawn in the flat, ink-outlined style of a printed technical plate. Next to it, a reading page sets each face's hieroglyphic column beside its transliteration, translation and notes.

- **Model**: drag to turn; pinch, Ctrl-scroll or the +/− buttons to zoom; scroll or drag to move along the shaft once zoomed. Hover or tap a line of hieroglyphs to read it.
- **Read**: one scrolling page per face, plus the pedestal with its Latin and Greek inscriptions. On wide screens the model follows what you read. **See it** takes the model to a passage; on the pedestal, **Photo** opens the real relief.
- **About**: credits, links and sources (the About button, or `#about` in the URL).
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
| `photos/` | Photographs of the pedestal, opened from the Photo buttons (see below) |
| `i18n.js` | Interface strings and translations (tr, fr, ja), keyed by the English text |
| `scripts/gen-data.py` | Regenerates `data.js` from Gardiner sign codes (needs Python 3 with Unicode 14+ data) |
| `server.js` | Minimal static server for local use |
| `favicon.svg`, `apple-touch-icon.png` | The Eye of Horus icon, on the same plate as bosphore-1819's |
| `docs/demo-10s-en.mp4` | The 10-second demo video (2560x1600, 60 fps) |
| `scripts/video/` | How the demo video was made (see below) |

## The demo video

`docs/demo-10s-en.mp4` was recorded in a headless browser with software WebGL, which draws only a few frames a second in real time. To get smooth 60 fps anyway, `scripts/video/vclock.js` replaces the page's clock (`performance.now`, `requestAnimationFrame`, timers, smooth scrolling and CSS transitions) with a virtual one, and `record.mjs` advances it by exactly 1/60 s before each screenshot, so the take is frame-perfect however slow the machine is.

```sh
node server.js &                                  # the app on :8080
cd scripts/video && npm i puppeteer-core          # uses the system Chromium
node record.mjs                                   # 600 frames at 1280x800, device scale 2
ffmpeg -framerate 60 -i frames/f%04d.jpg -vf 'scale=in_range=jpeg:out_range=tv,format=yuv420p' -c:v libx264 -crf 14 raw.mp4
python3 render.py spec.json                       # captions, cursor, click ripples, URL pill
```

`render.py` and the cursor sprites come from bosphore-1819. Captions must not contain apostrophes (ffmpeg `drawtext` quoting).

## Sources and caveats

- The royal names follow Thutmose III's standard titulary. The narrative passages are paraphrased after published translations: J. H. Breasted, *Ancient Records of Egypt* II (1906); L. Habachi, *The Obelisks of Egypt* (1985). Signs are re-typeset in Noto Sans Egyptian Hieroglyphs, so this is an illustrated reading, not a facsimile; the order of passages on each face is approximate.
- Pedestal inscriptions after B. Kiilerich, *American Journal of Archaeology* 105 (2001).
- The pedestal reliefs are line drawings made from photographs by Francesco Bini on Wikimedia Commons: each figure's position, head size and turn, hair, dress and gesture are measured on the photograph; the drawing style is simplified.
- The photographs in `photos/` are by Francesco Bini, from Wikimedia Commons, licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); they are resized here and otherwise unchanged. The app links each one to its Commons page. They remain under CC BY-SA 4.0; the rest of the repository is not affected by that license.
- Model proportions are approximate.

Companion to [bosphore-1819](https://github.com/CahidArda/bosphore-1819).
