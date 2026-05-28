from __future__ import annotations

import signal


def setup_signal_handlers() -> None:
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_IGN)
