# Proofreading the ferman reading

You are proofreading the transcription and translation of an Ottoman document, phrase by phrase, against images of the document. For each phrase, decide from the handwriting whether the existing reading matches what is written. Where it matches, confirm it. Where it does not, give your reading and show why. Judge each phrase on its own evidence. Don't assume the existing reading is right, and don't assume it is wrong.

## The document

**Ferâşet-i Şerîfe Beratı** of Sultan Abdülmecid I, issued in Istanbul on 8 Rebîülevvel 1267 (11 January 1851), now in the Sadberk Hanım Museum, Istanbul. A *berat* is a letter of appointment issued under the sultan's tuğra. This one grants a share (*kırât*) in the *ferâşet*: the duty of sweeping the Kaaba in Mecca and the Prophet's tomb (Ravza-i Mutahhara) in Medina.

- **Script:** dîvânî. Lines rise steeply towards the left, and each ends in a "stack": words piled diagonally up the left margin.
- **Ink** alternates by line: lines 1, 3, 5 and 7 are black, lines 2, 4 and 6 are red. The invocation, the tuğra and part of the nişan formula are in gold.
- **Elements**, top to bottom, with their ids:
  - `davet`: the gold invocation
  - `tugra`: the tuğra
  - `nisan`: the formula hanging from the tuğra (*Nişân-ı şerîf-i 'âlî-şân … hükmü oldur ki*)
  - `l1` to `l7`: the seven text lines
  - `place`: the place of issue, inside the loop at bottom left
- **What it should contain:** a berat of this kind usually runs preamble (line 1 opens with Qur'an 22:26), then the case: who held the share, why it became vacant, who asked for it and on whose recommendation. Then come the grant, the instruction to obey, and the date and place. Use this order as a guide when reading, not as a rule: read what is written.

## Repository

Public on GitHub: **https://github.com/CahidArda/obelisk-390**. Use the branch **`ferman-1851-reading-v2`**, which has the latest reading:

```sh
git clone -b ferman-1851-reading-v2 https://github.com/CahidArda/obelisk-390.git
cd obelisk-390
node server.js    # optional: the app at http://localhost:8080/ferman/index.html
```

The repository holds two apps. The ferman is in `ferman/`; everything outside it belongs to the obelisk app and is not part of this task.

| Path | What it holds |
|---|---|
| `ferman/data.js` | **The reading.** `window.FERMAN = { image, entries, regions, groups }` |
| `ferman/scripts/reading-words.json` | The word-level reading: for each line id, a list of words |
| `ferman/scripts/reading.json` | The phrase-level reading that `data.js` is generated from |
| `ferman/index.html`, `ferman/i18n.js` | The app and its interface text. Do not change these |
| `ferman/README.md` | How the replica and the reading were made |
| `ferman/scripts/*.py` | The image and reading pipeline. Its paths point at a remote machine, so you don't need to run it |

### `data.js`

- `image.full` is the whole document as one JPEG (8000 × 17131 px): https://b553e4b37a2b.blob.upstash.io/v2/replica-8000-v2.jpg. `image.tiles` is the same image as a Deep Zoom pyramid.
- `entries` lists the 11 elements in reading order (`davet`, `tugra`, `nisan`, `l1` … `l7`, `place`). Each entry has:
  - `id`, `ink`
  - `conf`: confidence for the whole element
  - `title`, `note`: in four languages
  - `chunks`: the phrases, in reading order. Each chunk has:
    - `ota`: Ottoman text in Arabic script
    - `tl`: transliteration
    - `text`: translation in `en`, `tr`, `fr` and `ja`
    - `conf`: one of `read`, `probable`, `partial`, `unread`
    - `words`: a list of `{ ota, tl, conf, poly }`
- `regions[id].polys` holds one polygon per chunk, in the same order as `entries[id].chunks`. Each polygon is a list of `[x, y]` pixel points on the full image, outlining the ink of that phrase.

### `reading-words.json`

For each line id, the words in order. Each word has `ota`, `tl`, `conf` (`read`, `probable`, `guess` or `illegible`), a `why` (the letter shapes the reading was based on), `alts` (alternative readings considered) and `poly` (its outline on the full image).

## Getting the images

Download `image.full` once. Then, for each chunk, crop the bounding box of its polygon from `regions[id].polys[i]` with about 60 px of padding. Lines slope steeply, so also make a version rotated to horizontal: the polygon's main axis gives the angle.

To look closer at a single word, crop its `poly` from `reading-words.json`. Keep some of the neighbouring words in view as well: dîvânî letters run across word boundaries, and dots often sit above a neighbouring word.

If you are given a folder of ready-made crops instead (`<id>.jpg` for a whole element with its boxes numbered, `<id>_<i>.png` for each box straightened, and `boxes.md` listing each box's current text), use those. Box `<id>_<i>` is chunk `i` of entry `<id>`.

## How to proofread

Work through the elements in order (`davet`, `tugra`, `nisan`, `l1` … `l7`, `place`), and through each element chunk by chunk. For every chunk:

1. **Read it yourself first.** Look at the crop and write down what you read, word by word, before you look at the existing `ota` and `tl`. Note the letter shapes and dots that decide each word.
2. **Compare** your reading with the existing `ota` and `tl`, word by word.
3. **Decide each word:**
   - `agree`: the existing reading matches the ink.
   - `correct`: the ink shows something else. Give your reading and the specific evidence.
   - `uncertain`: the ink does not settle it either way. Give the candidates.

   A word that is hard to read is not therefore wrong. Mark it `correct` only when you can point to what is written.
4. **Read the chunk in context.** Check that it makes sense with the chunks before and after it, and fits the formulary of a ferâşet berat. If the context suggests a different word, go back to the ink and check it. Context alone is not evidence.
5. **Check the transliteration** against your final Arabic-script reading: consistent spelling, iżâfet, long vowels (â, î, û) and the ' and ' marks.
6. **Check the translations** (`en`, `tr`, `fr`, `ja`) against the final reading. Do they say what the Ottoman says, with nothing added or left out? Rewrite a translation only where the reading changed or the meaning is off.
7. **Set the confidence** honestly: `read` if every word is clear, `probable` if a few words are slightly doubtful, `partial` if key words remain uncertain, `unread` if the phrase isn't legible.

Pay particular attention to:
- **Personal names and titles.** These are the hardest to predict from the formulary, so read them strictly from the ink: in lines 3 to 6, the holder, the person who asked, the recommending officials, and the previous holder if named.
- **Words marked `guess` or `illegible`,** and chunks marked `partial` or `unread`.
- **The date and place** at the end.

Don't skip a chunk because it looks formulaic. Formula words are read from the ink too.

## What to deliver

1. **`ferman/PROOFREAD-REPORT.md`**: one section per element, then one entry per chunk:

   ```
   ### l3 · chunk 4  [current conf: partial → proposed: probable]
   Current:  <ota>  |  <tl>
   Mine:     <ota>  |  <tl>
   Words:
   - word 1 "…": agree
   - word 3 "…": correct → "…". Evidence: …
   - word 5 "…": uncertain, between "…" and "…". Evidence: …
   Translation: en ok · tr changed to "…" · fr ok · ja changed to "…"
   ```

   End with a summary: how many chunks you confirmed unchanged and how many you changed, the names and other key facts as you read them, and what remains uncertain.
2. **The updated `ferman/data.js`**, if you changed anything. Change only `entries[].chunks` (`ota`, `tl`, `text`, `conf`, `words`) and, where the reading changed what they say, an entry's `note` and `conf`. Keep `regions`, `groups`, `image` and the order and number of chunks as they are, so the boxes on the image still line up with their text. If you think a chunk boundary is wrong (a word sitting in the wrong box), say so in the report rather than moving it.

Commit nothing and push nothing. Leave the changes in the working tree for review.
