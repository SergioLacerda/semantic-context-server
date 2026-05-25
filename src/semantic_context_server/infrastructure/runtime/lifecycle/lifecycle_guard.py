class LifecycleGuard:
    """Tracks container lifecycle state to detect unclean shutdowns in tests."""

    def __init__(self) -> None:
        self._violations: list[str] = []

    def record_violation(self, message: str) -> None:
        self._violations.append(message)

    def assert_clean(self) -> None:
        if self._violations:
            raise AssertionError(
                "LifecycleGuard detected unclean state:\n" + "\n".join(self._violations)
            )
