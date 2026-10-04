"""Latest-issued request admission for one grid, not server revisions."""
MAX_REVISION = 2**53 - 1


class RevisionGate:
    def __init__(self):
        self.issued = 0
        self.applied = 0

    def begin(self):
        if self.issued >= MAX_REVISION:
            raise OverflowError('Revision exhausted; create a new grid instance')
        self.issued += 1
        return self.issued

    def apply(self, revision, payload, commit):
        if type(revision) is not int or not 0 < revision <= MAX_REVISION:
            raise ValueError('Expected a positive JS-safe integer')
        if revision != self.issued or revision <= self.applied:
            return False
        commit(payload)  # synchronous; must not reenter this gate
        self.applied = revision
        return True
