"""Synchronous minimap-only lifecycle helper/oracle; not a DOM implementation.

Wrap observer/listener work with run, and supply owned-resource cleanup once.
Other preview work stays outside this gate. No remount or thread-safety contract.
"""


class MinimapLifecycle:
    def __init__(self, cleanup):
        self.disposed = False
        self._cleanup = cleanup

    def run(self, callback, *args):
        if self.disposed:
            return False
        callback(*args)
        return True

    def dispose(self):
        if self.disposed:
            return False
        self.disposed = True  # Close admission before cleanup/reentrant callbacks.
        cleanup, self._cleanup = self._cleanup, None
        cleanup()
        return True
