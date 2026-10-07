"""Async clipboard feedback oracle; not OS clipboard or a DOM bridge."""


class ClipboardFeedback:
    def __init__(self, schedule, cancel):
        self.schedule, self.cancel = schedule, cancel
        self.disposed = False
        self.request = self.timer = None
        self.label = 'Salin Rute'

    def invalidate(self):
        self.request = None
        if self.timer is not None:
            self.cancel(self.timer)
        self.timer = None

    def rerender(self):
        self.invalidate()
        self.label = 'Salin Rute'

    def dispose(self):
        if self.disposed:
            return False
        self.disposed = True
        self.rerender()
        return True

    async def copy(self, text, write=None, fallback=None):
        if self.disposed:
            return {'text': text, 'success': False}
        self.invalidate()
        request = self.request = object()
        self.label = 'Menyalin…'
        success = False
        try:
            if write is not None:
                await write(text)
                success = True
            elif fallback is not None:
                success = fallback(text) is True
        except Exception:
            success = False
        if not self.disposed and self.request is request:
            self.label = 'Tersalin!' if success else 'Gagal menyalin'

            def reset():
                if not self.disposed and self.request is request:
                    self.timer = self.request = None
                    self.label = 'Salin Rute'

            self.timer = self.schedule(reset, 1500)
        return {'text': text, 'success': success}
