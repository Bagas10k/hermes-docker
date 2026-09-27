"""Offline native-resolution RGB delta reference; no action authorization."""
import math
import numpy as np

class Detector:
    def __init__(self, tile=32, threshold=12, max_age_ms=100):
        if type(tile) is not int or tile < 1:
            raise ValueError('tile must be positive integer')
        if type(threshold) is not int or not 0 <= threshold <= 255:
            raise ValueError('threshold must be integer in 0..255')
        if not math.isfinite(max_age_ms) or max_age_ms <= 0:
            raise ValueError('invalid age bound')
        self.tile, self.threshold, self.max_age = tile, threshold, max_age_ms
        self.prev = None
        self.seq = -1

    def observe(self, image, sequence, capture_ms, now_ms):
        if not isinstance(image, np.ndarray) or image.dtype != np.uint8:
            raise ValueError('expected uint8 RGB array')
        if image.ndim != 3 or image.shape[2] != 3 or min(image.shape[:2]) < 1:
            raise ValueError('expected nonempty HWC RGB')
        if type(sequence) is not int or sequence < 0:
            raise ValueError('invalid sequence')
        if not all(math.isfinite(v) for v in (capture_ms, now_ms)):
            raise ValueError('invalid clock')
        age = now_ms - capture_ms
        if age < 0 or age > self.max_age or sequence <= self.seq:
            return {'state': 'stale', 'regions': []}
        if self.prev is None or self.prev.shape != image.shape:
            self.prev, self.seq = image.copy(), sequence
            return {'state': 'baseline', 'regions': []}
        mask = np.max(np.abs(image.astype(np.int16) - self.prev.astype(np.int16)), axis=2) > self.threshold
        ys, xs = np.nonzero(mask)
        tiles = sorted(set(zip((ys // self.tile).tolist(), (xs // self.tile).tolist())))
        h, w = image.shape[:2]
        regions = [(x*self.tile, y*self.tile, min(w,(x+1)*self.tile), min(h,(y+1)*self.tile)) for y,x in tiles]
        self.prev, self.seq = image.copy(), sequence
        return {'state': 'changed' if regions else 'unchanged', 'regions': regions}
