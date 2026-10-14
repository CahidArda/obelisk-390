"""Phase 8: QA renders and checks for the v2 reading.

usage: v2_qa.py render   -> work/qa/<id>.jpg (region, boxes numbered), work/qa/<id>_<i>.png (each box,
                            straightened, outside of the box dimmed), work/qa/boxes.md (each box's ota / tl)
       v2_qa.py check    -> structural checks on data.js
"""
import sys, os, re
import cv2
import numpy as np
from v2_common import *

QA = os.path.join(WORK, 'qa')
COLS = [(0, 0, 220), (0, 140, 0), (200, 0, 0), (170, 0, 170)]


def poly_mask_in_strip(id, poly):
    mx = np.load(wdir(id, 'map_x.npy')); my = np.load(wdir(id, 'map_y.npy'))
    P = np.array(poly, np.int32)
    x0, y0 = P.min(0) - 2; x1, y1 = P.max(0) + 2
    r = np.zeros((y1 - y0, x1 - x0), np.uint8); cv2.fillPoly(r, [P - [x0, y0]], 255)
    m = cv2.remap(r, (mx - x0).astype(np.float32), (my - y0).astype(np.float32), cv2.INTER_NEAREST, borderValue=0)
    return m > 0


def render(d):
    os.makedirs(QA, exist_ok=True)
    im = replica()
    md = []
    for e in d['entries']:
        id = e['id']; reg = d['regions'][id]
        x0, y0, x1, y1 = reg['bbox']; pad = 150
        X0, Y0 = max(0, x0 - pad), max(0, y0 - pad)
        v = np.ascontiguousarray(im[Y0:y1 + pad, X0:x1 + pad]).copy()
        for i, q in enumerate(reg['polys']):
            Q = np.array(q) - [X0, Y0]
            cv2.polylines(v, [Q], True, COLS[i % 4], 6)
            c = Q.mean(0).astype(int)
            cv2.putText(v, str(i), (int(c[0]), int(c[1])), 0, 4, COLS[i % 4], 10)
        s = min(1.0, 2400 / v.shape[1])
        cv2.imwrite(os.path.join(QA, f'{id}.jpg'), cv2.resize(v, None, fx=s, fy=s, interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 85])
        md.append(f'## {id}')
        for i, (q, ch) in enumerate(zip(reg['polys'], e['chunks'])):
            md.append(f'- `{id}_{i}.png` [{ch["conf"]}]  ota: {ch["ota"]}  |  tl: {ch["tl"]}')
            if os.path.exists(wdir(id, 'strip.png')) and id != 'nisan':
                strip = cv2.imread(wdir(id, 'strip.png'))
                m = poly_mask_in_strip(id, q)
                ys, xs = np.nonzero(m)
                a, b = max(0, xs.min() - 60), min(strip.shape[1], xs.max() + 60)
                c0, c1 = max(0, ys.min() - 60), min(strip.shape[0], ys.max() + 60)
                crop = strip[c0:c1, a:b].copy(); mm = m[c0:c1, a:b]
                crop[~mm] = (crop[~mm] * 0.35 + 165).astype(np.uint8)
                cs, _ = cv2.findContours(mm.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                cv2.drawContours(crop, cs, -1, (0, 0, 220), 2)
            else:
                Q = np.array(q)
                qx0, qy0 = np.maximum(Q.min(0) - 60, 0); qx1, qy1 = Q.max(0) + 60
                crop = np.ascontiguousarray(im[qy0:qy1, qx0:qx1]).copy()
                mm = np.zeros(crop.shape[:2], np.uint8); cv2.fillPoly(mm, [Q - [qx0, qy0]], 1); mm = mm > 0
                crop[~mm] = (crop[~mm] * 0.35 + 165).astype(np.uint8)
                cv2.polylines(crop, [Q - [qx0, qy0]], True, (0, 0, 220), 2)
            s = min(1.5, 1800 / crop.shape[1], 1400 / crop.shape[0])
            cv2.imwrite(os.path.join(QA, f'{id}_{i}.png'), cv2.resize(crop, None, fx=s, fy=s, interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC))
        md.append('')
    open(os.path.join(QA, 'boxes.md'), 'w').write('\n'.join(md))
    print('rendered', sum(len(e['chunks']) for e in d['entries']), 'boxes')


def check(d):
    bad = []
    for e in d['entries']:
        id = e['id']
        P, C = d['regions'][id]['polys'], e['chunks']
        if len(P) != len(C):
            bad.append(f'{id}: {len(P)} polys vs {len(C)} chunks')
        for i, c in enumerate(C):
            for k in ('ota', 'tl'):
                if re.search(r'\(؟\)|\[\?\]|\?|؟', c[k]):
                    bad.append(f'{id}.{i} {k} has a question mark: {c[k]}')
            for lang in ('en', 'tr', 'fr', 'ja'):
                t = c['text'].get(lang, '')
                if not t.strip():
                    bad.append(f'{id}.{i} missing {lang}')
                if '?' in t or '？' in t:
                    bad.append(f'{id}.{i} {lang} has a question mark')
            if c['conf'] not in ('read', 'probable', 'partial', 'unread'):
                bad.append(f'{id}.{i} conf {c["conf"]}')
    print('\n'.join(bad) if bad else 'all checks passed')
    return not bad


if __name__ == '__main__':
    d = load_data()
    if sys.argv[1] == 'render':
        render(d)
    else:
        sys.exit(0 if check(d) else 1)
