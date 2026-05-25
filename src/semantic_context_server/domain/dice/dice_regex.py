import re


class DiceRegex:
    _pattern = re.compile(
        r"^(?P<num>\d+)d(?P<sides>\d+)"
        r"(?P<explode>!)?"
        r"(?:(?P<keep>kh\d+)|(?P<drop>dl\d+))?"
        r"(?P<reroll>r[<>]=?\d+)?$"
    )

    @classmethod
    def match(cls, expression: str) -> re.Match[str] | None:
        return cls._pattern.match(expression)
