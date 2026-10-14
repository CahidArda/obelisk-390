"""Phase 1: curved centreline, unrolled strip and ink mask for each text line.

usage: v2_lines.py [id ...]     (default: all of v2_common.LINES)
writes work/<id>/{strip.png, map_x.npy, map_y.npy, ink.png, strip_preview.jpg, centreline.json}

Strip pixel (u, v) maps to replica (map_x[v, u], map_y[v, u]). The strip reads
right to left like the text: u = 0 is the far end of the line (top of the stack).
"""
import sys, math
import cv2
import numpy as np
from scipy.interpolate import splprep, splev
from v2_common import *

HALF = 500        # strip half-height (px) around the centreline
STEP = 4          # centreline resampling step

# Per-line adjustments, replica px. extend: (right, left) extension of the curve past
# the outer boxes; drop: anchor indices to ignore; add: extra anchors (inserted by
# arclength order); shift: move the whole curve along its normal (+ = down).
ADJ = {
    # stacks: centroid anchors left of `cut` are replaced by hand-placed points up the stack
    'l1': {'cut': 1900, 'stack': [(1760, 9440), (1440, 9320), (1120, 9160), (880, 8960), (760, 8800), (720, 8700)]},
    'l2': {'cut': 2300, 'stack': [(2240, 10360), (1320, 10240), (1080, 10160), (920, 9920), (800, 9680), (720, 9560)]},
    'l3': {'cut': 1900, 'stack': [(1840, 11440), (1520, 11360), (1200, 11160), (920, 10920), (720, 10720), (640, 10560)]},
    'l4': {'cut': 2100, 'stack': [(1900, 12450), (1320, 12300), (1000, 12080), (800, 11800), (660, 11450)]},
    'l5': {'cut': 2000, 'stack': [(1880, 13380), (1400, 13100), (1000, 12890), (760, 12720), (640, 12480), (600, 12270)]},
    'l6': {'cut': 1900, 'stack': [(1800, 14400), (1280, 14160), (920, 13920), (680, 13680), (560, 13400)]},
    'l7': {'cut': 1400, 'stack': [(1320, 15000), (960, 14880), (800, 14680), (680, 14480), (600, 14360)]},
}


def axis_ends(poly):
    """The two ends of a box's long axis: (right end, left end) in reading order."""
    P = np.array(poly, float)
    c = P.mean(0)
    _, _, vt = np.linalg.svd(P - c, full_matrices=False)
    ax = vt[0]
    a = (P - c) @ ax
    e1, e2 = c + a.min() * ax, c + a.max() * ax
    # reading order goes right-to-left, then up: the "first" end is the lower-right one
    key = lambda p: p[0] - p[1]
    return (e1, e2) if key(e1) > key(e2) else (e2, e1)


def anchors(polys, adj):
    """Box centroids in reading order, plus the outer ends of the first and last boxes."""
    cs = np.array([np.array(p, float).mean(0) for p in polys])
    first = max(axis_ends(polys[0]), key=lambda q: q[0])    # lines start at the right
    last = min(axis_ends(polys[-1]), key=lambda q: q[1])    # and end at the top of the stack
    pts = np.vstack([first, cs, last])
    if adj.get('drop'):
        pts = np.delete(pts, adj['drop'], 0)
    if adj.get('cut'):
        pts = np.vstack([pts[:-1][pts[:-1, 0] > adj['cut']], np.array(adj['stack'], float)])
    if adj.get('anchors'):
        pts = np.array(adj['anchors'], float)
    ext_r, ext_l = adj.get('extend', (150, 220))
    d0 = pts[0] - pts[1]; d0 /= np.linalg.norm(d0)
    d1 = pts[-1] - pts[-2]; d1 /= np.linalg.norm(d1)
    return np.vstack([pts[0] + d0 * ext_r, pts, pts[-1] + d1 * ext_l])


def centreline(pts, smooth):
    # drop near-duplicate anchors (touching boxes) so the spline stays well-posed
    keep = [0]
    for i in range(1, len(pts)):
        if np.linalg.norm(pts[i] - pts[keep[-1]]) > 60:
            keep.append(i)
    pts = pts[keep]
    tck, _ = splprep([pts[:, 0], pts[:, 1]], s=smooth * len(pts), k=min(3, len(pts) - 1))
    t = np.linspace(0, 1, 20000)
    x, y = splev(t, tck)
    seg = np.hypot(np.diff(x), np.diff(y))
    s = np.concatenate([[0], np.cumsum(seg)])
    L = s[-1]
    si = np.arange(0, L, STEP)
    xs, ys = np.interp(si, s, x), np.interp(si, s, y)
    return np.stack([xs, ys], 1)


