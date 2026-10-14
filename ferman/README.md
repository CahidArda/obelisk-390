# ferman-1851

An interactive reading of the **Ferâşet-i Şerîfe Beratı**, an Ottoman berat of Sultan Abdülmecid dated 8 Rebîülevvel 1267 (11 January 1851). It grants a share in the sweeping of the Kaaba in Mecca and the Prophet’s tomb in Medina. The document is in the Sadberk Hanım Museum, Istanbul (gift of Reya Danışman).

A companion to Dikilitaş ([obelisk-390](../README.md)), built the same way: the document on one side, a reading on the other.

- **Document**: a deep-zoom replica, 8000 × 17131 px. Hover or tap a line to highlight it and read it.
- **Read**: each element in order (invocation, tuğra, opening formula, lines 1–7, place of issue), with the Ottoman text, a transliteration, a translation, a note, and how sure the reading is. **See it** zooms the document to that passage.
- **Languages**: English, Türkçe, Français, 日本語.

## Running it

No build step. From the repository root:

```sh
node server.js        # http://localhost:8080/ferman/
```

OpenSeadragon, EB Garamond, Amiri and Noto Serif JP load from CDNs. The image tiles load from a public Upstash Blob bucket, so the repository stays light.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole app: viewer, line highlighting, reading page |
| `data.js` | The reading (`entries`), each line’s outline on the image (`regions`), and where the tiles live (`image`) |
| `i18n.js` | Interface strings and the About text, in four languages |
| `scripts/` | The stitching pipeline (below) |

## How the replica was made

23 phone photographs (plus 2 close-ups of the gold invocation), taken through the display glass, run through `scripts/` in an Upstash Box:

1. `s1_register.py` flattens the one straight-on photograph of the whole document into a rectangle (from its four corners) and registers every other photograph to it with SIFT + MAGSAC homographies.
2. `s2_blend.py` warps each photograph onto an 8000 × 17131 canvas, corrects the remaining misalignment from the wrinkled paper with dense optical flow against the growing mosaic, matches lighting, down-weights glare, and blends by resolution, so the closest shots win.
3. `s3_flatten.py` evens out the lamp light and the frame’s shadow.
4. `gold_reg.py` + `gold_blend.py` stitch in two raking-light close-ups of the gold invocation at the top. The light flips the gold from bright to dark, so they are placed from hand-picked landmarks (`grids.py` draws matching grids) and refined by block matching on gold-presence maps, then flat-fielded and feathered in.
5. `regions.py` traces each line’s outline from the ink for the hover highlights; `dzi.py` cuts the Deep Zoom tile pyramid. `chunks.py` splits each line into word-group boxes. `strip.py` unrolls a curved line into a straight strip, and `boxcrops.py` renders every box straightened, which is how the lines were read: each box in `data.js` carries its own Ottoman text and transliteration (`entries[].chunks`, in the same order as `regions[id].polys`), and the app links boxes and phrases both ways.

The photographs are not in the repository. Requirements: Python 3 with `opencv-contrib-python-headless`, `numpy`, `scipy`, `pillow`.

## Reading v2: words first, then boxes

The current reading was made word by word (`scripts/v2_*.py`, instructions in `READING-V2.md`): `v2_lines.py` unrolls each curved line along a fitted centreline, and `v2_words.py` cuts it into candidate words from the ink. Each line was then read by one agent, its words re-read blind by others, and every disagreement settled by a third from the letter shapes (`v2_brief.py`, `v2_final.py`). The readers then grouped the verified words into phrases, and `v2_boxes.py` builds each box's outline from the ink of exactly those words and checks it (all of its own ink inside, almost none of its neighbours'). The word-level results, with each word's outline and confidence, are in `scripts/reading-words.json`; the working files (crops, readings, disputes) go to `ferman/work/`, which is not committed.

## Sources and caveats

- Title, date, materials and description are from the museum’s label.
- **The reading is provisional.** It was made from the photographs, not the original. The opening formula, the Qur’anic verse (22:26), the closing and the date are secure. Much of the body is partial: each box’s confidence comes from its words, and `…` marks a word not read. The two personal names in lines 4–5 (Şefîk Bey, ‘Alî Rızâ) are probable readings, not certain ones. The small gold invocation at the top follows the ferâşet formula; several of its interlaced words are guesses.
- The Ottoman text is shown typeset in Naskh, not as written in dîvânî.
