"""Phase 2: segment each strip into candidate words; crops, polygons, overview.

usage: v2_words.py [id ...]
reads  work/<id>/{strip.png, ink.png, map_x.npy, map_y.npy}, optional work/<id>/seg_fix.json
writes work/<id>/{words.json, words/wNN.png, words/wNN_ctx.png, overview_K.jpg}

seg_fix.json (from the readers' segmentation notes):
  {"merge": [["w12", "w13"], ...], "split": [{"id": "w20", "u": 3410}, ...],
   "drop": ["w05"], "pieces": {"w07": [piece ids to move to the next/prev word]}}
Merged words get the id of their first member + "m", split words get "a"/"b"
suffixes; work/<id>/id_map.json records old -> new ids.
"""
import sys, glob, os
import cv2
import numpy as np
from v2_common import *

BAND = 330        # piece centroids must lie within this distance of the centreline
MIN_AREA = 60     # smaller components are specks
MARK_AREA = 900   # pieces smaller than this are dots/marks, attached to a letter piece
MARGIN = 40
SWASH_LINES = {'nisan'}   # set the long interlaced baseline strokes aside here
SWASHES = {}


def pieces_of(id):
    m = cv2.imread(wdir(id, 'ink.png'), 0) > 0
    H = m.shape[0]
    n, lab, st, cen = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
    # pieces excluded by hand (a paper fold fused with ink): work/<id>/exclude_pieces.json
    ex = set(jload(wdir(id, 'exclude_pieces.json'))) if os.path.exists(wdir(id, 'exclude_pieces.json')) else set()
    P = []
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a < MIN_AREA or abs(cen[i][1] - H / 2) > BAND:
            continue
        if i in ex:
            lab[lab == i] = 0
            continue
        # a long swash mostly outside the band belongs to another line
        if h > 450:
            ys = np.nonzero(lab[y:y + h, x:x + w] == i)[0] + y
            if np.mean(np.abs(ys - H / 2) < BAND) < 0.6:
                continue
        if id in SWASH_LINES and w > 900:
            SWASHES.setdefault(id, []).append(int(i)); continue
        P.append({'pid': i, 'box': [int(x), int(y), int(x + w), int(y + h)], 'area': int(a),
                  'c': [float(cen[i][0]), float(cen[i][1])]})
    return P, lab


def group(P):
    big = [p for p in P if p['area'] >= MARK_AREA]
    small = [p for p in P if p['area'] < MARK_AREA]
    # attach marks: nearest big piece by u-interval distance, then v distance
    for p in big:
        p['marks'] = []
    for s in small:
        cu, cv = s['c']
        def d(b):
            x0, y0, x1, y1 = b['box']
            du = max(0, x0 - cu, cu - x1)
            dv = max(0, y0 - cv, cv - y1)
            return du + 0.5 * dv
        if big:
            b = min(big, key=d)
            if d(b) < 160:
                b['marks'].append(s)
    # reading order = descending u (u = 0 is the stack end)
    big.sort(key=lambda p: -p['box'][2])
    # Dîvânî words overlap along the line (half the gaps are negative), so gap
    # thresholds chain whole lines together. Over-segment instead: one candidate per
    # letter piece, merging only a piece that lies mostly within the span of the
    # current candidate (a stacked letter, an alif above). Readers merge the rest.
    T = 0.75
    words = []
    cur = None
    for p in big:
        if cur is not None:
            x0 = min(q['box'][0] for q in cur); x1 = max(q['box'][2] for q in cur)
            w = p['box'][2] - p['box'][0]
            inside = max(0, min(x1, p['box'][2]) - max(x0, p['box'][0])) / max(1, w)
            if inside >= T:
                cur.append(p); continue
        cur = [p]; words.append(cur)
    return words, T


