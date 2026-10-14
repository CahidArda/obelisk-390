"""Phases 5-6: assemble final word readings; briefs for the sense check and the phrase grouping.

usage: v2_final.py final [id ...]   -> work/<id>/final.json  [{id, ota, tl, conf, src, alts, why}]
       v2_final.py sense [id ...]   -> work/<id>/brief_sense.md
       v2_final.py recheck <id> wNN ...  -> work/<id>/brief_recheck.md (fresh reader, larger crops)
       v2_final.py group [id ...]   -> work/<id>/brief_group.md
"""
import sys, os, glob, re, json
import cv2
import numpy as np
from v2_common import *
from v2_brief import DOC, DEFS, FORMULARY, abspath, lower, CONF_RANK


def finalize(id):
    W = jload(wdir(id, 'words.json'))
    C = jload(wdir(id, 'compare.json'))
    A = {}
    if os.path.exists(wdir(id, 'adjudicate.json')):
        A = {w['id']: w for w in jload(wdir(id, 'adjudicate.json'))['words']}
    R = {}
    if os.path.exists(wdir(id, 'recheck.json')):
        R = {w['id']: w for w in jload(wdir(id, 'recheck.json'))['words']}
    out = []
    for w in W:
        c = C[w['id']]
        if c['status'] == 'disputed' and w['id'] in A:
            a = A[w['id']]
            f = {'ota': a.get('ota', ''), 'tl': a.get('tl', ''), 'conf': a.get('conf', 'guess'),
                 'src': 'adjudicated:' + a.get('choice', '?'), 'why': a.get('why', ''),
                 'alts': [x for x in {c['tl'], c['b']['tl']} if x and x != a.get('tl')]}
        else:
            f = {'ota': c['ota'], 'tl': c['tl'], 'conf': c['conf'], 'src': c['status'],
                 'why': c.get('why', ''), 'alts': c.get('alts') or []}
        if w['id'] in R and R[w['id']].get('conf') in ('read', 'probable'):
            r = R[w['id']]
            f.update(ota=r['ota'], tl=r['tl'], conf=r['conf'], src=f['src'] + '+recheck', why=r.get('why', ''))
        if f['conf'] == 'illegible':
            f['ota'] = ''; f['tl'] = ''
        f['id'] = w['id']
        out.append(f)
    # coordinator fixes taken from agents' notes (e.g. one word over two outlines): work/<id>/overrides.json
    # {"w61d": {"tl": ..., "ota": ..., "conf": ..., "note": "source"}, "w61e": {"cont": true}}
    if os.path.exists(wdir(id, 'overrides.json')):
        O = jload(wdir(id, 'overrides.json'))
        for f in out:
            if f['id'] in O:
                f.update({k: v for k, v in O[f['id']].items()})
                f['src'] += '+override'
    jsave(wdir(id, 'final.json'), out)
    from collections import Counter
    print(id, len(out), dict(Counter(f['conf'] for f in out)))
    return out


def line_tl(F):
    return ' '.join(f['tl'] if f['conf'] != 'illegible' and f['tl'] else '…' for f in F)


def neighbours(id):
    i = LINES.index(id)
    def tl(j, end):
        if not (1 <= j < len(LINES)):
            return '(none)'
        p = wdir(LINES[j], 'final.json')
        if not os.path.exists(p):
            return '(not available)'
        F = jload(p)
        F = F[-12:] if end else F[:12]
        return line_tl(F)
    return tl(i - 1, True), tl(i + 1, False)


def brief_sense(id):
    F = jload(wdir(id, 'final.json'))
    prev, nxt = neighbours(id)
    rows = '\n'.join(f'- {f["id"]}: {f["tl"] or "…"} [{f["conf"]}]' for f in F)
    s = f"""# Sense check, line {id}

Line {id} of {DOC}

The line has been read word by word, verified blind by a second reader, and disputes adjudicated. Read the assembled line in context and check that it parses as Ottoman chancery prose.

Previous line ends: … {prev}
This line:
{rows}
Next line begins: {nxt} …

Formulary: `{abspath(os.path.join(WORK, 'reference-1904.txt'))}` and:
{FORMULARY}

Task: confirm or deny that the line parses (one or two sentences on its structure: what is said, who acts). Then list **at most 5** words to re-examine because they break the grammar or the sense (give the id and what kind of word is expected there). Do not propose readings from the formulary alone; the words will be re-read from the image by someone else.

Output only JSON to `{abspath(wdir(id, 'sense.json'))}` (Write tool): `{{"parses": true|false, "structure": "...", "recheck": [{{"id": "w07", "expected": "..."}}]}}`. Then reply with one line.
"""
    open(wdir(id, 'brief_sense.md'), 'w').write(s)


