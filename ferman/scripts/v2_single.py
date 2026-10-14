"""Phase 6.3: rebuild the single-box polygons (davet, tugra, place) from their ink.

usage: v2_single.py [id ...]   -> work/single/<id>.json {poly}, work/single/<id>.jpg (check)
"""
import sys, os
import cv2
import numpy as np
from v2_common import *

# search window (replica px) and darkness threshold per element
WIN = {
    'davet': ((3250, 600, 4900, 1600), 18),
    'tugra': ((2800, 5900, 6400, 8300), 22),
    'place': ((300, 15000, 1900, 16650), 28),
}


def disk(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def run(id, d):
    (x0, y0, x1, y1), thr = WIN[id]
    c = np.ascontiguousarray(replica()[y0:y1, x0:x1])
    L = c.astype(np.int16).mean(2)
    bg = cv2.medianBlur(L.astype(np.uint8), 151).astype(np.int16)
    m = ((L < bg - thr)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros(n, bool)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a < 250 or (w > 10 * h and h < 22) or w > 0.95 * (x1 - x0):
            continue
        keep[i] = True
    m = keep[lab].astype(np.uint8)
    # one shape: close generously, keep the components near the current box, fill
    s = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(70))
    s = cv2.dilate(s, disk(12))
    old = np.zeros_like(s)
    for q in d['regions'][id]['polys']:
        cv2.fillPoly(old, [np.array(q, np.int32) - [x0, y0]], 1)
    n, lab2, st2, _ = cv2.connectedComponentsWithStats(s, 8)
    hold = [i for i in range(1, n) if (old & (lab2 == i)).sum() > 2000]
    s = np.isin(lab2, hold).astype(np.uint8)
    cs, _ = cv2.findContours(s, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    hull = np.vstack([cc.reshape(-1, 2) for cc in cs])
    while len(cs) > 1:   # several shapes: bridge the nearest pair
        A = cs[0].reshape(-1, 2)
        B = np.vstack([cc.reshape(-1, 2) for cc in cs[1:]])
        D = ((A[::3, None, :] - B[None, ::3, :]) ** 2).sum(-1)
        i, j = np.unravel_index(D.argmin(), D.shape)
        cv2.line(s, tuple(map(int, A[::3][i])), tuple(map(int, B[::3][j])), 1, 40)
        cs, _ = cv2.findContours(s, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnt = max(cs, key=cv2.contourArea)
    poly = cv2.approxPolyDP(cnt.astype(np.float32), 10, True).reshape(-1, 2) + [x0, y0]
    poly = [[int(a), int(b)] for a, b in poly]
    os.makedirs(os.path.join(WORK, 'single'), exist_ok=True)
    jsave(os.path.join(WORK, 'single', id + '.json'), {'poly': poly})
    v = c.copy()
    v[m > 0] = (0.5 * v[m > 0] + [0, 0, 120]).astype(np.uint8)
    for q in d['regions'][id]['polys']:
        cv2.polylines(v, [np.array(q) - [x0, y0]], True, (200, 0, 0), 3)
    cv2.polylines(v, [np.array(poly) - [x0, y0]], True, (0, 160, 0), 4)
    sc = 900 / max(v.shape[:2])
    cv2.imwrite(os.path.join(WORK, 'single', id + '.jpg'), cv2.resize(v, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA))
    print(id, len(poly), 'points')


if __name__ == '__main__':
    d = load_data()
    for id in (sys.argv[1:] or SINGLE):
        run(id, d)
