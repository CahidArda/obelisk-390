"""Phase 7: write the v2 reading into data.js (+ reading.json, reading-words.json).

usage: v2_write.py
reads  work/<line>/{final.json, groups.json, boxes.json, words.json}, work/nisan/{read1,read2,adjudicate,boxes}.json,
       work/davet/{read1,read2}.json, work/single/davet.json, work/notes.json (note / title / intro edits)
"""
import os, re, json
import cv2
import numpy as np
from v2_common import *
from v2_brief import lower, same_reading

ELL = '…'


def join_tl(parts):
    out = ''
    for p in parts:
        if not out:
            out = p
        elif p == ELL or out.endswith(ELL):
            out += ' ' + p
        elif p[:1] in "’'-‘" and not p.startswith('‘'):
            out += p
        elif out.endswith('-'):
            out += p
        else:
            out += ' ' + p
    return re.sub(r'(…\s*)+…', ELL, out).strip()


def join_ota(parts):
    return re.sub(r'(…\s*)+…', ELL, ' '.join(parts)).strip()


def box_conf(words):
    c = [w['conf'] for w in words]
    ill = sum(x == 'illegible' for x in c) / len(c)
    if all(x == 'read' for x in c):
        return 'read'
    if all(x in ('read', 'probable') for x in c):
        return 'probable'
    if ill > 0.3:
        return 'unread'
    return 'partial'


def chunk_from_words(words, text):
    shown = [w for w in words if not w.get('cont')]
    ota = join_ota([w['ota'] if w['conf'] != 'illegible' and w['ota'] else ELL for w in shown])
    tl = join_tl([w['tl'] if w['conf'] != 'illegible' and w['tl'] else ELL for w in shown])
    return {'conf': box_conf(words), 'ota': ota, 'tl': tl, 'text': text,
            'words': [{'ota': w['ota'], 'tl': w['tl'], 'conf': w['conf'], 'poly': w.get('poly')} for w in words]}


def bbox(polys):
    xs = [p[0] for q in polys for p in q]; ys = [p[1] for q in polys for p in q]
    return [min(xs), min(ys), max(xs), max(ys)]


def line(d, id, allwords):
    F = {f['id']: f for f in jload(wdir(id, 'final.json'))}
    Wp = {w['id']: w['polygon'] for w in jload(wdir(id, 'words.json'))}
    G = jload(wdir(id, 'groups.json'))['phrases']
    B = jload(wdir(id, 'boxes.json'))
    assert [b['words'] for b in B] == [g['words'] for g in G], id + ': boxes.json is stale, rerun v2_boxes.py'
    chunks = []
    for g in G:
        words = [dict(F[i], poly=Wp[i]) for i in g['words']]
        chunks.append(chunk_from_words(words, g['text']))
    polys = [b['poly'] for b in B]
    d['regions'][id] = {'polys': polys, 'bbox': bbox(polys)}
    entry(d, id)['chunks'] = chunks
    allwords[id] = [dict(F[w['id']], poly=Wp[w['id']]) for w in jload(wdir(id, 'words.json'))]


def composition_words(id):
    """Words of a composition read as a whole: first reading, blind second reading, adjudication."""
    a = jload(os.path.join(WORK, id, 'read1.json'))['words']
    b = jload(os.path.join(WORK, id, 'read2.json'))['words']
    adj = {}
    if os.path.exists(os.path.join(WORK, id, 'adjudicate.json')):
        adj = {w['n']: w for w in jload(os.path.join(WORK, id, 'adjudicate.json'))['words']}
    out = []
    for n, (x, y) in enumerate(zip(a, b)):
        if n in adj:
            z = adj[n]; w = {'ota': z['ota'], 'tl': z['tl'], 'conf': z['conf'], 'src': 'adjudicated:' + z['choice']}
        elif same_reading(x, y):
            w = {'ota': x['ota'], 'tl': x['tl'], 'conf': lower(x['conf'], y['conf']), 'src': 'agreed'}
        else:
            raise SystemExit(f'{id} word {n}: readings differ and no adjudication')
        w['part'] = x.get('part', 0)
        out.append(w)
    ov = os.path.join(WORK, id, 'overrides.json')   # transliteration joins, keyed by word index
    if os.path.exists(ov):
        for n, o in jload(ov).items():
            out[int(n)].update({k: v for k, v in o.items() if k != 'note'})
    return out


