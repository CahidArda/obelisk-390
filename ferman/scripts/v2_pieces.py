"""Show the pieces inside candidate words, to resolve readers' splits.

usage: v2_pieces.py <id> wNN [wNN ...]   -> work/<id>/pieces_wNN.png (pieces coloured and numbered)
The piece assignment goes into work/<id>/split_assign.json: {"wNN": {"a": [pid, ...], "b": [...]}}
"""
import sys
import cv2
import numpy as np
from v2_common import *
from v2_words import pieces_of, crop

COLS = [(0, 0, 230), (0, 150, 0), (220, 0, 0), (170, 0, 170), (0, 140, 200), (120, 80, 0)]

if __name__ == '__main__':
    id = sys.argv[1]
    auto = {w['id']: w for w in jload(wdir(id, 'words_auto.json'))}
    strip = cv2.imread(wdir(id, 'strip.png'))
    _, lab = pieces_of(id)
    for c in sys.argv[2:]:
        w = auto[c]
        img, (ox, oy) = crop(strip, w['strip_box'], 60)
        img = (img * 0.55 + 110).astype(np.uint8)
        for k, p in enumerate(w['pieces']):
            ys, xs = np.nonzero(lab == p)
            col = COLS[k % len(COLS)]
            img[ys - oy, xs - ox] = col
            cv2.putText(img, str(p), (int(xs.mean()) - ox - 10, int(ys.min()) - oy - 4), 0, 0.7, col, 2)
        s = 2 if img.shape[1] < 600 else 1
        cv2.imwrite(wdir(id, f'pieces_{c}.png'), cv2.resize(img, None, fx=s, fy=s))
        print(c, w['pieces'])