def big_crops(id, ids):
    """x3 crops with more context for a fresh re-examination."""
    out = []
    W = {w['id']: w for w in jload(wdir(id, 'words.json'))}
    strip = cv2.imread(wdir(id, 'strip.png'))
    for i in ids:
        x0, y0, x1, y1 = W[i]['strip_box']
        a, b = max(0, x0 - 250), min(strip.shape[1], x1 + 250)
        c, d = max(0, y0 - 120), min(strip.shape[0], y1 + 120)
        img = strip[c:d, a:b].copy()
        cv2.rectangle(img, (x0 - a - 6, y0 - c - 6), (x1 - a + 6, y1 - c + 6), (0, 0, 230), 2)
        s = min(3.0, 2400 / img.shape[1])
        p = wdir(id, 'words', i + '_x3.png')
        cv2.imwrite(p, cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC))
        out.append(p)
    return out


def brief_recheck(id, ids):
    big_crops(id, ids)
    S = jload(wdir(id, 'sense.json')) if os.path.exists(wdir(id, 'sense.json')) else {'recheck': []}
    exp = {r['id']: r.get('expected', '') for r in S.get('recheck', [])}
    items = '\n'.join(f'- `{i}`: `{abspath(wdir(id, "words", i + "_x3.png"))}` (larger, more context) and `{abspath(wdir(id, "words", i + "_rep.png"))}` (straight from the document). Grammatically expected here: {exp.get(i, "(no hint)")}' for i in ids)
    s = f"""# Re-read {len(ids)} words, line {id}

Line {id} ({ink_of(load_data(), id)} ink) of {DOC}

Read the outlined word in each image. Each word is outlined in red.

{items}

{DEFS}

Output only JSON to `{abspath(wdir(id, 'recheck.json'))}` (Write tool): `{{"words": [{{"id": "w07", "ota": "...", "tl": "...", "conf": "...", "alts": [...], "why": "..."}}]}}`. Then reply with one line.
"""
    open(wdir(id, 'brief_recheck.md'), 'w').write(s)


def brief_group(id):
    d = load_data()
    e = entry(d, id)
    F = jload(wdir(id, 'final.json'))
    ov = sorted(glob.glob(wdir(id, 'overview_*.jpg')), key=lambda p: int(re.findall(r'_(\d+)\.jpg', p)[0]))
    rows = '\n'.join(f'- {f["id"]}: (continues the previous word; keep it in the same phrase)' if f.get('cont') else
                     f'- {f["id"]}: `{f["ota"] or "…"}` {f["tl"] or "…"} [{f["conf"]}]' for f in F)
    style = '\n'.join(f'  - {json.dumps(c["text"], ensure_ascii=False)}' for c in e['chunks'][:3])
    prev, nxt = neighbours(id)
    s = f"""# Group the words of line {id} into phrases, and translate them

Line {id} of {DOC}

Final word list, in reading order (illegible words are …):
{rows}

Previous line ends: … {prev}
Next line begins: {nxt} …

Overview images of the line with the words boxed and numbered (reading order runs from overview_1, the right end, leftwards):
{chr(10).join('- `' + abspath(p) + '`' for p in ov)}

Task:
1. Group **consecutive** words into phrases of 3 to 8 words each, cut at natural units (an izafet chain, a verb with its object, a formula, a name with its titles). The stack at the end of a line (the last words, piled up the left margin) should be one or two phrases of its own. Every word id must be in exactly one phrase, in order.
2. For each phrase write a short, literal translation into English, modern Turkish, French and Japanese, in the style of the existing translations of this document, for example:
{style}
   Use square brackets for words supplied for sense, and … where words are illegible. Do not translate words that are marked … (illegible). No question marks. Where a personal name's words are not `read`, add "(name tentative)" / "(isim belirsiz)" / "(nom incertain)" / "(名前は不確か)" after the name.
3. Also give a one-sentence summary of what the line says (English), and say whether it names a person and who.

Output only JSON to `{abspath(wdir(id, 'groups.json'))}` (Write tool):
`{{"phrases": [{{"words": ["w01", "w02m", ...], "text": {{"en": "...", "tr": "...", "fr": "...", "ja": "..."}}}}, ...], "summary": "...", "names": ["..."]}}`. Then reply with one line.
"""
    open(wdir(id, 'brief_group.md'), 'w').write(s)


if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'final':
        for id in (args or LINES[1:]):
            finalize(id)
    elif cmd == 'sense':
        for id in (args or LINES[1:]):
            brief_sense(id)
    elif cmd == 'recheck':
        for id in args:
            ids = [r['id'] for r in jload(wdir(id, 'sense.json')).get('recheck', [])][:5]
            known = {w['id'] for w in jload(wdir(id, 'words.json'))}
            ids = [i for i in ids if i in known]
            if ids:
                brief_recheck(id, ids)
            print(id, ids)
    elif cmd == 'group':
        for id in (args or LINES[1:]):
            brief_group(id)
