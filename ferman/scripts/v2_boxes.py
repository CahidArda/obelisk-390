"""Phase 6: build each box's polygon from its words, then validate.

usage: v2_boxes.py [id ...]
reads  work/<id>/{words.json, groups.json, strip ink + maps}
writes work/<id>/boxes.json  [{words: [ids], poly: [[x, y], ...]}] in reading order
prints the validation table (own-ink coverage, foreign ink, overlap).

groups.json: {"phrases": [{"words": ["w01", "w02m", ...], ...}, ...]}
"""
import sys
import cv2
import numpy as np
from v2_common import *
from v2_words import pieces_of, to_replica

CLOSE = 25     # closing radius that turns a phrase's words into one shape
DIL = 10       # margin around the ink
KEEP = 4       # own ink is always kept within this radius, even against a neighbour
SPECK = 60     # a separate component with less own ink than this is not bridged into the box
BIG = 1200     # components with this much ink always belong; smaller ones only within NEAR px of them
NEAR = 90
SMOOTH = 7     # px, rounds the traced outline
MID = 700      # mid-size pieces (a detached letter) join from up to 300 px away
FAINT_NEAR = 60  # faint unowned writing joins the nearest box within this distance


def disk(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def word_masks(id, W, lab):
    return {w['id']: np.isin(lab, w['pieces']) for w in W}


def bridge(m, own):
    """Join the components of m along the strip (consecutive in u) so a phrase is one shape."""
    n, cl, st, cen = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
    if n <= 2:
        return m
    comps = sorted(range(1, n), key=lambda i: cen[i][0])
    out = m.astype(np.uint8).copy()
    for a, b in zip(comps, comps[1:]):
        ya, xa = np.nonzero(cl == a); yb, xb = np.nonzero(cl == b)
        # nearest pair between the right edge of a and the left edge of b (sampled)
        A = np.stack([xa, ya], 1)[::7]; B = np.stack([xb, yb], 1)[::7]
        D = ((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)
        i, j = np.unravel_index(D.argmin(), D.shape)
        cv2.line(out, tuple(map(int, A[i])), tuple(map(int, B[j])), 1, 2 * CLOSE)
    return out > 0


def faint_mask(id, ink):
    """Like the strip's ink mask, with lower thresholds, inside the line's band."""
    st = cv2.imread(wdir(id, 'strip.png')).astype(np.int16)
    b, g, r = st[..., 0], st[..., 1], st[..., 2]
    L = (b + g + r) // 3
    bg = cv2.medianBlur(L.astype(np.uint8), 101).astype(np.int16)
    m = (r - g) > 26 if ink == 'red' else (L < bg - 18) & ((r - g) < 30)
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    band = np.zeros_like(m); H = m.shape[0]; band[H // 2 - 300:H // 2 + 300] = True
    return m & band


def build_line(id, groups=None):
    W = jload(wdir(id, 'words.json'))
    byid = {w['id']: w for w in W}
    G = groups or jload(wdir(id, 'groups.json'))['phrases']
    _, lab = pieces_of(id)
    mx = np.load(wdir(id, 'map_x.npy')); my = np.load(wdir(id, 'map_y.npy'))
    if id == 'nisan':
        sw = jload(wdir(id, 'swashes.json'))
    WM = word_masks(id, W, lab)
    own = []
    for g in G:
        m = np.zeros(lab.shape, bool)
        for wid in g['words']:
            m |= WM[wid]
        if id == 'nisan' and g.get('swashes'):
            m |= np.isin(lab, g['swashes'])
        own.append(m)
    words_ink = [m.copy() for m in own]   # validation scores the words' ink only
    # faint writing below the ink threshold (faded red, hairlines) belongs to no word; give each
    # faint component that touches no word to the box whose ink is nearest, within FAINT_NEAR px
    if id != 'nisan':
        faint = faint_mask(id, ink_of(load_data(), id)) & ~(lab > 0)
        n, fl, fst, _ = cv2.connectedComponentsWithStats(faint.astype(np.uint8), 8)
        dists = [cv2.distanceTransform((~m).astype(np.uint8), cv2.DIST_L2, 3) for m in own]
        # QA fixes: faint writing between two boxes, given to one by strip u-range {"box": [[u0, u1]]}
        fa = jload(wdir(id, 'faint_assign.json')) if os.path.exists(wdir(id, 'faint_assign.json')) else {}
        for i in range(1, n):
            cu = fst[i][0] + fst[i][2] / 2
            hit = [int(k) for k, rs in fa.items() for u0, u1 in rs if u0 <= cu <= u1]
            if hit and fst[i][4] >= 30:
                own[hit[0]] |= fl == i
                continue
            if fst[i][4] < 80 or fst[i][4] > 2500:
                continue
            c = fl == i
            d = [float(dd[c].min()) for dd in dists]
            k = int(np.argmin(d))
            second = sorted(d)[1] if len(d) > 1 else 1e9
            if d[k] < FAINT_NEAR and second > 2 * d[k] + 30:
                own[k] |= c
    shapes = []
    for k, m in enumerate(own):
        s = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, disk(CLOSE)) > 0
        s = cv2.dilate(s.astype(np.uint8), disk(DIL)) > 0
        # stray specks far from the text would pull long bridges out over bare paper: leave them out
        n, cl, _, _ = cv2.connectedComponentsWithStats(s.astype(np.uint8), 8)
        if n > 2:
            inkc = np.bincount(cl[m], minlength=n)
            big = [i for i in range(1, n) if inkc[i] >= BIG] or [int(np.argmax(inkc[1:])) + 1]
            dist = cv2.distanceTransform((~np.isin(cl, big)).astype(np.uint8), cv2.DIST_L2, 3)
            near = [i for i in range(1, n) if i not in big and inkc[i] >= SPECK and (dist[cl == i].min() < NEAR or (inkc[i] >= MID and dist[cl == i].min() < 300))]
            s = np.isin(cl, big + near)
        s = bridge(s, m)
        shapes.append(s)
    # shrink overlaps away from the other boxes' ink
    for k in range(len(shapes)):
        others = np.zeros(lab.shape, bool)
        for j, m in enumerate(own):
            if j != k:
                others |= m
        keep = (cv2.dilate(own[k].astype(np.uint8), disk(KEEP)) > 0) & shapes[k]
        s = shapes[k] & ~(cv2.dilate(others.astype(np.uint8), disk(6)) > 0) | keep
        # earlier boxes win the contested space between two boxes
        for j in range(k):
            s &= ~shapes[j] | keep
        shapes[k] = s
    boxes = []
    for k, s in enumerate(shapes):
        s = cv2.morphologyEx(s.astype(np.uint8), cv2.MORPH_CLOSE, disk(3))
        s = ((cv2.GaussianBlur(s.astype(np.float32), (0, 0), SMOOTH) > 0.5) | (own[k] & (s > 0))).astype(np.uint8)   # round the outline
        n, cl, st, _ = cv2.connectedComponentsWithStats(s, 8)
        if n > 2:   # keep the components holding own ink; bridge them
            hold = [i for i in range(1, n) if (own[k] & (cl == i)).any()]
            s = np.isin(cl, hold)
            s = bridge(s, own[k]).astype(np.uint8)
        cs, _ = cv2.findContours(s.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        c = max(cs, key=cv2.contourArea).reshape(-1, 2).astype(float)
        R = to_replica(c, mx, my).astype(np.float32)
        R = cv2.approxPolyDP(R.reshape(-1, 1, 2), 4, True).reshape(-1, 2)
        boxes.append({'words': G[k]['words'], 'poly': [[int(round(a)), int(round(b))] for a, b in R]})
    jsave(wdir(id, 'boxes.json'), boxes)
    return boxes, words_ink, mx, my


def raster(poly, x0, y0, w, h):
    m = np.zeros((h, w), np.uint8)
    cv2.fillPoly(m, [np.array(poly, np.int32) - [x0, y0]], 1)
    return m > 0


def validate(id, boxes, own, mx, my):
    ok = True
    allx = [p[0] for b in boxes for p in b['poly']]; ally = [p[1] for b in boxes for p in b['poly']]
    x0, y0 = min(allx) - 5, min(ally) - 5
    w, h = max(allx) - x0 + 5, max(ally) - y0 + 5
    R = [raster(b['poly'], x0, y0, w, h) for b in boxes]
    pts = []
    for m in own:
        v, u = np.nonzero(m)
        X = np.clip(np.round(mx[v, u] - x0).astype(int), 0, w - 1)
        Y = np.clip(np.round(my[v, u] - y0).astype(int), 0, h - 1)
        pts.append((X, Y))
    rows = []
    for k, b in enumerate(boxes):
        X, Y = pts[k]
        cov = R[k][Y, X].mean() if len(X) else 1.0
        foreign = 0
        for j in range(len(boxes)):
            if j != k:
                Xo, Yo = pts[j]
                foreign += len(set(zip(Xo[R[k][Yo, Xo]], Yo[R[k][Yo, Xo]])))
        area = R[k].sum()
        fr = foreign / max(1, area)
        ov = max([(R[k] & R[j]).sum() / max(1, min(R[k].sum(), R[j].sum())) for j in range(len(boxes)) if j != k] or [0])
        good = cov >= 0.97 and fr <= 0.03 and ov <= 0.02
        ok &= good
        rows.append(f'  {id}.{k:<2} words {len(b["words"]):>2}  own-ink {cov * 100:5.1f}%  foreign {fr * 100:4.1f}%  overlap {ov * 100:4.1f}%  {"ok" if good else "FAIL"}')
    # every word in exactly one box
    W = [w['id'] for w in jload(wdir(id, 'words.json'))]
    used = [x for b in boxes for x in b['words']]
    if sorted(used) != sorted(W):
        ok = False
        rows.append(f'  {id}: words not in exactly one box: missing {sorted(set(W) - set(used))}, repeated {sorted(set(x for x in used if used.count(x) > 1))}')
    print('\n'.join(rows))
    return ok


if __name__ == '__main__':
    allok = True
    for id in (sys.argv[1:] or LINES):
        boxes, own, mx, my = build_line(id)
        allok &= validate(id, boxes, own, mx, my)
    print('ALL OK' if allok else 'SOME FAILED')
