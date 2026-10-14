# Ferman 1851 — reading v2: word-level transcription and exact boxes

Instructions for Claude Code. Run from the root of the `obelisk-390` repository, on the branch `ferman-1851` (`git checkout ferman-1851 && git pull`). The app lives in `ferman/`.

You are the **coordinator**. You do the deterministic work (scripts, geometry, validation, assembling `data.js`) yourself, and you hand all reading and judging of handwriting to **subagents** (the Agent/Task tool), in parallel where the steps below say so. Do not read the handwriting yourself to "save time": the point of this run is that every word is read, then checked blind, by separate agents.

## Goal

Fix two problems in `ferman/data.js`:

1. **Boxes don't match their text.** Today each line is cut into "word-group" boxes by ink gaps alone, so a box can contain a word that belongs to the next box, and the text attached to a box does not always sit inside it.
2. **The reading is weak.** It was made box by box by one reader. 12 boxes are partial and 3 unread; two personal names are tentative; **the name of the new holder of the share has not been found** (most likely in line 5 or 6).

The new pipeline works bottom-up: **words first** (segment, read, verify blind, adjudicate), **then** group verified words into boxes whose polygons are built *from those words*, so a box contains exactly its words by construction.

Do not change the app's look or behaviour. Only `ferman/data.js` (and `ferman/scripts/reading.json`) should change, plus new scripts under `ferman/scripts/` and this run's working files under `ferman/work/` (gitignored).

## What the document is

- **Ferâşet-i Şerîfe Beratı** of Sultan Abdülmecid I, Istanbul, 8 Rebîülevvel 1267 (11 January 1851). Sadberk Hanım Museum, gift of Reya Danışman. It grants a share in the *ferâşet*, the sweeping of the Kaaba (Mecca) and the Prophet's tomb (Ravza-i Mutahhara, Medina).
- Script: **dîvânî**; lines rise steeply to the left and end in **stacks** (words piled diagonally up the left margin). Ink alternates by line: **black** (lines 1, 3, 5, 7) and **red** (2, 4, 6). Gold: tuğra, invocation, part of the nişan formula.
- Elements, top to bottom, with their ids in `data.js`:
  - `davet` — gold invocation at the top (probable: *zekera'llâhu te'âlâ a'lâ ve bi't-takdîmi ehakka ve elyaka ve evlâ*).
  - `tugra` — *'Abdü'l-mecîd Hân bin Mahmûd el-muzaffer dâimâ* (read).
  - `nisan` — gold + red block hanging from the tuğra: *Nişân-ı şerîf-i 'âlî-şân-ı sâmî-mekân ve tuğrâ-yı garrâ-yı cihân-sitân-ı hâkânî nefeze bi'l-'avni'r-Rabbânî ve'l-'inâyeti's-Samedâniyye hükmü oldur ki* (read).
  - `l1` … `l7` — the seven text lines.
  - `place` — *Bi-makâm-ı Kostantıniyye el-mahrûse*, inside the loop at bottom left (probable).
- The current per-box reading (Ottoman, transliteration, confidence, translations in en/tr/fr/ja) is in `ferman/data.js` → `entries[].chunks` and in `ferman/scripts/reading.json`. Treat it as **a hypothesis to test, never as ground truth**.

### Formulary to check readings against

Ferâşet berats follow a chancery template. A full transliteration of a 1904 ferâşet berat (Abdülhamid II, for Mezhebzâde Abdurrahman Efendi) is published here — fetch it with WebFetch at the start and save the transcription block to `ferman/work/reference-1904.txt` for the agents:
https://www.karamandauyanis.com/yazarlar/yusuf-yildirim/mezhebzade-abdurrahman-efendi-nin-feraset-berati/88536