def word_mask(lab, pieces, shape):
    ids = [p['pid'] for p in pieces] + [m['pid'] for p in pieces for m in p.get('marks', [])]
    x0 = min(p['box'][0] for p in pieces); x1 = max(p['box'][2] for p in pieces)
    y0 = min(p['box'][1] for p in pieces); y1 = max(p['box'][3] for p in pieces)
    for p in pieces:
        for m in p.get('marks', []):
            x0 = min(x0, m['box'][0]); x1 = max(x1, m['box'][2])
            y0 = min(y0, m['box'][1]); y1 = max(y1, m['box'][3])
    sub = np.isin(lab[y0:y1, x0:x1], ids)
    return sub, (x0, y0, x1, y1), ids


def to_replica(pts, mx, my):
    u = np.clip(pts[:, 0], 0, mx.shape[1] - 1).astype(int)
    v = np.clip(pts[:, 1], 0, mx.shape[0] - 1).astype(int)
    return np.stack([mx[v, u], my[v, u]], 1)


def polygon(sub, box, mx, my, dil=10, close=0):
    x0, y0, _, _ = box
    pad = dil + close + 4
    m = np.pad(sub.astype(np.uint8), pad)
    if close:
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * close + 1,) * 2))
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * dil + 1,) * 2))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea).reshape(-1, 2).astype(float) + [x0 - pad, y0 - pad]
    R = to_replica(c, mx, my).astype(np.float32)
    R = cv2.approxPolyDP(R.reshape(-1, 1, 2), 4, True).reshape(-1, 2)
    return [[int(round(a)), int(round(b))] for a, b in R]


def clahe(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    lab[..., 0] = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(4, 4)).apply(lab[..., 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def crop(strip, box, margin):
    x0, y0, x1, y1 = box
    H, W = strip.shape[:2]
    a, b = max(0, x0 - margin), min(W, x1 + margin)
    c, d = max(0, y0 - margin), min(H, y1 + margin)
    return strip[c:d, a:b].copy(), (a, c)


def render(id, strip, W):
    out = wdir(id, 'words')
    os.makedirs(out, exist_ok=True)
    for f in glob.glob(os.path.join(out, '*.png')):
        os.remove(f)
    for k, w in enumerate(W):
        img, _ = crop(strip, w['strip_box'], MARGIN)
        img = clahe(cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC))
        cv2.imwrite(os.path.join(out, w['id'] + '.png'), img)
        # context: one neighbour each side; word outlined
        nb = [W[j]['strip_box'] for j in (k - 1, k, k + 1) if 0 <= j < len(W)]
        box = [min(b[0] for b in nb), min(b[1] for b in nb), max(b[2] for b in nb), max(b[3] for b in nb)]
        img, (ox, oy) = crop(strip, box, MARGIN)
        img = clahe(img)
        x0, y0, x1, y1 = w['strip_box']
        cv2.rectangle(img, (x0 - ox - 6, y0 - oy - 6), (x1 - ox + 6, y1 - oy + 6), (0, 0, 230), 3)
        s = min(1.5, 1800 / img.shape[1])
        cv2.imwrite(os.path.join(out, w['id'] + '_ctx.png'), cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC))
        # the same word straight from the replica (no unrolling), its outline drawn thin
        P = np.array(w['polygon'])
        x0, y0 = np.maximum(P.min(0) - 120, 0); x1, y1 = P.max(0) + 120
        rep = np.ascontiguousarray(replica()[y0:y1, x0:x1]).copy()
        cv2.polylines(rep, [P - [x0, y0]], True, (0, 0, 230), 2)
        s = min(2.0, 1600 / max(rep.shape[:2]))
        cv2.imwrite(os.path.join(out, w['id'] + '_rep.png'), clahe(cv2.resize(rep, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)))
    overview(id, strip, W)