def main():
    d = load_data()
    notes = jload(os.path.join(WORK, 'notes.json'))
    allwords = {}
    for id in LINES[1:]:
        line(d, id, allwords)
    # nişan: two parts, boxes from its ink, words from the composition reading
    NW = composition_words('nisan')
    NB = jload(wdir('nisan', 'boxes.json'))
    NG = jload(wdir('nisan', 'groups_text.json'))
    nchunks = []
    for k in range(2):
        ws = [w for w in NW if w['part'] == k]
        nchunks.append(chunk_from_words(ws, NG['phrases'][k]['text']))
    entry(d, 'nisan')['chunks'] = nchunks
    d['regions']['nisan'] = {'polys': [b['poly'] for b in NB], 'bbox': bbox([b['poly'] for b in NB])}
    allwords['nisan'] = NW
    # davet: one box, new outline from its ink; text unchanged (both readers agree with it)
    DW = composition_words('davet')
    old = entry(d, 'davet')['chunks'][0]
    entry(d, 'davet')['chunks'] = [chunk_from_words(DW, old['text'])]
    dp = jload(os.path.join(WORK, 'single', 'davet.json'))['poly']
    d['regions']['davet'] = {'polys': [dp], 'bbox': bbox([dp])}
    allwords['davet'] = DW
    # place: keep its outline but cut away line 7's boxes where they overlap
    pp = np.array(d['regions']['place']['polys'][0], np.int32)
    x0, y0 = pp.min(0) - 10; x1, y1 = pp.max(0) + 10
    m = np.zeros((y1 - y0, x1 - x0), np.uint8); cv2.fillPoly(m, [pp - [x0, y0]], 1)
    for q in d['regions']['l7']['polys']:
        o = np.zeros_like(m); cv2.fillPoly(o, [np.array(q, np.int32) - [x0, y0]], 1)
        m[cv2.dilate(o, np.ones((25, 25), np.uint8)) > 0] = 0
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    c = cv2.approxPolyDP(c.astype(np.float32), 6, True).reshape(-1, 2) + [x0, y0]
    pl = [[int(a), int(b)] for a, b in c]
    d['regions']['place'] = {'polys': [pl], 'bbox': bbox([pl])}
    # entry-level conf = worst box conf; notes / titles / group intros from notes.json
    rank = {'read': 3, 'probable': 2, 'partial': 1, 'unread': 0}
    for e in d['entries']:
        e['conf'] = min((ch['conf'] for ch in e['chunks']), key=lambda c: rank[c])
        if e['id'] == 'l7' or e['id'] == 'place' or e['id'] == 'tugra':
            pass
        for k in ('note', 'title'):
            if e['id'] in notes.get(k, {}):
                e[k] = notes[k][e['id']]
    for g in d['groups']:
        if g['id'] in notes.get('intro', {}):
            g['intro'] = notes['intro'][g['id']]
    save_data(d)
    # mirrors
    # reading.json keeps its shape: {groups, chunks: {id: [chunk]}}, chunks without the word list
    R = {'groups': d['groups'],
         'chunks': {e['id']: [{k: v for k, v in c.items() if k != 'words'} for c in e['chunks']] for e in d['entries']}}
    with open(READING, 'w', encoding='utf-8') as f:
        f.write(json.dumps(R, ensure_ascii=False, indent=0))
    jsave(os.path.join(HERE, 'reading-words.json'), allwords)
    from collections import Counter
    print(Counter(ch['conf'] for e in d['entries'] for ch in e['chunks']))


if __name__ == '__main__':
    main()
