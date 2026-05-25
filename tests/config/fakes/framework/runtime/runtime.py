from .lock import DummyLock


class DummyRuntime:
    def __init__(self, *, cooldown=True, locked=False, warn=True):
        self.cooldown = cooldown
        self._locked = locked
        self._warn = warn

    def should_warn(self, *args):
        return self._warn

    def check_cooldown(self, *args):
        return self.cooldown

    def get_lock(self, *args):
        return DummyLock(self._locked)