def overview(id, strip, W, seg=1800, ov=200):
    for f in glob.glob(wdir(id, 'overview_*.jpg')):
        os.remove(f)
    H = strip.shape[0]
    xs = [b for w in W for b in (w['strip_box'][0], w['strip_box'][2])]
    lo, hi = max(0, min(xs) - 60), min(strip.shape[1], max(xs) + 60)
    # reading order: segment 1 is the right end of the strip
    starts = list(range(hi, lo, -(seg - ov)))
    for k, b in enumerate(starts):
        a = max(lo, b - seg)
        img = strip[100:H - 100, a:b].copy()
        for j, w in enumerate(W):
            x0, y0, x1, y1 = w['strip_box']
            if x1 < a or x0 > b:
                continue
            col = [(0, 0, 220), (0, 140, 0), (200, 0, 0), (160, 0, 160)][j % 4]
            cv2.rectangle(img, (x0 - a, y0 - 100), (x1 - a, y1 - 100), col, 2)
            ty = y0 - 112 if j % 2 == 0 else y1 - 60
            cv2.putText(img, w['id'], (x0 - a + 4, max(30, min(img.shape[0] - 8, ty))), 0, 1.1, col, 3)
        cv2.imwrite(wdir(id, f'overview_{k + 1}.jpg'), img, [cv2.IMWRITE_JPEG_QUALITY, 88])
        if a == lo:
            break


def build(id, P, lab, groups, mx, my, ids=None):
    W = []
    for k, g in enumerate(groups):
        sub, box, pids = word_mask(lab, g, lab.shape)
        W.append({'id': ids[k] if ids else f'w{k + 1:02d}', 'strip_box': list(map(int, box)),
                  'pieces': [int(p) for p in pids], 'polygon': polygon(sub, box, mx, my)})
        R = np.array(W[-1]['polygon'])
        W[-1]['bbox'] = [int(R[:, 0].min()), int(R[:, 1].min()), int(R[:, 0].max()), int(R[:, 1].max())]
    return W


def apply_fix(id, W, P, lab):
    """Apply readers' segmentation corrections to an existing words.json."""
    fix = jload(wdir(id, 'seg_fix.json'))
    byid = {w['id']: w for w in W}
    order = [w['id'] for w in W]
    mapping = {}
    for grp in fix.get('merge', []):
        grp = [g for g in grp if g in byid]
        if len(grp) < 2:
            continue
        new = grp[0] + 'm'
        pieces = sum((byid[g]['pieces'] for g in grp), [])
        byid[new] = {'id': new, 'pieces': pieces}
        i = order.index(grp[0])
        for g in grp:
            order.remove(g); mapping[g] = new
        order.insert(i, new)
    for sp in fix.get('split', []):
        w = byid.get(sp['id'])
        if not w:
            continue
        pcs = w['pieces']
        cu = {p: np.nonzero(lab == p)[1].mean() for p in pcs}
        # reading order: the first part is the one at larger u
        a = [p for p in pcs if cu[p] >= sp['u']]; b = [p for p in pcs if cu[p] < sp['u']]
        if not a or not b:
            print('split had no effect', sp); continue
        i = order.index(w['id']); order.remove(w['id'])
        for suf, part in (('a', a), ('b', b)):
            byid[w['id'] + suf] = {'id': w['id'] + suf, 'pieces': part}
        order[i:i] = [w['id'] + 'a', w['id'] + 'b']
        mapping[w['id']] = [w['id'] + 'a', w['id'] + 'b']
    for dname in fix.get('drop', []):
        if dname in order:
            order.remove(dname); mapping[dname] = None
    for src, mv in fix.get('move', {}).items():   # {"w07": {"to": "w08", "u_below": 1234}}
        w = byid[src]; dst = byid[mv['to']]
        moving = [p for p in w['pieces'] if np.nonzero(lab == p)[1].mean() < mv['u_below']] if 'u_below' in mv else \
                 [p for p in w['pieces'] if np.nonzero(lab == p)[1].mean() >= mv['u_above']]
        w['pieces'] = [p for p in w['pieces'] if p not in moving]; dst['pieces'] = dst['pieces'] + moving
    return order, byid, mapping