def strip_maps(C, half):
    """C: centreline in reading order (right end first), STEP apart."""
    T = np.gradient(C, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    T = cv2.GaussianBlur(T.reshape(-1, 1, 2).astype(np.float32), (1, 0), sigmaX=0, sigmaY=6).reshape(-1, 2)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    N = np.stack([T[:, 1], -T[:, 0]], 1)  # "down" for text written along T
    n = len(C)
    L = (n - 1) * STEP
    u = np.arange(0, int(L))               # strip column; u=0 is the far (left/stack) end
    s = (L - u) / STEP                     # index along C (C[0] is the right end)
    cx = np.interp(s, np.arange(n), C[:, 0]); cy = np.interp(s, np.arange(n), C[:, 1])
    nx = np.interp(s, np.arange(n), N[:, 0]); ny = np.interp(s, np.arange(n), N[:, 1])
    v = np.arange(-half, half)[:, None]
    mx = (cx[None, :] + v * nx[None, :]).astype(np.float32)
    my = (cy[None, :] + v * ny[None, :]).astype(np.float32)
    return mx, my


def remap(im, mx, my):
    x0 = max(0, int(mx.min()) - 2); x1 = min(im.shape[1], int(mx.max()) + 3)
    y0 = max(0, int(my.min()) - 2); y1 = min(im.shape[0], int(my.max()) + 3)
    sub = np.ascontiguousarray(im[y0:y1, x0:x1])
    # remap is limited to 32767 px per side; strips are well under that
    return cv2.remap(sub, mx - x0, my - y0, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                     borderValue=(235, 235, 235))


def ink_mask(strip, ink):
    b, g, r = [strip[..., i].astype(np.int16) for i in range(3)]
    L = (b + g + r) // 3
    bg = cv2.medianBlur(L.astype(np.uint8), 101).astype(np.int16)
    red = (r - g) > 40
    if 'red' in ink and 'black' not in ink and 'gold' not in ink:
        m = red
    elif ink == 'black':
        m = (L < bg - 28) & ((r - g) < 30)
    else:  # nisan: gold + red; take red and darker gold strokes
        m = red | (L < bg - 28)
    m = m.astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return m


def drop_creases(m, text_u):
    """Remove long thin components (paper creases) and anything past the text."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros(n, bool)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a < 12:
            continue
        if (w > 10 * h and h < 22) or (h > 10 * w and w < 22):
            continue
        if x + w < text_u[0] or x > text_u[1]:
            continue
        keep[i] = True
    return keep[lab].astype(np.uint8)


def preview(strip, m, path, scale=0.25):
    p = strip.copy()
    p[m > 0] = (0.4 * p[m > 0] + 0.6 * np.array([255, 120, 0])).astype(np.uint8)
    cv2.line(p, (0, p.shape[0] // 2), (p.shape[1], p.shape[0] // 2), (0, 200, 0), 2)
    for u in range(0, p.shape[1], 500):
        cv2.putText(p, str(u), (u, 40), 0, 1.4, (0, 0, 255), 3)
    cv2.imwrite(path, cv2.resize(p, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA),
                [cv2.IMWRITE_JPEG_QUALITY, 88])


def run(id, d):
    adj = ADJ.get(id, {})
    pts = anchors(d['regions'][id]['polys'], adj)
    C = centreline(pts, adj.get('smooth', 100))
    if adj.get('shift'):
        T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1, keepdims=True)
        C = C + adj['shift'] * np.stack([T[:, 1], -T[:, 0]], 1)
    half = adj.get('half', HALF)
    mx, my = strip_maps(C, half)
    strip = remap(replica(), mx, my)
    m = ink_mask(strip, ink_of(d, id))
    m = drop_creases(m, adj.get('text_u', (0, strip.shape[1])))
    cv2.imwrite(wdir(id, 'strip.png'), strip)
    cv2.imwrite(wdir(id, 'ink.png'), m * 255)
    np.save(wdir(id, 'map_x.npy'), mx); np.save(wdir(id, 'map_y.npy'), my)
    jsave(wdir(id, 'centreline.json'), {'anchors': pts.round(1).tolist(), 'curve': C[::10].round(1).tolist()})
    preview(strip, m, wdir(id, 'strip_preview.jpg'))
    print(id, 'strip', strip.shape[1], 'x', strip.shape[0])


if __name__ == '__main__':
    d = load_data()
    for id in (sys.argv[1:] or LINES):
        run(id, d)
