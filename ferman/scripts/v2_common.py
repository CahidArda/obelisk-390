"""Shared helpers for the v2 reading pipeline (word-level reading, boxes built from words).

Paths are relative to the repository; run the scripts from anywhere.
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FERMAN = os.path.dirname(HERE)
DATA = os.path.join(FERMAN, 'data.js')
READING = os.path.join(HERE, 'reading.json')
WORK = os.path.join(FERMAN, 'work')
REPLICA = os.path.join(WORK, 'replica.jpg')
LINES = ['nisan', 'l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7']
SINGLE = ['davet', 'tugra', 'place']
HEADER = '// Generated from the stitched replica (regions) and the reading (entries, groups).'


def load_data():
    s = open(DATA, encoding='utf-8').read()
    body = s[s.index('window.FERMAN = ') + len('window.FERMAN = '):].rstrip()
    return json.loads(body.rstrip(';'))


def save_data(d):
    with open(DATA, 'w', encoding='utf-8') as f:
        f.write(HEADER + '\n')
        f.write('window.FERMAN = ' + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + ';\n')


def entry(d, id):
    return next(e for e in d['entries'] if e['id'] == id)


def ink_of(d, id):
    return entry(d, id)['ink']


_replica = None


def replica():
    """The 8000 x 17131 replica as a BGR array (cached)."""
    global _replica
    if _replica is None:
        import cv2
        npy = os.path.join(WORK, 'replica.npy')
        if os.path.exists(npy):
            _replica = np.load(npy, mmap_mode='r')
        else:
            _replica = cv2.imread(REPLICA)
            np.save(npy, _replica)
    return _replica


def wdir(id, *p):
    path = os.path.join(WORK, id, *p)
    os.makedirs(os.path.dirname(path) if p else path, exist_ok=True)
    return path


def jload(path):
    return json.load(open(path, encoding='utf-8'))


def jsave(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
