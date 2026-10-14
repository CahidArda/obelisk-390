"""Nişan: rebuild its two boxes (part 0 right/gold, part 1 left/red) from the ink, in replica coordinates.

The nişan is an interlaced composition read as a whole (Phase 3 on composition crops), and its
strip folds at the left end, so its boxes are built here directly on the replica: ink components
are assigned to the part whose current box holds their centroid, then each part is closed into
one outline. Validated like the line boxes (own-ink coverage, foreign ink, overlap).
usage: v2_nisan.py   -> work/nisan/boxes.json, work/nisan/boxes.jpg
"""
import os
import cv2
import numpy as np
from v2_common import *

WIN = (250, 7850, 3150, 8640)
RED = 35   # median R-G above this is red ink


def disk(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def bridge(s):
    cs, _ = cv2.findContours(s, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    while len(cs) > 1:
        A = cs[0].reshape(-1, 2); B = np.vstack([c.reshape(-1, 2) for c in cs[1:]])
        D = ((A[::3, None, :] - B[None, ::3, :]) ** 2).sum(-1)
        i, j = np.unravel_index(D.argmin(), D.shape)
        cv2.line(s, tuple(map(int, A[::3][i])), tuple(map(int, B[::3][j])), 1, 30)
        cs, _ = cv2.findContours(s, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return cs[0]


if __name__ == '__main__':
    d = load_data()
    x0, y0, x1, y1 = WIN
    c = np.ascontiguousarray(replica()[y0:y1, x0:x1])
    b, g, r = [c[..., i].astype(np.int16) for i in range(3)]
    L = (b + g + r) // 3
    bg = cv2.medianBlur(L.astype(np.uint8), 101).astype(np.int16)
    m = (((r - g) > 40) | (L < bg - 24)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    polys = [np.array(p, np.int32) - [x0, y0] for p in d['regions']['nisan']['polys']]
    own = [np.zeros(m.shape, bool), np.zeros(m.shape, bool)]
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a < 60 or w > 1400 or (w > 10 * h and h < 25):
            continue   # specks, the paper fold under the composition, creases
        ins = [cv2.pointPolygonTest(p, (float(cen[i][0]), float(cen[i][1])), True) for p in polys]
        if max(ins) < -60:
            continue   # outside both parts: tuğra arms, the line above
        if np.hypot(w, h) > 200:
            cc, _ = cv2.findContours((lab[y:y + h, x:x + w] == i).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if 2 * a / max(1.0, sum(cv2.arcLength(q, True) for q in cc)) < 8:
                continue   # hairlines of the tuğra and ruled lines, not letters
        # gold is the imperial sign (part 0), red is God’s help (part 1): split by colour
        rg = float(np.median((r - g)[lab == i]))
        own[1 if rg > RED else 0] |= lab == i
    # a red letter can touch a gold sweep and form one component: split those by pixel colour
    allink = own[0] | own[1]
    rb = (own[0] & ((r - g) > RED)).astype(np.uint8)
    nb, bl, bst, _ = cv2.connectedComponentsWithStats(rb, 8)
    blob = np.isin(bl, [j for j in range(1, nb) if bst[j][4] >= 300])
    blob = (cv2.dilate(blob.astype(np.uint8), disk(4)) > 0) & own[0]
    own = [own[0] & ~blob, own[1] | blob]
    shapes = []
    for k in range(2):
        s = cv2.morphologyEx(own[k].astype(np.uint8), cv2.MORPH_CLOSE, disk(40))
        s = cv2.dilate(s, disk(10))
        shapes.append(s)
    # the right part keeps contested space; the left part keeps its own ink
    keep1 = cv2.dilate(own[1].astype(np.uint8), disk(4)) > 0
    shapes[1] = ((shapes[1] > 0) & ~(shapes[0] > 0) | keep1).astype(np.uint8)
    shapes[0] = ((shapes[0] > 0) & ~(keep1 & ~(cv2.dilate(own[0].astype(np.uint8), disk(4)) > 0))).astype(np.uint8)
    boxes = []
    for k in range(2):
        cnt = bridge(shapes[k].copy())
        P = cv2.approxPolyDP(cnt.astype(np.float32), 5, True).reshape(-1, 2) + [x0, y0]
        boxes.append({'part': k, 'poly': [[int(a), int(b)] for a, b in P]})
    # validate
    R = []
    for bx in boxes:
        q = np.zeros(m.shape, np.uint8); cv2.fillPoly(q, [np.array(bx['poly']) - [x0, y0]], 1); R.append(q > 0)
    for k in range(2):
        cov = R[k][own[k]].mean(); fr = (R[k] & own[1 - k]).sum() / R[k].sum()
        ov = (R[0] & R[1]).sum() / min(R[0].sum(), R[1].sum())
        print(f'  nisan.{k} own-ink {cov * 100:5.1f}%  foreign {fr * 100:4.1f}%  overlap {ov * 100:4.1f}%  '
              f'{"ok" if cov >= .97 and fr <= .03 and ov <= .02 else "FAIL"}')
    jsave(wdir('nisan', 'boxes.json'), boxes)
    v = c.copy()
    v[own[0]] = (0, 160, 0); v[own[1]] = (200, 0, 0)
    for bx, col in zip(boxes, [(0, 120, 0), (160, 0, 0)]):
        cv2.polylines(v, [np.array(bx['poly']) - [x0, y0]], True, col, 4)
    cv2.imwrite(wdir('nisan', 'boxes.jpg'), cv2.resize(v, None, fx=0.35, fy=0.35, interpolation=cv2.INTER_AREA))
