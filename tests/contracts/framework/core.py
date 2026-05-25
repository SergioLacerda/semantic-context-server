class ValidationError(Exception):
    pass


class ValidationResult:
    def __init__(self):
        self.errors: list[str] = []

    def add(self, message: str):
        self.errors.append(message)

    def is_valid(self) -> bool:
        return not self.errors

    def raise_if_invalid(self):
        if not self.is_valid():
            raise AssertionError("\n\n".join(self.errors))


class ArchitectureValidator:
    """
    Engine principal do framework.
    """

    def __init__(self):
        self._rules = []

    def register(self, rule):
        self._rules.append(rule)
        return self

    def validate(self, context):
        result = ValidationResult()

        for rule in self._rules:
            try:
                rule.validate(context)
            except Exception as e:
                result.add(rule.format_error(e))

        result.raise_if_invalid()