Its preamble differs from ours (ours opens *Çünki Hazret-i Vâhibü'l-atâyâ ve'l-cûd … «ve tahhir beytiye li't-tâifîne …»*), but these parts are shared and should guide (not override) the reading:

- the share: *ber-vech-i hasebî … kırât ferâşet-i şerîfe hıdmet-i celîlesiyle şeref-yâb olan …*
- the vacancy: *… vefâtı vukû'ıyla mahlûlünden …* / *münhal olmağla*
- the applicant: *… ol hıdmet-i şerîfeyi kendüye sermâye-i devlet ve sebeb-i rahmet ve şefâ'at bilüp ez-derûn tâlib ü râgıb olmağla …*
- the request: *… makâm-ı nezâret-i evkâf-ı hümâyûnumdan bi't-takrîr … tevcîh olunmak fermânım olmağın … târîhiyle bu berât-ı … verdim ve buyurdum ki …*
- the duty: *mûmâ ileyh ba'de'l-yevm … hıdmet-i lâzımesin tarafından ta'yîn edeceği kâim-makâm ve nâib-i menâb … kemâl-i ta'zîm ve tekrîm ve âdâb ve nihâyet-i hayâ ve hicâb ve nezâfet-i elbise ve siyâb ile …*

Facts established so far (verify them like everything else):
- Line 3 ends with *Hazîne-i Hâssam nâzırı* and line 4 opens with that official's elkab: *iftihârü'l-e'âlî ve'l-e'âzım Şefîk Bey dâme 'ulüvvühû* (name tentative).
- Line 5 names the *Evkâf-ı Hümâyûnum nâzırı … 'Alî Rızâ(?) dâme 'ulüvvühû* who reports *bi't-takrîr*; the grant formula *'inâyetim erzânî kılınarak bu berât-ı hümâyûnu verdim* is probable; the stack at the end of line 5 holds a date, probably the effective date of the grant.
- Shares are counted in *kırât*; *ber-vech-i hasebî* occurs in lines 4 and 6.
- Line 7 is the closing: *… da'avât-ı hayriyyesine iştigâl ve muvâzabet eyleye. Şöyle bileler, 'alâmet-i şerîfeye i'timâd kılalar. Tahrîren fi'l-yevmi's-sâmin min şehr-i Rebî'i'l-evvel sene seb' ve sittîn ve mieteyn ve elf* (read).

**Top priority for the readers: find the new holder's name** (*… nâm …*, *mûmâ ileyh*, *merkûm*, *işbu râfi'-i tevkî'* …) and the holder's previous holder / the reason for the vacancy.

## Inputs

| What | Where |
|---|---|
| Stitched replica, 8000 × 17131 px | `https://b553e4b37a2b.blob.upstash.io/v2/replica-8000-v2.jpg` (20 MB) |
| Gold invocation, raking-light close-up (photo + enhanced) | `https://b553e4b37a2b.blob.upstash.io/v1/gold-closeup.jpg` |
| Current regions + reading | `ferman/data.js` (`regions`, `entries[].chunks`, `groups`) |
| Current reading, editable | `ferman/scripts/reading.json` |
| Earlier pipeline scripts (paths inside point at the old cloud box; adapt) | `ferman/scripts/*.py` |

All coordinates in `data.js` are in replica pixels (x right, y down). `regions[id].polys[i]` is the outline of box `i` of element `id`; `entries[k].chunks[i]` is that box's text. **The i-th poly and the i-th chunk must always describe the same thing.** Boxes are in reading order (right to left, then up the stack).

## Phase 0 — setup (coordinator)

1. `mkdir -p ferman/work` and add `ferman/work/` to `.gitignore`.
2. Download both images into `ferman/work/`. Python 3 with `opencv-python-headless numpy scipy pillow` (install with pip if missing).
3. Fetch the 1904 reference (above) into `ferman/work/reference-1904.txt`.
4. Load `ferman/data.js` in Python by stripping the `window.FERMAN = ` prefix and the trailing `;`, then `json.loads`. Write a helper `ferman/scripts/v2_common.py` with load/save for `data.js` (keep the header comment and the compact JSON format the file uses today).

## Phase 1 — line geometry (coordinator, scripted)

For each text element (`l1`…`l7`, `nisan`; `davet`, `tugra`, `place` are single-box and handled in Phase 6), build a **curved centreline** and an **unrolled strip**:

1. Centreline: take the current boxes of the line (`regions[id].polys`), compute their centroids in reading order, add the right end of the line's text and the top of its stack, and fit a smooth curve (e.g. a cubic spline through the points, resampled every 4 px). Lines rise to the left and bend sharply up at the stack; the curve must follow the stack.
2. Strip: sample the replica along the curve with normals (`cv2.remap`), height ±500 px around the centreline (lines are ~1100 px apart; trim so neighbouring lines barely appear). Save `work/<id>/strip.png` and the two float32 maps `work/<id>/map_x.npy`, `work/<id>/map_y.npy` so any strip pixel `(u, v)` maps back to replica `(x, y)`. The strip is rotated so text reads normally (right-to-left along the strip).
3. Ink mask for the strip: dark ink for black lines (L below local background by > 28) and red ink for red lines (R − G > 40), small opening to drop specks. **Drop paper creases**: components that are long and thin (width > 10 × height and height < ~22 px) or that run past the end of the text.
4. Render `work/<id>/strip_preview.jpg` with the ink mask tinted, to check by eye that the strip contains the whole line (stack included) and nothing of the neighbouring lines. Fix anchors and repeat until it does. Look at every preview yourself; this is geometry, not reading.

## Phase 2 — word segmentation (coordinator, scripted)

Dîvânî words are made of several disconnected pieces (letters that don't join to the left, dots, marks above), and the gaps inside a word can be as wide as the gaps between words. So:

1. Connected components of the strip's ink mask → **pieces**. Attach dots and marks (small components) to the nearest large piece below/above them.
2. Group pieces into **candidate words** by horizontal gap along the strip, threshold from the gap distribution of that line (typically the valley of a bimodal histogram), never splitting a piece. In the stack, group by the stack's own diagonal instead.
3. Number candidate words in reading order: `w01, w02, …`. For each word save:
   - `work/<id>/words/wNN.png` — the word cut out with ~40 px margin, **upscaled ×2**, contrast-equalised (CLAHE on L).
   - `work/<id>/words/wNN_ctx.png` — the same word with one neighbour on each side, the word itself outlined.
   - its polygon in **replica coordinates**: dilate the word's ink mask by ~10 px, take the outer contour, map every point through `map_x/map_y`, simplify (approx. 4 px tolerance).
4. Render `work/<id>/overview.jpg`: the whole strip with every candidate word boxed and numbered (numbers big enough to read).
5. Write `work/<id>/words.json`: `[{id, polygon, bbox, strip_box, pieces}]`.

Expect over- and under-segmentation; Phase 3 corrects it. Aim for slightly **over**-segmented (merging is easier than splitting).

## Phase 3 — word reading (subagents, one per line, all 8 in parallel)

Launch one subagent per element (`l1`…`l7`, `nisan`). Give each the prompt below with the paths filled in. Agents must look at the images with the Read tool.

> You are reading one line of an Ottoman dîvânî document, word by word: line **{id}** ({ink} ink) of the Ferâşet-i Şerîfe Beratı of Sultan Abdülmecid, Istanbul, 8 Rebîülevvel 1267 (11 January 1851), granting a share in the sweeping of the Kaaba and the Prophet's tomb.
>
> Files: the unrolled line `{strip}`, the numbered overview `{overview}`, one image per candidate word `{words_dir}/wNN.png` and with context `{words_dir}/wNN_ctx.png`. Context: the previous line's last words and the next line's first words, as currently read: `{prev_next}`. Chancery formulary: `{reference}` and the formulas listed in `ferman/READING-V2.md`. A previous reader's tentative reading of this line (may be wrong, **do not copy it, test it**): `{current_reading}`.
>
> 1. First check segmentation on the overview. List merges (`w12+w13`) and splits (`w20` at a described point) needed so each candidate is exactly one written word. Count a word joined by *-i* izafet as one word if written as one; enclitics written apart are separate words.
> 2. Then, for every word in reading order, look at `wNN.png` and `wNN_ctx.png` and give:
>    - `ota`: the word in Ottoman Turkish (Arabic script, modern Naskh spelling, with the letters you actually see; use ـ for nothing), or `""` if illegible;
>    - `tl`: transliteration (İA-style: â î û, ' for 'ayn, ' for hamza, -ı/-i izafet);
>    - `conf`: `read` (no doubt), `probable` (one letter or dot in doubt), `guess` (shape fits but other readings are possible), `illegible`;
>    - `alts`: other readings you considered, most likely first;
>    - `why`: one line on the letter shapes that decided it (e.g. "three teeth + dots above = ش; final ه tail").
> 3. Read the line as a sentence at the end and flag any word that breaks the grammar or the formulary (`flag: true`, with a reason).
>
> Rules: describe what is written, not what the formulary says should be written. If the formulary suggests a word that does not match the shapes, say so in `why` and keep your reading. Never fill a gap with a plausible word you cannot see: use `illegible`. Names of people matter most; for each personal name give letter-by-letter what you see.
>
> Output only JSON to `{out}` with `{segmentation: [...], words: [{id, ota, tl, conf, alts, why, flag}], sentence_tl, notes}`.

Apply the segmentation corrections to `words.json` (re-run Phase 2 steps 3–5 for changed words; give merged/split words new ids and keep a mapping), then continue.

## Phase 4 — blind verification (subagents, parallel)

For every word whose first-pass `conf` is not `read`, **and** for a 20% random sample of `read` words, launch verification in batches of ~15 words per subagent (many in parallel). The verifier sees **only the images and the line's position in the document**, never the first reading.

> Read these Ottoman dîvânî words from line {id} of an 1851 Ottoman berat (ferâşet grant). For each image `wNN.png` (and `wNN_ctx.png` for context) give `ota`, `tl`, `conf` (read / probable / guess / illegible), `alts`, `why`, exactly as defined: … (repeat the definitions from Phase 3). You may use `{reference}` for vocabulary, but read the shapes first. Output JSON to `{out}`.

Then the coordinator compares first and second readings per word (normalise: strip diacritics, unify ی/ي and ک/ك, ignore izafet hyphens):
- same reading → keep, `conf` = the lower of the two;
- different → send to **adjudication**.

## Phase 5 — adjudication (subagents)

One adjudicator per line with disagreements (parallel across lines). It gets, for each disputed word: both readings with their `why`, the word image and context image, the line's sentence so far, and the formulary.

> Two readers disagree on these words. For each, decide from the letter shapes: pick A, pick B, give a third reading, or mark illegible. Explain in one line what in the image decides it. Prefer the reading that fits the shapes over the one that fits the formulary; when both fit, prefer the formulary. Output JSON to `{out}`.

Loop: if adjudication returns `illegible` for a word that the line's sense check (next step) needs, try once more with a larger crop (×3, more context) by a fresh subagent; then stop and accept `illegible`.

**Line sense check** (one subagent per line, after adjudication): read the assembled line in context (previous and next lines), confirm it parses as Ottoman chancery prose, list at most 5 words to re-examine. Re-examine those with a fresh word reader; accept its result only if it is `read` or `probable`.

## Phase 6 — group words into boxes (one subagent per line, then scripted geometry)

1. A subagent per line gets the final word list (ota, tl, conf, id) and the overview image and groups **consecutive** words into **phrases**: 3–8 words each, cut at natural units (an izafet chain, a verb with its object, a formula, a name with its elkab). The stack at the end of a line is one or two phrases of its own. It also writes, per phrase, the translation into **English, Turkish (modern), French and Japanese**, short and literal, following the style of the current `chunks[].text` (square brackets for words supplied for sense; … where words are illegible). Output JSON.
2. The coordinator builds each box polygon **from its words**: union of the words' polygons (Phase 2 step 3), closed by ~25 px, outer contour, simplified; if a line's boxes would overlap, shrink the overlap away from the word owners. Then **validate** with a script:
   - every word belongs to exactly one box;
   - ≥ 97% of each box's own ink pixels are inside its polygon;
   - ≤ 3% of the box's area is ink belonging to words of *other* boxes;
   - boxes of one line don't overlap by more than 2% of the smaller box.
   Fail → adjust the polygon (or ask the grouping agent to move a word) and re-validate. Print a table per line.
3. `davet`, `tugra` and `place` stay single boxes; re-check their polygons cover the whole composition (`davet` must include the tall cluster on the left and the long tail stroke). For `davet` also use the close-up `work/gold-closeup.jpg` for the reading (Phases 3–5 with that image instead of word crops).

**Box confidence** = from its words: all `read` → `read`; all `read`/`probable` → `probable`; any `guess` or ≤ 30% `illegible` → `partial`; more illegible → `unread`. In box `ota`/`tl`, write illegible words as `…` (merge consecutive ones). **No question marks** in `ota`, `tl` or translations; uncertainty lives in `conf`, and for names add "(name tentative)" in the translations when the name's words are not `read`.

## Phase 7 — write the data (coordinator)

1. For each element: `regions[id].polys` = the new box polygons in reading order, `regions[id].bbox` = their bounding box; `entries[k].chunks` = the new boxes, same order, each `{conf, ota, tl, text: {en, tr, fr, ja}}`. Add `words: [{ota, tl, conf, poly}]` to each chunk (the app ignores it; keep it for future corrections).
2. Update a line's `note` (all four languages) **only** where the new reading changes a fact stated in it (e.g. a name found, a share size, who petitioned). Keep notes short and in the same voice. If the new holder's name is found, add it to the `case` group intro and to line 6's note.
3. Keep `groups`, `ink`, `ref`, `title`, `photo` unchanged unless a title is now wrong.
4. Save `ferman/data.js` (same header comment, compact JSON), and mirror chunks/groups into `ferman/scripts/reading.json`. Also save the full word-level results to `ferman/scripts/reading-words.json`.
5. Keep all the new scripts in `ferman/scripts/` with paths relative to the repo (no absolute paths), and add a short section to `ferman/README.md` describing the v2 pipeline in three or four sentences.

## Phase 8 — QA (coordinator + one reviewer subagent)

1. Render `work/qa/<id>.jpg` per element: the replica region with every box outlined and numbered, and next to it the box's `ota` / `tl`. Render every box as its own straightened crop `work/qa/<id>_<i>.png` with its `ota` printed under it.
2. A reviewer subagent goes through all box crops and answers per box: does the crop contain exactly the written words in its `ota` (no word missing, no extra word)? List failures. Fix and re-check failures.
3. Checks by script: counts of polys and chunks match for every element; no `(؟)`, `[?]` or `?` inside any `ota`/`tl`; every chunk has all four translations; `conf` values are one of `read|probable|partial|unread`.
4. Run the app (`node server.js`, open `http://localhost:8080/ferman/`), open `#l5.1`, `#l6.3` and `#davet`, and confirm the selected box outlines exactly its text. Tooltips should show the box's own text.

## Phase 9 — finish

1. Commit on `ferman-1851` with a message summarising what changed (counts of read/probable/partial/unread before and after, the holder's name if found, names confirmed or changed), and push.
2. Report in a few lines: the new confidence counts, what was found (especially the holder's name and the two officials' names), what remains illegible and where, and anything the reviewer could not fix.

## Notes for the coordinator

- Parallelism: Phase 3 and 6.1 run 8 subagents at once; Phase 4 runs as many batches as needed at once. Keep every subagent's input self-contained (paths + definitions); they don't see this conversation.
- Never let one agent both read and verify the same word.
- Keep the replica's coordinate system. Do not re-stitch or re-tile the image; the deep-zoom tiles on Blob stay as they are.
- If you run out of context, the files in `ferman/work/` are the state: words.json, reader outputs, verifier outputs, adjudications. Resume from them.
