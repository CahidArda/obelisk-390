"""Phase 3-5 helpers: write self-contained briefs for the reading subagents.

usage: v2_brief.py read            -> work/<id>/brief_read.md for every line, nisan/davet composition briefs
       v2_brief.py verify          -> work/verify/batch_NN.md (blind: images only)
       v2_brief.py compare         -> work/<id>/compare.json, work/<id>/brief_adjudicate.md
"""
import sys, os, glob, random, unicodedata, re
import cv2
import numpy as np
from v2_common import *

DOC = ('the Ferâşet-i Şerîfe Beratı of Sultan Abdülmecid I, Istanbul, 8 Rebîülevvel 1267 '
       '(11 January 1851), granting a share in the ferâşet (sweeping) of the Kaaba in Mecca and the '
       'Prophet\'s tomb in Medina. Script: dîvânî; lines rise steeply to the left and end in a '
       '"stack" of words piled diagonally up the left margin. Lines 1, 3, 5, 7 are black ink, 2, 4, 6 red.')

DEFS = '''Field definitions (per word):
- `ota`: the word in Ottoman Turkish (Arabic script, modern Naskh spelling, with the letters you actually see), or `""` if illegible.
- `tl`: transliteration, İA style (â î û; ‘ for ‘ayn, ’ for hamza; -ı/-i for izafet).
- `conf`: `read` (no doubt), `probable` (one letter or dot in doubt), `guess` (shape fits but other readings are possible), `illegible`.
- `alts`: other readings you considered, most likely first (list of transliterations; may be empty).
- `why`: one line on the letter shapes that decided it (e.g. "three teeth + dots above = ش; final ه tail").
Rules: describe what is written, not what the formulary says should be written. If the formulary suggests a word that does not match the shapes, say so in `why` and keep your reading. Never fill a gap with a plausible word you cannot see: use `illegible`. Personal names matter most: for each name give letter by letter what you see in `why`.'''

FORMULARY = '''Formulary shared by ferâşet berats (guide, not ground truth):
- the share: ber-vech-i hasebî … kırât ferâşet-i şerîfe hıdmet-i celîlesiyle şeref-yâb olan …
- the vacancy: … vefâtı vukû‘ıyla mahlûlünden … / münhal olmağla
- the applicant: … ol hıdmet-i şerîfeyi kendüye sermâye-i devlet ve sebeb-i rahmet ve şefâ‘at bilüp ez-derûn tâlib ü râgıb olmağla …
- the request: … makâm-ı nezâret-i evkâf-ı hümâyûnumdan bi’t-takrîr … tevcîh olunmak fermânım olmağın … târîhiyle bu berât-ı … verdim ve buyurdum ki …
- the duty: mûmâ ileyh ba‘de’l-yevm … hıdmet-i lâzımesin tarafından ta‘yîn edeceği kâim-makâm ve nâib-i menâb … kemâl-i ta‘zîm ve tekrîm ve âdâb ve nihâyet-i hayâ ve hicâb ve nezâfet-i elbise ve siyâb ile …
- the holder is usually introduced as "… nâm …", "mûmâ ileyh", "merkûm", or "işbu râfi‘-i tevkî‘-i refî‘ü’ş-şân-ı hâkânî <name> zîde …".
Our document's preamble differs from the 1904 one: it opens "Çünki Hazret-i Vâhibü’l-atâyâ ve’l-cûd …" and quotes Qur'an 22:26 "ve tahhir beytiye li’t-tâifîne ve’l-kâimîne ve’r-rukke‘i’s-sücûd".'''


def rel(p):
    return os.path.relpath(p, os.path.dirname(FERMAN))


def abspath(p):
    return os.path.abspath(p)


def line_text(d, id, which):
    ch = entry(d, id)['chunks']
    c = ch[-1] if which == 'last' else ch[0]
    return c['tl']


