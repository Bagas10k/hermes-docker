"""In-memory integer R-tree index for half-open merged-cell rectangles."""
import sqlite3


class SpanIndex:
    def __init__(self, rows, cols):
        if any(type(n) is not int or not 0 < n < 2**31 for n in (rows, cols)):
            raise ValueError('Dimensions must be positive signed-32-bit integers')
        self.rows, self.cols = rows, cols
        self.db = sqlite3.connect(':memory:')
        self.db.execute('CREATE VIRTUAL TABLE spans USING rtree_i32(id,r0,r1,c0,c1)')

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.db.close()

    def _validate(self, r0, c0, r1, c1):
        if any(type(n) is not int for n in (r0,c0,r1,c1)):
            raise ValueError('Coordinates must be integers, not bools')
        if not (0 <= r0 <= r1 <= self.rows and 0 <= c0 <= c1 <= self.cols):
            raise ValueError('Rectangle out of bounds or reversed')

    def add(self, ident, r0, c0, r1, c1):
        self._validate(r0,c0,r1,c1)
        if type(ident) is not int or not 0 <= ident < 2**63:
            raise ValueError('ID must be a nonnegative signed-64-bit integer')
        if r0 == r1 or c0 == c1:
            raise ValueError('Empty merged cell')
        with self.db:
            if self.db.execute('SELECT 1 FROM spans WHERE id=?',(ident,)).fetchone():
                raise ValueError('Duplicate ID')
            if self.query(r0,c0,r1,c1):
                raise ValueError('Overlapping merge')
            self.db.execute('INSERT INTO spans VALUES (?,?,?,?,?)', (ident,r0,r1,c0,c1))

    def query(self, r0, c0, r1, c1):
        self._validate(r0,c0,r1,c1)
        if r0 == r1 or c0 == c1:
            return []
        hits = self.db.execute(
            'SELECT id,r0,c0,r1,c1 FROM spans WHERE r0 < ? AND r1 > ? '
            'AND c0 < ? AND c1 > ? ORDER BY id', (r1,r0,c1,c0)).fetchall()
        return [{'id': i, 'anchor': [a,b], 'bounds': [a,b,c,d],
                 'clip': [max(a,r0),max(b,c0),min(c,r1),min(d,c1)]}
                for i,a,b,c,d in hits]