def run(id):
    strip = cv2.imread(wdir(id, 'strip.png'))
    mx = np.load(wdir(id, 'map_x.npy')); my = np.load(wdir(id, 'map_y.npy'))
    P, lab = pieces_of(id)
    if os.path.exists(wdir(id, 'seg_fix.json')) and os.path.exists(wdir(id, 'words_auto.json')):
        W0 = jload(wdir(id, 'words_auto.json'))
        order, byid, mapping = apply_fix(id, W0, P, lab)
        bypid = {p['pid']: p for p in P}
        groups = [[{'pid': q, 'box': box_of(lab, q)} for q in byid[o]['pieces']] for o in order]
        W = build(id, P, lab, groups, mx, my, ids=order)
        jsave(wdir(id, 'id_map.json'), mapping)
    else:
        groups, T = group(P)
        W = build(id, P, lab, groups, mx, my)
        jsave(wdir(id, 'words_auto.json'), W)
        print(id, 'gap threshold', T)
    jsave(wdir(id, 'words.json'), W)
    jsave(wdir(id, 'swashes.json'), SWASHES.get(id, []))
    render(id, strip, W)
    print(id, len(W), 'words')


def box_of(lab, pid):
    ys, xs = np.nonzero(lab == pid)
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def from_reading(id, src='read1.json'):
    """Re-segment from a reader's word list: each reader word = union of its candidates.

    Writes words.json (new ids: the first candidate's id, + "m" when merged), id_map.json
    (candidate -> word id) and pass1.json (the reading, keyed by the new ids)."""
    R = jload(wdir(id, src))
    auto = {w['id']: w for w in jload(wdir(id, 'words_auto.json'))}
    sa = wdir(id, 'split_assign.json')
    if os.path.exists(sa):   # readers' splits: candidate wNN -> parts wNNa, wNNb (pieces by hand)
        for c, parts in jload(sa).items():
            for suf, pcs in parts.items():
                if pcs:
                    auto[c + suf] = {'id': c + suf, 'pieces': pcs}
            del auto[c]
    strip = cv2.imread(wdir(id, 'strip.png'))
    mx = np.load(wdir(id, 'map_x.npy')); my = np.load(wdir(id, 'map_y.npy'))
    _, lab = pieces_of(id)
    seen, groups, ids, mapping, reading = set(), [], [], {}, {}
    for w in R['words']:
        cand = [c for c in w['ids'] if c in auto and c not in seen]
        if not cand:
            print(id, 'word without candidates', w.get('tl')); continue
        seen.update(cand)
        nid = cand[0] + ('m' if len(cand) > 1 else '')
        pcs = sorted(set(p for c in cand for p in auto[c]['pieces'] if (lab == p).any()))
        groups.append([{'pid': q, 'box': box_of(lab, q)} for q in pcs]); ids.append(nid)
        for c in cand:
            mapping[c] = nid
        reading[nid] = {k: w.get(k) for k in ('ota', 'tl', 'conf', 'alts', 'why', 'flag')}
        reading[nid]['cands'] = cand
    for c in auto:
        if c not in seen:
            mapping[c] = None
    # QA fixes: a piece that belongs to a neighbouring word, {"pid": "target word id"}
    pm = wdir(id, 'piece_moves.json')
    if os.path.exists(pm):
        for pid, target in jload(pm).items():
            pid = int(pid)
            for g in groups:
                g[:] = [q for q in g if q['pid'] != pid]
            groups[ids.index(target)].append({'pid': pid, 'box': box_of(lab, pid)})
    W = build(id, None, lab, groups, mx, my, ids=ids)
    jsave(wdir(id, 'words.json'), W)
    jsave(wdir(id, 'id_map.json'), mapping)
    jsave(wdir(id, 'pass1.json'), reading)
    render(id, strip, W)
    missing = [c for c, v in mapping.items() if v is None]
    print(id, len(W), 'words;', 'unassigned/dropped:', missing)


if __name__ == '__main__':
    if sys.argv[1:2] == ['--from-reading']:
        for id in (sys.argv[2:] or LINES[1:]):
            from_reading(id)
    else:
        for id in (sys.argv[1:] or LINES):
            run(id)