def brief_read(d, id):
    W = jload(wdir(id, 'words.json'))
    ov = sorted(glob.glob(wdir(id, 'overview_*.jpg')), key=lambda p: int(re.findall(r'_(\d+)\.jpg', p)[0]))
    i = LINES.index(id)
    prev_id = LINES[i - 1] if i > 0 else None
    next_id = LINES[i + 1] if i + 1 < len(LINES) else None
    prev = line_text(d, prev_id, 'last') if prev_id else '(top of document)'
    nxt = line_text(d, next_id, 'first') if next_id else '(end of text)'
    cur = '\n'.join(f'  box {k}: [{c["conf"]}] {c["ota"]} | {c["tl"]}' for k, c in enumerate(entry(d, id)['chunks']))
    ink = ink_of(d, id)
    out = abspath(wdir(id, 'read1.json'))
    s = f'''# Read line {id} word by word

You are reading one line of an Ottoman dîvânî document, word by word: line **{id}** ({ink} ink) of {DOC}

## Files (look at them with the Read tool)
- The whole unrolled line (straightened; reads right to left; the left end is the stack, unrolled): `{abspath(wdir(id, 'strip.png'))}` (large; optional)
- Numbered overview of candidate words, in reading order (overview_1 is the right end, where the line starts; each next overview continues to the left, with a little overlap):
{chr(10).join('  - `' + abspath(p) + '`' for p in ov)}
- One image per candidate word, upscaled x2: `{abspath(wdir(id, 'words'))}/wNN.png`, and the same word with one neighbour each side, outlined in red: `wNN_ctx.png`. Candidates: {', '.join(w['id'] for w in W)} ({len(W)} candidates).
- Chancery formulary: the 1904 ferâşet berat transliteration at `{abspath(os.path.join(WORK, 'reference-1904.txt'))}`, and:

{FORMULARY}

## Context
- Previous line's end, as currently read: {prev}
- Next line's start, as currently read: {nxt}
- A previous reader's tentative reading of this line, box by box (may be wrong; **do not copy it, test it**):
{cur}

## Task
1. First check segmentation on the overviews. The candidates are deliberately **over-segmented** (often one candidate per letter group), so most words will need merging. List the merges (e.g. `["w12","w13","w14"]`) needed so that each candidate is exactly one written word, and splits (`{{"id": "w20", "where": "<describe the point>"}}`) if one candidate holds two words. Count a word joined by -i izafet as one word if written as one; enclitics written apart are separate words. Candidates that are not writing (stains, strokes from another line) go in `drop`.
2. Then for every word (after your merges) in reading order, look at its `wNN.png` and `wNN_ctx.png` images and give the fields below. For a merged word, use the id list of its candidates (e.g. `"ids": ["w12","w13"]`).
3. Finally read the line as a sentence and flag any word that breaks the grammar or the formulary (`flag: true` plus a reason in `why`).

{DEFS}

Top priority for this document: **find the name of the new holder of the share** (look for "… nâm …", "mûmâ ileyh", "merkûm", "işbu râfi‘-i tevkî‘ …") and the previous holder / the reason for the vacancy, if they are on this line.

## Output
Write only JSON to `{out}` (use the Write tool), shaped:
```
{{"segmentation": {{"merge": [["w01","w02"], ...], "split": [{{"id": "w20", "where": "..."}}], "drop": ["w33"]}},
 "words": [{{"ids": ["w01","w02"], "ota": "...", "tl": "...", "conf": "read|probable|guess|illegible", "alts": ["..."], "why": "...", "flag": false}}, ...],
 "sentence_tl": "the whole line in transliteration, … for illegible words",
 "notes": "anything the coordinator should know (names found, doubtful segmentation)"}}
```
Every candidate id must appear in exactly one word's `ids` or in `drop`. Then reply with one short paragraph: the line's sentence and any names found.
'''
    open(wdir(id, 'brief_read.md'), 'w').write(s)
    return wdir(id, 'brief_read.md')


