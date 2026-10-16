class Dispatcher:
    def __init__(self):
        self.stopping = False
        self.pending = 0
        self.released = False

    def begin(self):
        if self.stopping:
            raise RuntimeError('closed')
        self.pending += 1

    def stop(self):
        self.stopping = True
        self._refresh_release()

    def finish(self):
        if not self.pending:
            raise RuntimeError('empty')
        self.pending -= 1
        self._refresh_release()

    def _refresh_release(self):
        self.released = self.stopping and self.pending == 0