def comp_crops(d):
    im = replica()
    # nisan: right (gold) and left (red) parts, as in the current two boxes
    os.makedirs(os.path.join(WORK, 'nisan', 'comp'), exist_ok=True)
    for k, p in enumerate(d['regions']['nisan']['polys']):
        P = np.array(p)
        x0, y0 = P.min(0) - 80; x1, y1 = P.max(0) + 80
        x0, y0 = max(0, x0), max(0, y0)
        c = np.ascontiguousarray(im[y0:y1, x0:x1])
        s = min(2.0, 2400 / c.shape[1])
        c = cv2.resize(c, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(os.path.join(WORK, 'nisan', 'comp', f'part{k}.png'), c)
        # halves for detail
        h = c.shape[1] // 2
        cv2.imwrite(os.path.join(WORK, 'nisan', 'comp', f'part{k}_right.png'), c[:, h - 100:])
        cv2.imwrite(os.path.join(WORK, 'nisan', 'comp', f'part{k}_left.png'), c[:, :h + 100])
    os.makedirs(os.path.join(WORK, 'davet'), exist_ok=True)
    x0, y0, x1, y1 = d['regions']['davet']['bbox']
    c = np.ascontiguousarray(im[y0 - 80:y1 + 80, x0 - 80:x1 + 80])
    cv2.imwrite(os.path.join(WORK, 'davet', 'replica.png'), cv2.resize(c, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC))


def brief_comp(d, id, images, extra=''):
    cur = '\n'.join(f'  box {k}: [{c["conf"]}] {c["ota"]} | {c["tl"]}' for k, c in enumerate(entry(d, id)['chunks']))
    out = abspath(os.path.join(WORK, id, 'read1.json'))
    s = f'''# Read the {entry(d, id)['title']['en']} ({id}) of an Ottoman berat

This is the **{entry(d, id)['title']['en']}** of {DOC}
It is a calligraphic composition (words stacked and interlaced), so it is read from whole-composition images rather than word crops.

Images (look at them with the Read tool):
{chr(10).join('- `' + abspath(p) + '`' for p in images)}
{extra}
A previous reader's reading (may be wrong; **test it, do not copy it**):
{cur}

Chancery formulary: `{abspath(os.path.join(WORK, 'reference-1904.txt'))}` (the 1904 berat's invocation and nişan formula are at its start).

Task: read the composition word by word in reading order. For each word give the fields below. Say for each word where in the image it is (e.g. "lower right, on the long gold sweep").

{DEFS}

Output only JSON to `{out}` (Write tool): `{{"words": [{{"ota","tl","conf","alts","why","where","part": <box index it belongs to, 0 or 1 if there are two parts>}}], "sentence_tl": "...", "notes": "..."}}`. Then reply with one line: the reading.
'''
    open(os.path.join(WORK, id, 'brief_read.md'), 'w').write(s)


CONF_RANK = {'read': 3, 'probable': 2, 'guess': 1, 'illegible': 0}


def brief_verify(d, lines, per=15, frac=0.2, seed=1851):
    """Blind batches: every word not `read` in pass 1, plus a 20% sample of `read` words."""
    vdir = os.path.join(WORK, 'verify'); os.makedirs(vdir, exist_ok=True)
    for id in lines:
        rnd = random.Random(f'{seed}{id}')
        batches = []
        W = jload(wdir(id, 'words.json')); P = jload(wdir(id, 'pass1.json'))
        order = [w['id'] for w in W]
        rd = [i for i in order if P[i]['conf'] == 'read']
        pick = set(i for i in order if P[i]['conf'] != 'read')
        pick |= set(rnd.sample(rd, max(1 if rd else 0, round(frac * len(rd)))))
        pick = [i for i in order if i in pick]
        for k in range(0, len(pick), per):
            batches.append((id, pick[k:k + per], order))
        for n, (id, ids, order) in enumerate(batches):
            name = f'batch_{id}_{n + 1:02d}'
            out = abspath(os.path.join(vdir, name + '.json'))
            items = '\n'.join(f'- `{i}` (word {order.index(i) + 1} of {len(order)}): `{abspath(wdir(id, "words", i + ".png"))}` context `{abspath(wdir(id, "words", i + "_ctx.png"))}`, straight from the document `{abspath(wdir(id, "words", i + "_rep.png"))}`' for i in ids)
            s = f"""# Blind reading of {len(ids)} words

Read these Ottoman dîvânî words from line {id[1:]} of 7 ({ink_of(d, id)} ink) of an 1851 Ottoman berat (ferâşet grant): {DOC}

Each word image is upscaled x2; the context image shows the same word outlined in red with one neighbour on each side; the third image is the same area cut straight from the document (not straightened), the word outlined in red, which helps where the straightening distorts letters. Words are listed in reading order within the line (right to left; the last words of a line are in the stack at its left end).

{items}

You may use `{abspath(os.path.join(WORK, 'reference-1904.txt'))}` (a published 1904 ferâşet berat) for vocabulary, but read the shapes first. If the outlined area holds more or less than one whole word, say so in `why` and read what is inside the outline.

{DEFS}

Output only JSON to `{out}` (Write tool): `{{"words": [{{"id": "w07", "ota": "...", "tl": "...", "conf": "...", "alts": [...], "why": "..."}}, ...]}}` with one entry per word above. Then reply with one line.
"""
            open(os.path.join(vdir, name + '.md'), 'w').write(s)
            jsave(os.path.join(vdir, name + '.meta.json'), {'line': id, 'ids': ids})
        print(id, len(batches), 'batches', sum(len(b[1]) for b in batches), 'words')


AR_MARKS = re.compile('[ً-ْٰـ‌‍]')


def norm_ota(s):
    s = AR_MARKS.sub('', s or '')
    for a, b in (('ي', 'ی'), ('ى', 'ی'), ('ك', 'ک'), ('ة', 'ه'), ('ۀ', 'ه'), ('ھ', 'ه'),
                 ('أ', 'ا'), ('إ', 'ا'), ('آ', 'ا'), ('ؤ', 'و'), ('ئ', 'ی')):
        s = s.replace(a, b)
    return re.sub(r'[\s…]+', '', s)


def norm_tl(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r"[\s\-‘’'`ʿʾ…\.]+", '', s).replace('ı', 'i')


def lower(a, b):
    return a if CONF_RANK.get(a, 0) <= CONF_RANK.get(b, 0) else b


def same_reading(a, b):
    if a['conf'] == b['conf'] == 'illegible':
        return True
    return bool((norm_ota(a['ota']) and norm_ota(a['ota']) == norm_ota(b['ota'])) or
                (norm_tl(a['tl']) and norm_tl(a['tl']) == norm_tl(b['tl'])))


def compare(d):
    V = {}
    for f in glob.glob(os.path.join(WORK, 'verify', 'batch_*.json')):
        if f.endswith('.meta.json'):
            continue
        meta = jload(f.replace('.json', '.meta.json'))
        for w in jload(f)['words']:
            V[(meta['line'], w['id'])] = w
    tot = {'same': 0, 'diff': 0, 'unverified': 0}
    for id in LINES[1:]:
        W = jload(wdir(id, 'words.json')); P = jload(wdir(id, 'pass1.json'))
        res, disputes = {}, []
        for w in W:
            a = P[w['id']]; b = V.get((id, w['id']))
            if b is None:
                res[w['id']] = dict(a, status='unverified'); tot['unverified'] += 1
            elif same_reading(a, b):
                res[w['id']] = dict(a, conf=lower(a['conf'], b['conf']), status='agreed', b=b); tot['same'] += 1
            else:
                res[w['id']] = dict(a, status='disputed', b=b); disputes.append(w['id']); tot['diff'] += 1
        jsave(wdir(id, 'compare.json'), res)
        if disputes:
            brief_adjudicate(d, id, W, res, disputes)
        print(id, 'disputed', len(disputes), 'of', sum(1 for r in res.values() if r['status'] != 'unverified'), 'verified')
    print(tot)


def sentence(W, res, mark=()):
    out = []
    for w in W:
        r = res[w['id']]
        t = r['tl'] if r['conf'] != 'illegible' and r['tl'] else '…'
        out.append(f'[{w["id"]}: {t} / {r["b"]["tl"] if r.get("b") else "?"}]' if w['id'] in mark else t)
    return ' '.join(out)


def brief_adjudicate(d, id, W, res, disputes, name='brief_adjudicate.md', out='adjudicate.json', extra=''):
    items = []
    for i in disputes:
        r = res[i]; b = r['b']
        items.append(f"""### {i}
- image `{abspath(wdir(id, 'words', i + '.png'))}`, context `{abspath(wdir(id, 'words', i + '_ctx.png'))}`, straight from the document `{abspath(wdir(id, 'words', i + '_rep.png'))}`
- A: `{r['ota']}` {r['tl']} [{r['conf']}]: {r.get('why', '')}
- B: `{b['ota']}` {b['tl']} [{b['conf']}]: {b.get('why', '')}""")
    s = f"""# Adjudicate disputed words, line {id}

Line {id} ({ink_of(d, id)} ink) of {DOC}

Two readers disagree on the words below. For each, decide from the letter shapes: pick A, pick B, give a third reading, or mark illegible. Explain in one line what in the image decides it. Prefer the reading that fits the shapes over the one that fits the formulary; when both fit, prefer the formulary.
{extra}
The line so far (disputed words in brackets as [id: A / B]):
{sentence(W, res, set(disputes))}

Formulary: `{abspath(os.path.join(WORK, 'reference-1904.txt'))}` and:
{FORMULARY}

{chr(10).join(items)}

{DEFS}

Output only JSON to `{abspath(wdir(id, out))}` (Write tool): `{{"words": [{{"id": "w07", "choice": "A|B|C|illegible", "ota": "...", "tl": "...", "conf": "read|probable|guess|illegible", "why": "..."}}]}}`, one entry per disputed word. Then reply with one line.
"""
    open(wdir(id, name), 'w').write(s)


if __name__ == '__main__':
    d = load_data()
    if sys.argv[1] == 'read':
        for id in LINES[1:]:
            print(brief_read(d, id))
        comp_crops(d)
        brief_comp(d, 'nisan', sorted(glob.glob(os.path.join(WORK, 'nisan', 'comp', '*.png'))),
                   'Part 0 is the right part of the composition (mostly gold), part 1 the left part (mostly red); the parts overlap a little.')
        brief_comp(d, 'davet', [os.path.join(WORK, 'davet', 'replica.png'), os.path.join(WORK, 'gold-closeup.jpg')],
                   'The first image is from the stitched replica; the second is a raking-light close-up photograph (left: photo, right: enhanced) where the gold reads much better.')
    elif sys.argv[1] == 'verify':
        brief_verify(d, sys.argv[2:] or LINES[1:])
    elif sys.argv[1] == 'compare':
        compare(d)
